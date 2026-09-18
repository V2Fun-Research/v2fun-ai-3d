# V2Fun API integration notes

## Sources and refresh policy

Fetched and checked official [image](https://doc.v2fun.art/zh/api/reference/images), [3D](https://doc.v2fun.art/zh/api/reference/3d-models), and [balance](https://doc.v2fun.art/zh/api/reference/balance) documentation on **2026-09-18**. This is the local verification date, not an upstream version.

Read this local reference for routine use. When the user requests a refresh, integration changes, unrecorded parameters, or another stage, fetch the relevant official pages, compare request/response schemas, and update these notes and the verification date. If retrieval fails, retain the previous record and report that freshness could not be confirmed; never advance the date alone. This file does not automatically synchronize with the website.

## Verified interfaces

Base URL: `https://api.v2fun.art/api/v1`; JSON requests with Bearer authentication. Set `options.block=false` for asynchronous execution. Creation may return 200 or 201; persist `task_uuid` and query the matching GET endpoint. States: QUEUED/PROCESSING/COMPLETED/FAILED. Image generation/editing and mesh results are asset URI arrays, not OpenAI synchronous image responses. Optional `options.priority` is 0–255 and must not exceed the client's `mq_priority`; normally omit it.

| Stage | Create / query | Request fields |
| --- | --- | --- |
| Image edit | POST /images/edits; GET /images/edits/{task_uuid} | model, prompt, input_images, size, background, options |
| Mesh | POST /3d_models/meshes; GET /3d_models/meshes/{task_uuid} | One of three input schemas; model, with_texture, pbr_texture, hd_texture, options |
| Balance | GET /balance | Numeric balance: total credits minus credits reserved for in-progress tasks; not total credits or final billing |

### Image editing

- Listed models: `qwen-image-edit` (API default), `nano-banana-pro`, `nano-banana-2`, `nano-banana-2-lite`, `gpt-image-2`, `gpt-image-2.5-sunburst`, `gpt-image-2.5-flare`, `gpt-multiview`. This skill still explicitly uses `gpt-image-2`; documentation updates do not authorize model changes.
- `input_images` is optional/nullable in the schema; an array contains 1–3 inputs. This reference-editing workflow still supplies images with the original as primary. Each accepts a relative asset URI, base64 payload including data URLs, or HTTP/HTTPS URL. `prompt` is optional/nullable.
- Sizes: 1024x1024, 1152x864, 864x1152, 1280x720, 720x1280. `background`: opaque or transparent. No `quality` or `n` field is listed. Do not infer model-specific capabilities from the model list.

### Mesh generation

- Choose one input schema: text `prompt`; single image `input_image`; or multiview `input_images` object with required `front` and optional/nullable `left`, `back`, `right`. Do not add the text schema's prompt to single-image requests.
- Image values accept relative asset URIs, base64 including data URLs, or HTTP/HTTPS URLs. Multiview inputs must show the same object as separate views; a triptych is not this object schema.
- `model`: `pro` (API default) or `flash`. API defaults for `with_texture`, `pbr_texture`, `hd_texture` are all false; this skill explicitly sets all three true and keeps pro.
- `metadata` is a nullable array of model metadata, potentially including reference_images, preview_image, t_pose_model, mesh_info, preview_video, downloads. Optional outputs are not guaranteed.

Store prompts/images in references/, image task records in api-jobs/part-images/, mesh records in api-jobs/<part-id>.json, and downloaded models in source-models/<part-id>.glb. The official schema describes downloads as temporary descriptors with any-typed entries. The existing executor expects asset_path matching a result URI and a download_url; these descriptor keys are a client expectation, not strictly specified by this page. Report missing descriptors and query the original task rather than guessing URLs or regenerating. Never send the API key to signed asset URLs. Refresh expired links by querying the original task, not by generating again.

## API support versus implemented commands

The runtime implements single-image meshes, balance, status, and downloads. Text-to-3D, multiview meshes, image editing, and other stages have no generic submit command. The API also lists textures, remeshings, conversions, and renderings under /3d_models/; this does not make them implemented locally. Before adding a stage, check its full schema and integrate the same recovery and budget protocol.

## Reliable execution

- Read keys only from current environment or selected local configuration. Do not write keys into skill files, prompts, logs, or deliverables. Persist keys only if requested, with restricted permissions.
- Save SUBMITTING and input hashes before POST; persist the returned ID immediately. Distinguish proven not-sent, proven rejected-without-creation, and uncertain outcomes. Only the first two allow a repaired submission under existing authorization. Preserve failure evidence. Missing IDs or HTTP errors alone do not prove that nothing was created.
- Use one poller per task. Normal queries are at least 15 seconds apart; after 429/5xx, wait at least 120 seconds before the next query. Stop at terminal states. Poll inside the executor, not through repeated assistant tool calls.
- When account limits are unknown, allow at most two unfinished tasks across image, mesh, retopology, and texture stages; stricter account limits prevail. Count queued/running tasks. The bundled executor does not enforce this across projects.
- Record finite whole-task and stage ceilings under current user authorization, including reference preparation and corrections. Queries/downloads do not count as new tasks. Resume known IDs without requiring a new-submission budget record. Actual charges come from the account balance/billing.
- Local construction may proceed concurrently. One coordinator updates shared manifests; each task owns its own record. Failures pause only dependent work.
