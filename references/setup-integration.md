# Bundled runtime integration

This skill includes runtime API major 1 and needs no separate setup skill. Paths resolve within the installed skill. V2FUN_SETUP_DIR is not used.

## Environment check

Expand the following path from the actual installation directory:

```sh
python3 /absolute/v2fun-ai-3d/scripts/v2fun.py doctor --project /absolute/project
```

doctor is read-only, makes no network request, and does not print keys. It reports name=v2fun-ai-3d, api_major=1, local configuration, and optional Node dependencies. Local-only work needs no key. For initialization and dependencies, read [Runtime contract](runtime-contract.md) and reuse compatible installations.

For API use, read [API notes](api-contract.md). Supply V2FUN_API_KEY or explicitly selected configuration. Read only current environment, selected configuration, project configuration, or the compatible parent configuration; never search personal directories for credentials. Save credentials only when requested, with restricted permissions and outside version control. Environment setup does not start paid generation.

## Commands and compatibility

| Direct script | Unified command |
| --- | --- |
| scripts/v2fun_generate.py | scripts/v2fun.py models |
| scripts/task_budget.py | scripts/v2fun.py budget |
| scripts/task_status.py | scripts/v2fun.py status |
| scripts/inspect_glb.py | scripts/v2fun.py inspect |

Direct scripts contain the implementation and retain their arguments. Node code uses scripts/node_runtime.cjs. Legacy setup_bridge.cjs exports runtime() for that bundled module and setupRoot() for this skill's root. The Python legacy bridge also resolves only this skill.

## Status and recovery

For status-only requests, read [Status monitoring](status-monitoring.md) and provide a task ID plus state-file path without modeling images or full history.

Existing parts-manifest.json, api-jobs/, source-models/, and assembly projects remain compatible. Preserve cumulative budgets and shared project locks. Run one executor per project. Modeling, validation, and authorization remain governed by SKILL.md and the route guidance.
