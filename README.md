# PartMe.AI Volcengine Design Plugin

Tri-platform plugin (Codex / ZCode / Kimi Code) that connects coding agents to **Volcengine creation services** through deterministic stdlib clients (no SDK dependency):

- **豆包大模型 ASR** — 录音转写 with **millisecond word-level timestamps**（口播/短视频切片的时间轴事实底座）
- **豆包 TTS** — 解说配音生成（v3 unidirectional stream）
- **Seedream 生图** — 文生图 / 参考图编辑 / 组图（Ark `/images/generations`）
- **Seedance 生视频** — t2v / i2v / **FL2VA 首尾帧白模锚定** / 参考图（Ark task API，一次提交 + 断点轮询）

## Why it exists

多插件组合的**使能件**：生态里此前只有 ZCode 托管的 ASR（video-agent-kit），Codex/Kimi 上没有便携转写。本插件把 ASR/TTS/生图/生视频四族能力以同一套确定性客户端补齐后——

```
口播流水线：volcengine（ASR 词级时间轴→切片点）→ video-factory（装配）→ 剪映草稿导出
白模流水线：partme-blender（白模首尾帧）→ volcengine（Seedance FL2VA）→ volcengine（TTS 解说）
```

与 partme-minimax-design（H3）、partme-dreamina-design（即梦）、partme-comfy-plugin（ComfyUI）构成多供应商矩阵。

## Credential families (two, independent)

| 族 | 凭据 | 覆盖 | 获取 |
|---|---|---|---|
| 方舟 v3 | `ARK_API_KEY` | chat / Seedream / Seedance | [console.volcengine.com/ark](https://console.volcengine.com/ark) → API Key 管理 |
| 豆包语音 | `VOLCENGINE_APP_ID` + `VOLCENGINE_ACCESS_TOKEN` | ASR / TTS（openspeech） | [console.volcengine.com/speech/app](https://console.volcengine.com/speech/app) |

环境变量、项目 `.env`、`~/.volcengine-design/config.json` 三处均可；缺失时客户端 fail-fast 并给出补办指引。

## Installation

### Codex
```bash
codex plugin marketplace add partme-ai/plugins
codex plugin add volcengine-design@partme-ai
```

### ZCode
插件 → 添加插件市场 → `https://github.com/partme-ai/plugins` → 安装 `volcengine-design`。userConfig 三项（sensitive）分别注入两族凭据。

### Kimi Code CLI
```
/plugins marketplace https://raw.githubusercontent.com/partme-ai/plugins/main/kimi-marketplace.json
```

## Commands

| Command | 作用 |
|---|---|
| `/volcengine-setup` | 两族凭据配置指引 |
| `/volcengine-check` | 凭据与连通性体检 |
| `/volcengine-asr` | 转写：submit → wait → 词级毫秒时间轴 |
| `/volcengine-tts` | 配音：文本 → 音频落盘 |
| `/volcengine-image` | Seedream 生图（参考图/组图） |
| `/volcengine-video` | Seedance 生视频（FL2VA 白模锚定） |

## Cost discipline

- ASR ≈ 0.8 元/小时档；TTS 按字符；Seedream 按张、Seedance 按秒（分分辨率）。
- **发现/查询免费，生成计费**：视频任务提交前复述计费项；`task_id` 先持久化再报告；失败/超时上报，绝不自动二次提交。

## License

Apache-2.0（本仓适配代码）。API 事实来源：火山引擎官方文档与 ArcReel 工作集成的公开行为观察（仅事实，无代码拷贝）。
