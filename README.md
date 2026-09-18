<div align="center">

<a href="https://v2fun.ai/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg" />
    <img src="assets/logo.svg" width="250" height="100" alt="V2Fun" />
  </picture>
</a>

# V2Fun AI 3D

**AI 3D Modeling with Hybrid AI Generation and Procedural Three.js**

Choose the right method for each part. Assemble in Three.js. Deliver a GLB and editable source.

[English](./README.md) | [简体中文](./README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version: 1.0.0](https://img.shields.io/badge/version-1.0.0-green.svg)](runtime.json)
[![Runtime: Three.js](https://img.shields.io/badge/runtime-Three.js-000000.svg)](https://threejs.org/)
[![Tooling: Python 3.9+ stdlib](https://img.shields.io/badge/tooling-Python%203.9%2B%20stdlib-3776AB.svg)](scripts)
[![Sponsor: V2Fun](https://img.shields.io/badge/Sponsor-V2Fun-16161A.svg)](https://v2fun.ai/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/2uBMRp275u)

</div>

---
## Live demos

Explore the V2Fun AI 3D showcase on the V2Fun website.

| Demo | Description | View |
| --- | --- | --- |
| Astra 3D Modeling Showcase | Explore a reference-based object, its procedural and AI-generated parts, and the assembled result. | [Live](https://v2fun.ai/solution/gpt-6-astra/) |

---

## What it does

Give the skill reference images or an existing model. It plans the parts, chooses procedural construction, V2Fun AI generation, or reuse, then assembles the result in Three.js.

- **Regular forms, built in code.** Shells, brackets, pipes, mechanical structures, and repeated components use explicit geometry and reusable parameters.
- **Organic forms, generated with AI.** People, animals, complex folds, and sculpted details use V2Fun textured-mesh generation.
- **Hybrid assemblies.** Combine generated subjects with procedural bases, interfaces, and supporting structures.
- **Reusable assets.** Keep suitable existing models and instance repeated parts instead of generating every copy.
- **Resumable work.** Preserve task IDs, local state, and cumulative budgets across batches and interruptions.
- **Standalone installation.** The API client, dependency helpers, budget tools, and status commands are included. No separate setup skill is required.

This is a visual-mesh workflow. Exact CAD/STEP output, automatic rigging, certified print preparation, and video production are outside its scope.

Image generation currently has workflow/API guidance but no generic submit command. Standalone texturing, retopology, and automatic rigging are not implemented by this skill.

## How it works

**References → part plan → build or generate → Three.js assembly → inspect → GLB + source**

1. **Plan.** Identify the subject, important features, part boundaries, methods, and a finite API call plan.
2. **Prepare references.** For single-view input, first prepare front/side/rear reference views. Reuse suitable multiview references when available.
3. **Build ready parts.** Construct regular geometry locally; generate textured AI parts using the approved plan.
4. **Assemble.** Align scale, axes, anchors, contact surfaces, and materials in Three.js.
5. **Validate and deliver.** Inspect the rendered model, export GLB, reload it in a clean scene, and deliver source plus validation records.

Default remote models are `gpt-image-2` for reference images and `pro` for meshes with texture, PBR, and HD texture enabled. Uploads and credit use require current-user authorization. The assistant reuses existing authorization and does not reset budgets when resuming.

See [modeling routes](references/modeling-routes.md), [generation and recovery](references/ai-generation.md), and [validation](references/threejs-runtime.md).

## Quick start

### 1. Install the skill

Extract the skill folder into `~/.codex/skills/v2fun-ai-3d/`. With a custom `CODEX_HOME`, use its `skills/v2fun-ai-3d/` directory. `SKILL.md` must sit directly inside that folder.

Use Codex with local skill support, Python **3.9+**, and Node.js/Three.js with a WebGL browser for local 3D work. Python helpers use the standard library. Playwright and sharp are optional; reuse compatible installed dependencies.

Existing installations: replace the old `v2fun-hybrid` skill directory with `v2fun-ai-3d` to avoid loading duplicate skills. Preserve project configuration, task IDs, source assets, and budget records; invoke `$v2fun-ai-3d` afterward.

### 2. Check your environment

From the installed skill directory:

```sh
python3 scripts/v2fun.py doctor --project examples/local-inventory
python3 scripts/v2fun.py models --project examples/local-inventory
```

The second command returns:

```json
{"ai_parts": 0, "new_tasks": 0, "status": "no_ai_work"}
```

This offline example inventories a procedural part; it does not generate a model.

### 3. Attach your references and ask

> Use $v2fun-ai-3d to rebuild the object in these references. Choose a method for each part, explain the API call plan, and deliver a GLB with its Three.js source project.

For remote work, supply `V2FUN_API_KEY` through the execution environment or an explicitly selected local JSON configuration. Keep credentials out of source control. Remote calls consume V2Fun credits.

Single-view input normally needs remote reference preparation even when the final mesh is procedural. Use sufficient consistent views or reusable assets for local-only modeling. Provide dimensions when exact interfaces matter.

### Troubleshooting

| Situation | Action |
| --- | --- |
| Missing API key | Configure credentials for authorized remote work; local checks can continue |
| Missing Three.js | Reuse an explicit dependency path or install the required pinned package |
| Polling timeout | Inspect the saved state and resume the existing task |
| Uncertain submission | Reconcile the original request before another paid call |

## What you get

| Deliverable | Contents |
| --- | --- |
| **GLB model** | The assembled model, checked by export and clean-scene reload |
| **Three.js source** | Reproducible JS/TS construction and assembly code |
| **Parameters** | Dimensions, transforms, part relationships, and reusable settings |
| **Inspection records** | Necessary rendered evidence, export checks, and known limitations |
| **Task state** | Original task IDs, source assets, and cumulative budget records |

A download or metadata report alone is not acceptance. Missing key parts, lost textures, or severe intersections remain unfinished work. Hidden geometry inferred from references is not a measured reconstruction.

## Roadmap

### v1.0.0

- [x] Standalone runtime and part-based procedural/AI routing.
- [x] Mesh submission, in-process polling, download, and recovery.
- [x] Cumulative budgets and independent local status queries.
- [x] Bilingual documentation and MIT license.

## Star history

If V2Fun AI 3D is useful to you, a star helps other creators discover it.

[![Star History Chart](https://api.star-history.com/svg?repos=V2Fun-Research/v2fun-ai-3d&type=Date)](https://www.star-history.com/#V2Fun-Research/v2fun-ai-3d&Date)

## Sponsors

V2Fun is the sole sponsor presented in this project.

<table>
  <tr>
    <td align="center" width="160">
      <a href="https://v2fun.ai/">
        <img src="assets/sponsors/v2fun-square.png" width="96" height="96" alt="V2Fun square logo" />
      </a>
      <br /><strong>V2Fun</strong>
      <br /><sub>AI-powered 3D creation</sub>
    </td>
    <td>
      <strong><a href="https://v2fun.ai/">V2Fun</a></strong> brings image generation, 3D modeling, and character animation into a browser-based creation platform. Creators can begin with text or reference images and develop ideas into 3D assets. In V2Fun AI 3D, its reference-image and textured-model generation complement procedural Three.js construction: AI handles organic forms, while code defines regular structures and assembly. The result stays connected to its source project, parameters, and task records so that work can be inspected and continued. This skill uses a focused part of the wider platform; platform features such as rigging are not automatically included in the skill.
      <br /><br />
      <strong><a href="https://v2fun.ai/">Explore V2Fun →</a></strong>
    </td>
  </tr>
</table>

Release owner and maintainer: **V2Fun Team**. Questions and feedback: [V2Fun Discord](https://discord.com/invite/2uBMRp275u).

[V2Fun Skill Overview](https://v2fun.ai/developers/skill) · [Runtime documentation](references/runtime-contract.md)

## Acknowledgments

Thanks to [img2threejs](https://github.com/img2threejs/img2threejs) and its contributors for inspiring V2Fun AI 3D through its reference-image-driven procedural Three.js modeling approach and clear README presentation.

## License

[MIT License](LICENSE)<br>
Copyright © 2026 V2Fun Team.

The license covers this project's code and documentation. Optional dependencies keep their own licenses; see [third-party scope](THIRD_PARTY.md). Brand marks identify V2Fun and do not grant trademark rights. Service access, reference-material rights, and generated-asset usage are governed separately.
