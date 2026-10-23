#!/usr/bin/env bash
# See the demo move without a Vapi account or a phone call.
#
#   mkdir -p demo/public
#   cp assets/server-skeleton.mjs  demo/server.mjs
#   cp assets/demo-dashboard.html  demo/public/index.html
#   (cd demo && node server.mjs) &
#   open http://localhost:7788
#   bash scripts/try-it.sh http://localhost:7788
#
# Replays a scripted call as the same webhook bodies Vapi sends, paced like a
# real conversation. Also exactly how to test YOUR generated demo before any
# call is placed: synthetic probes exercise every panel with zero telephony.

set -euo pipefail
URL="${1:-http://localhost:7788}/vapi"
CALL="try-it-$RANDOM"

probe() {
  curl -s -o /dev/null -X POST "$URL" -H 'content-type: application/json' -d "$1"
  sleep "${2:-1}"
}

echo "replaying a scripted call to $URL (call id $CALL)"

probe '{"message":{"type":"status-update","status":"ringing","call":{"id":"'$CALL'"}}}' 1
probe '{"message":{"type":"status-update","status":"in-progress","call":{"id":"'$CALL'"}}}' 1
probe '{"message":{"type":"transcript","transcriptType":"final","role":"assistant","transcript":"Hey there! I can get you set up in under a minute. Ready to give it a try?","call":{"id":"'$CALL'"}}}' 2
probe '{"message":{"type":"transcript","transcriptType":"partial","role":"user","transcript":"Yes,","call":{"id":"'$CALL'"}}}' 0.4
probe '{"message":{"type":"transcript","transcriptType":"partial","role":"user","transcript":"Yes, let us do it.","call":{"id":"'$CALL'"}}}' 0.4
probe '{"message":{"type":"transcript","transcriptType":"final","role":"user","transcript":"Yes, let us do it.","call":{"id":"'$CALL'"}}}' 1.5
probe '{"message":{"type":"transcript","transcriptType":"final","role":"assistant","transcript":"Great. Give me one moment while I pull up a quote.","call":{"id":"'$CALL'"}}}' 1
probe '{"message":{"type":"conversation-update","call":{"id":"'$CALL'"},"messages":[{"role":"bot","toolCalls":[{"id":"tc-1","function":{"name":"get_quote","arguments":"{\"item\":\"the usual\"}"}}]}]}}' 1.5
probe '{"message":{"type":"conversation-update","call":{"id":"'$CALL'"},"messages":[{"role":"bot","toolCalls":[{"id":"tc-1","function":{"name":"get_quote","arguments":"{\"item\":\"the usual\"}"}}]},{"role":"tool_call_result","name":"get_quote","result":"Quote ready: twenty dollars and forty-four cents."}]}}' 1
probe '{"message":{"type":"transcript","transcriptType":"final","role":"assistant","transcript":"The estimated price is twenty dollars and forty-four cents. Want me to book it?","call":{"id":"'$CALL'"}}}' 2
probe '{"message":{"type":"transcript","transcriptType":"final","role":"user","transcript":"Yes, please book it.","call":{"id":"'$CALL'"}}}' 1.5
probe '{"message":{"type":"conversation-update","call":{"id":"'$CALL'"},"messages":[{"role":"bot","toolCalls":[{"id":"tc-2","function":{"name":"book_it","arguments":"{\"confirmed\":true}"}}]},{"role":"tool_call_result","name":"book_it","result":"Booked. Reference AB-1234."}]}}' 1.5
probe '{"message":{"type":"transcript","transcriptType":"final","role":"assistant","transcript":"You are booked, reference A B twelve thirty-four. Anything else?","call":{"id":"'$CALL'"}}}' 2
probe '{"message":{"type":"transcript","transcriptType":"final","role":"user","transcript":"No thanks, that is everything.","call":{"id":"'$CALL'"}}}' 1.5
probe '{"message":{"type":"status-update","status":"ended","endedReason":"customer-ended-call","call":{"id":"'$CALL'"}}}' 1
probe '{"message":{"type":"end-of-call-report","endedReason":"customer-ended-call","call":{"id":"'$CALL'"},"artifact":{"structuredOutputs":{"demo-so-id":{"name":"booking_made","result":true}}}}}' 0

echo "done — the board should show the whole call, ending with the report"
