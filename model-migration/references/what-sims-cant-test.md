# What simulations don't show

Chat simulations are where model behavior is compared, but they leave out everything about audio and timing, and tools are mocked. Check these separately before rollout.

| Behavior | Why chat simulations miss it | Check it with |
|---|---|---|
| Turn latency and cost per minute | Chat has no audio path | Voice simulations on a few core scenarios; read cost and timing from each call (`GET /call/{id}`) |
| Interruptions and barge-in | Chat turns never overlap | Voice simulations with an interrupting personality, and a few manual calls |
| Silence and silence timeouts | Chat has no silence timer, so silence scenarios can't finish | Voice simulations or manual calls |
| Hooks that react to speech or timing | They depend on audio events | Voice simulations or manual calls |
| Speech recognition of names, numbers and accents | Chat sends exact text | Voice simulations with a matching voice; don't rely on them alone for digit accuracy |
| How the voice reads the reply (markdown, symbols, numbers) | Chat shows text, not speech | Listen to voice simulation recordings |
| Real transfers, warm-transfer summaries | Transfers are mocked; a mocked transfer doesn't end the conversation | Test calls to a number you own |
| Real tool behavior, latency and errors | Every tool is mocked with one fixed answer per scenario | A staging version of the tools, or production monitoring during rollout |
| Answers that change on a second call to the same tool | A mock returns the same answer every time in a scenario | Separate scenarios for each state |
| Real caller satisfaction | Only proxies can be graded | Survey scores and complaints during rollout |

Verify each row on your own setup; simulation capabilities change. When in doubt, test the behavior in a few manual voice calls before rollout.
