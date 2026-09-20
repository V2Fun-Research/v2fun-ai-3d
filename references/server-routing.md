# CN and global server routing

Run from this installed skill directory. No sibling setup installation is needed.

```sh
python3 scripts/v2fun.py region --project /path/to/project
python3 scripts/v2fun.py region --project /path/to/project --region global
```

Provide V2FUN_API_KEY in the execution environment or api_key in explicitly selected private JSON configuration. Accept a raw key, Bearer <key>, or Authorization: Bearer <key>; placeholders are rejected. Never ask users to paste secrets into chat. Region can be auto (default), cn, or global through V2FUN_REGION, --region on region/balance commands, or project configuration. Conflicting explicit settings fail rather than silently winning. Legacy official base_url settings select that server; custom hosts are rejected.

| Region | API base | Documentation |
| --- | --- | --- |
| cn | https://api.v2fun.art/api/v1 | https://doc.v2fun.art |
| global | https://api.v2fun.ai/api/v1 | https://doc.v2fun.ai |

No documented key-prefix rule exists. Do not infer the region from language, IP or geography. For a new unconfigured credential, the client sends only GET /balance to the two official API hosts. Bind only when exactly one returns a finite numeric balance and the other returns 401. Two successes require an explicit choice. Two 401 responses mean credentials were not accepted. 403, timeout, 429, 5xx, malformed responses and redirects are inconclusive; do not infer invalid credentials or select the other server. Explicit region selection validates only that server. These checks never upload media or create paid tasks. Balance zero is a valid response.

The client stores routing and a one-way credential fingerprint in project .v2fun/server.json with private permissions, never the raw key. Matching credentials reuse the binding and validate only that server; changed credentials require fresh detection unless a server is explicitly configured. A cached binding conflicting with explicit configuration fails. To intentionally change a project server, preserve old tasks and use a new project, or review/remove only its server cache after reconciling existing work. Do not automatically rewrite user configuration or change active tasks.

All paid plans and task records must carry a server object with region, base_url, docs_base_url and credential_fingerprint from Client.binding(). Keep these records private. Quote prices from the selected docs host; include the binding in the approved quote hash. Creation, polling, retargeting and recovery use that same binding. A changed key or conflicting server fails before submission. Do not automatically fail over, retry a POST, or send another server's asset URI. Renewed credentials require explicit account verification before updating a historical binding. Fetch signed downloads exactly as returned without API Authorization headers or domain replacement. Authenticated HTTP redirects are disabled.

Legacy tasks with no binding are deliberately blocked before remote recovery. Determine the original server from the original configuration/request evidence; verify the credential against that server, then explicitly migrate the private record with Client.binding(). Preserve task IDs, original authorization, inputs, budgets and plan hashes; when changing a quote hash, reconcile its associated task records together. Never guess cn merely because it used to be the default. Unsubmitted old quotes can be regenerated normally. There is no automatic migration command.

The region command verifies routing and available balance, not generation permissions, current service capabilities, actual billing, or authorization to spend. Missing credentials do not block offline scaffolding, doctor, status or procedural work.

Verified documentation: [CN quickstart](https://doc.v2fun.art/zh/quickstart), [global quickstart](https://doc.v2fun.ai/zh/quickstart), [global authentication](https://doc.v2fun.ai/zh/authentication), [global balance](https://doc.v2fun.ai/zh/api/reference/balance). Server maps are explicit; service-specific schema and current pricing must still be checked before a new paid call.
