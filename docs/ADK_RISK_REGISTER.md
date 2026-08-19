# ADK risk register

V1 avoids experimental or unnecessary security paths. We do not use A2A, MCP, ADK human confirmation as the authorization boundary, arbitrary code execution, or parallel side-effecting tools.

Gemini function calls and structured output are treated as untrusted proposals. The server validates and authorizes independently. Any Gemini outage leaves deterministic authorization intact.

ADK dependencies are pinned to a compatible range and CI recompiles/tests on every push and pull request.
