---
name: v2fun-ai-3d
license: MIT
description: "AI 3D modeling from reference images using AI-generated meshes, procedural Three.js geometry, or hybrid modeling. Use for image-to-3D reconstruction, part planning, assembly, GLB/source delivery, and local task-status queries. Includes a standalone runtime; not for exact CAD or certified print preparation."
---

# V2Fun AI 3D

Before the first image generation, 3D generation, or procedural build, explain the concrete modeling strategy in the conversation: parts, methods, API calls, and execution order. Follow [Routes and parts](references/modeling-routes.md). For single-view input, follow [AI generation](references/ai-generation.md). Assemble, inspect, and export in Three.js.

## Scope and required inputs

Use this skill for reference-based visual mesh reconstruction, part construction, assembly, GLB/source delivery, and task-status queries. Do not use it for image-only stylization, ordinary video editing, website publishing, slicer preparation, certified printable parts, or exact CAD/STEP delivery. An image-only request does not authorize mesh generation.

For new modeling, obtain accessible reference images or reusable model files and the intended subject/scope. Use a static visual assembly when no use is specified; infer relative scale if physical dimensions are unknown and label hidden structure as inferred. Ask for a missing reference or an essential ambiguous feature before dependent generation; continue environment checks and independent work. Exact interfaces require dimensions or a stated tolerance, not invented measurements. Status-only work needs a task ID and its local state-file path.

## Failure and completion

Missing keys block remote calls, not local work. Fix missing local dependencies without switching services or paying for another model. Resume known task IDs after interruption; reconcile uncertain submissions before any retry. The mesh poller pauses after its bounded processing window; resume the same task rather than treating timeout as remote failure. The local status watcher returns a timeout separately. See [API recovery](references/api-contract.md), [generation limits](references/ai-generation.md#cross-batch-budget), and [status monitoring](references/status-monitoring.md).

Success requires the requested parts, visual checks, a clean GLB export/reload, source and parameter delivery, and an accurate project state. Missing key parts or unresolved severe defects mean incomplete work, even if remote generation succeeded.

## Bundled runtime

This skill includes the API client, budget ledger, status tools, GLB metadata inspection, and Node dependency resolver. It installs independently. Before first execution, follow [Runtime integration](references/setup-integration.md); reuse compatible existing environments. Python 3.9+ uses the standard library. Prepare Three.js and optional rendering dependencies only as needed. Installing the skill does not initialize a project or authorize paid calls. Local-only work requires no API key.

## Load by task

- **Status only:** Read [Status monitoring](references/status-monitoring.md); use the task ID and state-file path without loading modeling images or history.
- **New or modified geometry:** Read [Routes and parts](references/modeling-routes.md). With single-view input, prepare multiview reference first, including for procedural work. Then build regular parts procedurally and prepare individual references for AI parts as needed.
- **Reference images or AI models:** Read [AI generation](references/ai-generation.md). Procedural projects with sufficient consistent views can skip API setup.
- **Existing assets:** Reuse them and read [Three.js workflow](references/threejs-runtime.md); continue only unfinished work.
- **Final delivery:** Follow [Validation and export](references/threejs-runtime.md#validation-and-export).
- **Save or resume:** Follow [Project state](references/project-state.md).

## Execution rules

Use JS/TS and Three.js for all local geometry, assembly, animation, rendering, and export. Do not use Blender or local DCC/CAD applications. Python helpers handle API calls, downloads, status, read-only metadata, and file checks; they do not manipulate geometry or images.

Deliver a validated GLB, the Three.js source project, parameters, and necessary inspection records. Retain actual renders needed for validation. Do not add reference explanation sheets, exploded-view illustrations, promotional images, videos, or ZIP archives unless requested. Modeling reference images remain part of the workflow.

Advance ready parts without waiting for the entire batch. Use the [direct textured workflow](references/ai-generation.md#direct-textured-models). Do not reload unchanged instructions, script source, or unaffected review views.

Checks and acceptance are performed by the assistant, not automatic user approval gates. Choose reasonable implementation defaults within scope and record them. Ask only when missing information materially changes the result and cannot be inferred, or when an action exceeds existing authorization. Continue independent work while awaiting necessary answers. Honor explicit requests to review before execution.

## Authorization and service use

This public skill grants no standing authorization to spend credits or upload files. Use the current user's instructions and any authorization already established in the conversation. Before a paid submission, establish permission to upload the necessary task references to V2Fun and spend account credits under a finite task plan. If that scope is already authorized, explain the strategy, record the budget, and continue without asking again. Otherwise present the concrete call plan and obtain the missing authorization.

Use only credentials supplied through the current environment or an explicitly selected project configuration. Never include credentials in prompts, logs, source, or deliverables. Follow [API handling](references/api-contract.md) and [budget rules](references/ai-generation.md#cross-batch-budget).

Default reference generation uses gpt-image-2; 3D uses pro with all three texture flags enabled. Do not silently switch services or models. Respect user limits across batches and recovery. New stages or paid retries outside the authorized plan require additional authorization. Installation, configuration, a ledger entry, or a model's own decision cannot grant permission.

Skill edits and analysis do not start generation. Image-only requests do not start 3D generation. Unrelated uploads, public publishing, account top-ups, and unlimited retries are outside modeling authorization.
