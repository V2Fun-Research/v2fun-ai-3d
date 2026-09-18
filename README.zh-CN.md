<div align="center">

<a href="https://v2fun.ai/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg" />
    <img src="assets/logo.svg" width="250" height="100" alt="V2Fun" />
  </picture>
</a>

# V2Fun AI 3D

**AI 3D 混合建模：结合 AI 生成与 Three.js 程序化建模**

按部件选择方法，在 Three.js 中装配，交付 GLB 与可编辑源码。

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

在 V2Fun 官网查看 V2Fun AI 3D 演示。

| 演示 | 介绍 | View |
| --- | --- | --- |
| Astra 3D 建模演示 | 查看参考物体、过程式与 AI 生成部件，以及最终装配效果。 | [Live](https://v2fun.ai/solution/gpt-6-astra/) |

---

## What it does

提供参考图或已有模型，技能会规划部件，选择过程式构建、V2Fun AI 生成或资产复用，再统一在 Three.js 中装配。

- **规则形体，用代码构建。** 壳体、支架、管路、机械结构及重复组件使用明确的几何和可复用参数。
- **有机形体，用 AI 生成。** 人物、动物、复杂衣褶与雕刻细节采用 V2Fun 带贴图网格生成。
- **混合装配。** 将生成主体与过程式底座、接口和支撑结构组合。
- **复用已有资产。** 保留合格模型，重复部件采用实例复用，不逐件重新生成。
- **可恢复的任务。** 跨批次和中断保留任务 ID、本地状态及累计预算。
- **独立安装。** 内置 API 客户端、依赖辅助工具、预算和状态命令，无需另装 setup 技能。

这是视觉网格工作流，不包含精确 CAD/STEP 输出、自动绑骨、经过认证的打印准备或视频制作。

当前生图已有工作流及 API 说明，但没有通用提交命令。本技能尚未实现独立贴图、重拓扑或自动绑骨。

## How it works

**参考图 → 部件规划 → 构建或生成 → Three.js 装配 → 检查 → GLB + 源码**

1. **规划。** 明确主体、关键特征、部件边界、制作方式和有限的 API 调用计划。
2. **准备参考。** 单视图输入先补齐正、侧、背参考；已有合格多视图时直接复用。
3. **处理就绪部件。** 规则几何在本地构建，AI 部件按已授权计划直接生成带贴图模型。
4. **装配。** 在 Three.js 中对齐尺度、轴向、锚点、接触面和材质。
5. **验证与交付。** 检查实际渲染，导出 GLB，在干净场景重载，交付源码及验证记录。

远程参考图默认使用 `gpt-image-2`；网格默认使用 `pro`，开启贴图、PBR 和高清贴图。上传和积分消费需要当前用户授权；已有授权直接复用，恢复任务不重置预算。

详见 [建模路线](references/modeling-routes.md)、[生成与恢复](references/ai-generation.md) 和 [验证流程](references/threejs-runtime.md)。

## Quick start

### 1. 安装技能

将技能文件夹解压到 `~/.codex/skills/v2fun-ai-3d/`。使用自定义 `CODEX_HOME` 时，放入其 `skills/v2fun-ai-3d/` 目录。`SKILL.md` 必须直接位于该目录。

使用支持本地技能的 Codex、Python **3.9+**，并为本地三维工作准备 Node.js、Three.js 和 WebGL 浏览器。Python 辅助脚本仅用标准库。Playwright 和 sharp 按需使用，优先复用兼容依赖。

已有安装：将旧的 `v2fun-hybrid` 技能目录替换为 `v2fun-ai-3d`，避免同时加载两个副本。保留项目配置、任务 ID、源资产和预算记录；之后使用 `$v2fun-ai-3d` 调用。

### 2. 检查环境

在已安装的技能目录执行：

```sh
python3 scripts/v2fun.py doctor --project examples/local-inventory
python3 scripts/v2fun.py models --project examples/local-inventory
```

第二条命令返回：

```json
{"ai_parts": 0, "new_tasks": 0, "status": "no_ai_work"}
```

此离线示例只盘点过程式部件，不生成模型。

### 3. 附上参考图并提出任务

> 使用 $v2fun-ai-3d，按这些参考图重建物体。按部件选择方法，说明 API 调用计划，并交付 GLB 和 Three.js 源码工程。

远程工作通过执行环境中的 `V2FUN_API_KEY` 或明确指定的本地 JSON 配置认证，不要将凭据提交到仓库。远程调用消耗 V2Fun 积分。

单视图输入通常需要远程补图，即使最终网格采用过程式路线也适用。纯本地建模请提供充分且一致的多视图或合格资产；需要精确接口时提供尺寸。

### 故障排查

| 情况 | 处理 |
| --- | --- |
| 缺少 API 密钥 | 为已授权远程任务配置凭据，本地检查可以继续 |
| 缺少 Three.js | 复用显式依赖路径，或安装所需的固定版本 |
| 轮询超时 | 检查保存的状态，恢复原任务 |
| 提交结果不确定 | 核实原请求后再决定是否再次付费调用 |

## What you get

| 交付物 | 内容 |
| --- | --- |
| **GLB 模型** | 完成装配，并经导出和干净场景重载检查的模型 |
| **Three.js 源码** | 可复现的 JS/TS 构建与装配代码 |
| **参数** | 尺寸、变换、部件关系与可复用设置 |
| **检查记录** | 必要的渲染证据、导出检查及已知局限 |
| **任务状态** | 原任务 ID、源资产与累计预算记录 |

下载成功或元数据报告不足以完成验收。关键部件缺失、贴图丢失或严重穿插仍属于未完成问题。由参考图推断的隐藏几何不代表实测重建。

## Roadmap

### v1.0.0

- [x] 独立运行能力，以及按部件选择过程式／AI 路线。
- [x] 网格提交、进程内轮询、下载和恢复。
- [x] 累计预算与独立本地状态查询。
- [x] 双语文档和 MIT 许可。

## Star history

如果 V2Fun AI 3D 对你有帮助，欢迎点亮 Star，让更多创作者发现它。

[![Star History Chart](https://api.star-history.com/svg?repos=V2Fun-Research/v2fun-ai-3d&type=Date)](https://www.star-history.com/#V2Fun-Research/v2fun-ai-3d&Date)

## Sponsors

本项目仅展示 V2Fun 一家赞助方。

<table>
  <tr>
    <td align="center" width="160">
      <a href="https://v2fun.ai/">
        <img src="assets/sponsors/v2fun-square.png" width="96" height="96" alt="V2Fun 方形 Logo" />
      </a>
      <br /><strong>V2Fun</strong>
      <br /><sub>AI 驱动的三维创作</sub>
    </td>
    <td>
      <strong><a href="https://v2fun.ai/">V2Fun</a></strong> 将图像生成、三维建模和角色动画整合到浏览器创作平台中，让创作者从文字或参考图出发，将想法发展为三维资产。在 V2Fun AI 3D 中，参考图与带贴图模型生成和 Three.js 过程式构建配合：AI 处理有机形体，代码定义规则结构与装配关系。结果保留对应的源码工程、参数和任务记录，方便检查、修改与继续处理。本技能使用平台中与该工作流相关的能力；平台具备的绑骨等功能，并不因此自动包含在本技能中。
      <br /><br />
      <strong><a href="https://v2fun.ai/">探索 V2Fun →</a></strong>
    </td>
  </tr>
</table>

发布负责人和技术维护人：**V2Fun Team**。提问与反馈：[V2Fun Discord](https://discord.com/invite/2uBMRp275u)。

[V2Fun Skill 官网介绍](https://v2fun.ai/developers/skill) · [运行文档](references/runtime-contract.md)

## Acknowledgments

感谢 [img2threejs](https://github.com/img2threejs/img2threejs) 项目及其贡献者。其参考图驱动的过程式 Three.js 建模思路，以及清晰的 README 展示方式，为 V2Fun AI 3D 提供了启发。

## License

[MIT License](LICENSE)<br>
Copyright © 2026 V2Fun Team.

许可适用于本项目代码与文档。可选依赖保留各自许可，详见 [第三方范围](THIRD_PARTY.md)。品牌标识用于识别 V2Fun，不授予商标权；服务访问、参考素材权利和生成资产使用条件另行适用对应条款。
