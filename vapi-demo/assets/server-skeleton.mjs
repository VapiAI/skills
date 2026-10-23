// Vapi demo server skeleton — plain Node, no dependencies.
//
// Serves the dashboard, receives Vapi webhooks, and rebroadcasts them to the
// page over SSE. This is the OBSERVER wiring: it watches an existing agent
// without owning its tools. Every optional block is marked OPTIONAL and safe
// to delete.
//
// Env: PORT (Railway sets it), and for the optional blocks:
//   ASSISTANT_ID                       assistant-request answer / webcall target
//   VAPI_ORG_ID, VAPI_PRIVATE_KEY      webcall token minting only
//   PUBLIC_ORIGIN                      webcall origin restriction

import { createServer } from 'node:http';
import { createHmac } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';

const PORT = Number(process.env.PORT ?? 7788);
const PUBLIC_DIR = new URL('./public', import.meta.url).pathname;

// ---- SSE with replay ------------------------------------------------------
// A ring buffer of recent events plus a per-boot token in every event id. A
// reconnecting page sends Last-Event-ID; if the id is from this boot and still
// in the buffer, replay resumes seamlessly. Otherwise send a `reset` frame so
// the page clears rather than rendering stale state on top of live state.
const BOOT = Math.random().toString(36).slice(2, 8);
const BUFFER_MAX = 200;
const buffer = [];
let nextId = 1;
let lastEvictedId = 0;
const clients = new Set();

function frameBuild(event) {
  return `id: ${BOOT}-${event.id}\ndata: ${JSON.stringify({ type: event.type, data: event.data })}\n\n`;
}

export function emitEvent(type, data, { replayable = true } = {}) {
  const event = { id: nextId++, type, data };
  if (replayable) {
    buffer.push(event);
    if (buffer.length > BUFFER_MAX) lastEvictedId = buffer.shift().id;
  }
  const payload = frameBuild(event);
  for (const res of clients) res.write(payload);
}

function sseHandler(req, res) {
  res.writeHead(200, {
    'content-type': 'text/event-stream',
    'cache-control': 'no-cache',
    connection: 'keep-alive',
    // nginx-family proxies buffer streaming responses unless told not to.
    'x-accel-buffering': 'no',
  });
  // ~2KB of comment padding defeats proxies that hold a response until N
  // bytes have accumulated (verified live: a cloudflared quick tunnel
  // delivered ZERO SSE bytes without this while localhost streamed fine).
  res.write(':' + ' '.repeat(2048) + '\n');
  res.write('retry: 3000\n\n');
  const last = req.headers['last-event-id'] ?? '';
  const [bootSeen, idRaw] = String(last).split('-');
  const lastId = Number(idRaw);
  const resumable = bootSeen === BOOT && Number.isFinite(lastId) && lastId >= lastEvictedId;
  if (resumable) {
    // Reconnect within this boot: send only what the client missed.
    for (const event of buffer) if (event.id > lastId) res.write(frameBuild(event));
  } else {
    // Fresh page, or a reconnect we can't resume (server rebooted, or the
    // buffer evicted past their position). Tell an old client to clear, then
    // replay the buffer so a page opened mid-call still shows the call so far.
    if (last) res.write(`data: ${JSON.stringify({ type: 'reset', data: {} })}\n\n`);
    for (const event of buffer) res.write(frameBuild(event));
  }
  clients.add(res);
  req.on('close', () => clients.delete(res));
}

// Heartbeat comment so idle connections are neither reaped by proxies nor
// left buffered. Comments are invisible to EventSource.
setInterval(() => { for (const res of clients) res.write(':hb\n\n'); }, 15000);

// ---- Webhook ingest -------------------------------------------------------
// Attach via the assistant: serverMessages [status-update, transcript,
// conversation-update, end-of-call-report] and server.url → this /vapi.
//
// Tool observation happens through conversation-update, NOT tool-calls: the
// messages array carries every tool_calls / tool_call_result turn regardless
// of whose server executes the tool. Emitting from here means the demo never
// competes with the agent's real tool server.
// Real conversation-update payloads, verified live 2026-08-18:
//   - tool CALLS arrive as messages[].toolCalls[] with stable ids across updates
//   - tool RESULTS arrive as role "tool_call_result" with name+result and NO id
//   - every update resends the FULL history, so everything repeats every time
// So: dedup calls by id, and match results POSITIONALLY per (call, tool name) —
// the nth result for a name pairs with the nth call of that name. Stable across
// full-history replays. Honest limit: with parallel same-name calls the
// observer cannot prove which result belongs to which call; Vapi sends no id.
const callToolState = new Map(); // callId -> { ids:Set, calls:{name:[{id,at}]}, resultsEmitted:{name:count} }

function toolStateFor(callId) {
  if (!callToolState.has(callId)) callToolState.set(callId, { ids: new Set(), calls: {}, resultsEmitted: {} });
  return callToolState.get(callId);
}

function toolTurnsEmit(callId, messages) {
  const st = toolStateFor(callId);
  const resultsSeen = {}; // per-name occurrence counter within THIS update
  for (const m of messages ?? []) {
    for (const tc of m.toolCalls ?? m.tool_calls ?? []) {
      if (!tc?.id || st.ids.has(tc.id)) continue;
      st.ids.add(tc.id);
      const name = tc.function?.name ?? tc.name ?? '?';
      let args = tc.function?.arguments ?? {};
      if (typeof args === 'string') { try { args = JSON.parse(args || '{}'); } catch { args = {}; } }
      (st.calls[name] ??= []).push({ id: tc.id, at: Date.now() });
      emitEvent('tool.called', { callId, toolCallId: tc.id, name, args });
    }
    if (m.role === 'tool_call_result') {
      const name = m.name ?? '?';
      const n = (resultsSeen[name] = (resultsSeen[name] ?? 0) + 1) - 1;
      if (n < (st.resultsEmitted[name] ?? 0)) continue; // already emitted in an earlier update
      st.resultsEmitted[name] = n + 1;
      const paired = (st.calls[name] ?? [])[n];
      emitEvent('tool.completed', {
        callId,
        toolCallId: paired?.id ?? null,
        name,
        result: m.result ?? '',
        // Observed latency (call seen -> result seen), not true execution time.
        ms: paired ? Date.now() - paired.at : 0,
      });
    }
  }
}

async function vapiHandler(req, res) {
  let body = '';
  for await (const chunk of req) body += chunk;
  let message;
  try { message = JSON.parse(body || '{}').message; } catch { message = undefined; }
  const callId = message?.call?.id ?? 'unknown-call';
  // One line per webhook, so "did Vapi reach me at all?" is never a mystery.
  console.log(`[vapi] ${message?.type ?? '??'} call=${callId}`);
  // Raw bodies on demand: DEBUG_BODIES=1 dumps each webhook to stdout. The
  // fastest way to learn a payload's real shape when a panel stays empty.
  if (process.env.DEBUG_BODIES) console.log(body.slice(0, 4000));

  switch (message?.type) {
    // OPTIONAL — assistant-request. Only fires when the phone number carries
    // NO assistantId and its server.url points here. Delete the case (and
    // re-attach the assistant to the number) if the demo doesn't showcase it.
    // 🔴 Answer within 7.5s END TO END or the call dies before it is answered
    //    ("Couldn't get assistant"). That ceiling is the telephony provider's,
    //    not server.timeoutSeconds.
    // 🔴 If you send assistantOverrides.model it MUST carry provider + model
    //    (discriminated union) — a bare {messages} override kills the call.
    // If the dashboard animates this stage, hold the response to a DEADLINE
    // (target total elapsed), never an unconditional sleep.
    case 'assistant-request': {
      const startedAt = Date.now();
      const from = message.customer?.number;
      emitEvent('caller.resolved', { callId, number: from ?? null });
      const HOLD_MS = 0; // raise (≤3500) only if the page animates the resolution
      const wait = Math.max(0, HOLD_MS - (Date.now() - startedAt));
      if (wait) await new Promise((r) => setTimeout(r, wait));
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ assistantId: process.env.ASSISTANT_ID }));
      return;
    }
    case 'status-update':
      emitEvent('call.status', { callId, status: message.status ?? '?', endedReason: message.endedReason });
      break;
    case 'transcript':
      // Partials are live-only: hundreds per call would flush the replay ring.
      emitEvent('transcript', {
        callId,
        role: message.role ?? 'unknown',
        text: message.transcript ?? '',
        final: message.transcriptType === 'final',
      }, { replayable: message.transcriptType === 'final' });
      break;
    case 'conversation-update':
      toolTurnsEmit(callId, message.messages);
      // The SAME payload carries the platform's own merged turn history, which
      // is the authoritative text: revised partials and re-cut finals have
      // already been folded into one message per turn, with the speaking member
      // named. The live transcript stream is what the room watches, but it
      // fragments whenever speech-to-text revises a word mid-utterance, so this
      // is what the page corrects itself from at every turn boundary.
      emitEvent('transcript.history', {
        callId,
        turns: (message.messages ?? [])
          .filter((m) => (m.role === 'bot' || m.role === 'user') && typeof m.message === 'string' && m.message.trim())
          .map((m) => ({ role: m.role === 'bot' ? 'assistant' : 'user', name: m.assistantName ?? null, text: m.message })),
      });
      break;
    case 'end-of-call-report':
      emitEvent('call.report', {
        callId,
        endedReason: message.endedReason,
        structuredOutputs: message.artifact?.structuredOutputs ?? null,
      });
      break;
  }
  res.writeHead(200, { 'content-type': 'application/json' });
  res.end('{}');
}

// ---- OPTIONAL: web-call button auth ----------------------------------------
// The browser never sees the org private key. It fetches a short-lived JWT;
// the key doubles as the HS256 secret (verified live). The token is
// public-scoped — the ONLY endpoint it can reach is POST /call/web — and the
// restrictions are enforced by Vapi server-side (403 on any other assistant).
const b64url = (input) => Buffer.from(input).toString('base64url');

function webcallTokenMint({ orgId, privateKey, assistantId, origin, ttlSeconds = 3600 }) {
  const now = Math.floor(Date.now() / 1000);
  const header = b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = b64url(JSON.stringify({
    orgId,
    token: {
      tag: 'public',
      restrictions: {
        enabled: true,
        allowedAssistantIds: [assistantId],
        allowedOrigins: [origin],
        allowTransientAssistant: false,
      },
    },
    iat: now,
    exp: now + ttlSeconds,
  }));
  const signature = createHmac('sha256', privateKey).update(`${header}.${payload}`).digest('base64url');
  return `${header}.${payload}.${signature}`;
}

function webcallTokenHandler(res) {
  const { VAPI_ORG_ID, VAPI_PRIVATE_KEY, ASSISTANT_ID, PUBLIC_ORIGIN } = process.env;
  if (!VAPI_ORG_ID || !VAPI_PRIVATE_KEY || !ASSISTANT_ID || !PUBLIC_ORIGIN) {
    res.writeHead(503, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ error: 'Web calling is not configured on this server' }));
    return;
  }
  const token = webcallTokenMint({
    orgId: VAPI_ORG_ID, privateKey: VAPI_PRIVATE_KEY,
    assistantId: ASSISTANT_ID, origin: PUBLIC_ORIGIN,
  });
  res.writeHead(200, { 'content-type': 'application/json' });
  res.end(JSON.stringify({ token, assistantId: ASSISTANT_ID }));
}

// ---- Static + routing -------------------------------------------------------
const MIME = { '.html': 'text/html', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.otf': 'font/otf', '.js': 'text/javascript', '.css': 'text/css' };

async function staticHandler(req, res) {
  const path = normalize(req.url === '/' ? '/index.html' : req.url).replace(/^(\.\.[/\\])+/, '');
  try {
    const file = await readFile(join(PUBLIC_DIR, path));
    res.writeHead(200, { 'content-type': MIME[extname(path)] ?? 'application/octet-stream' });
    res.end(file);
  } catch {
    res.writeHead(404); res.end('not found');
  }
}

createServer(async (req, res) => {
  if (req.url === '/health') { res.writeHead(200, { 'content-type': 'application/json' }); res.end('{"ok":true}'); return; }
  if (req.url === '/events/stream') return sseHandler(req, res);
  if (req.method === 'POST' && req.url === '/vapi') return vapiHandler(req, res);
  if (req.method === 'GET' && req.url === '/webcall-token') return webcallTokenHandler(res);
  return staticHandler(req, res);
}).listen(PORT, () => console.log(`demo server on :${PORT}`));
