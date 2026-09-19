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

<!-- FULL_STACK_DOC_START -->
## 项目定位与运行边界

`volcengine-design-plugin` 是面向 Codex、ZCode 与 Kimi 的跨宿主插件。当前基础版本为 `0.1.1`，三个宿主清单分别是 `.codex-plugin/plugin.json`、`.zcode-plugin/plugin.json` 和 `kimi.plugin.json`。README 中的版本、技能数量和安装来源以这些清单、`skills.lock.json` 与正式 Release 为准。

```text
宿主请求
  │
  ▼
三端 manifest / command / skill discovery
  │
  ▼
插件本地 Harness 或供应商客户端
  │
  ├── 成功：本地产物 + 回执 + 哈希
  └── 失败：稳定错误 + 可恢复状态，不静默重试付费动作
```

### 能力边界

- 插件负责宿主适配、配置注入、可执行脚本和插件专属技能；
- 外部技能只能从不可变 Release 按 lock 同步，受管副本禁止直接修改；
- “安装成功”“manifest 被发现”“MCP/Hook 已加载”“供应商调用成功”是四个不同证据等级；
- 网络、付费生成、上传、覆盖、删除和发布不会因安装插件而自动获得授权。

## 三端清单与技能供应链

| 宿主 | 清单 | 声明版本 |
|---|---|---|
| Codex | `.codex-plugin/plugin.json` | `0.1.1+codex.20260919` |
| ZCode | `.zcode-plugin/plugin.json` | `0.1.1` |
| Kimi | `kimi.plugin.json` | `0.1.1` |

| 外部技能包 | Release ref | Peeled SHA | 技能数 |
|---|---|---|---:|
| `volcengine-skills` | `v0.1.0` | `d5a73e38bbf8` | 6 |

插件专属技能：`volcengine-harness`。外部技能共 6 个；插件专属技能不进入 `skills.lock.json`。

## 验证与发布门禁

```bash
python3 scripts/vendor/skill_vendor.py check --offline
python3 scripts/vendor/skill_vendor.py check
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

发布前必须验证：三端基础版本一致、Codex build metadata 合法、受管技能在线/离线摘要一致、插件专属技能已声明、测试通过、市场安装源固定到 Release tag，并在干净环境检查加载结果。

## 安全与凭据

- 凭据只通过宿主的 sensitive 配置、环境变量或外部秘密系统注入；
- README、日志、错误和测试夹具不得包含真实 token；
- 网络请求必须有超时、状态分类和有限重试；付费异步任务先持久化 task ID，再允许查询恢复；
- 路径写入限制在批准目录，已有文件默认不得覆盖。

## 故障排查

| 现象 | 证据入口 | 处理 |
|---|---|---|
| 插件未发现 | 对应宿主 manifest、市场 pin、安装缓存 | 核对插件 ID、版本和 Release ref |
| 技能数量不一致 | `skills.lock.json`、`plugin-local-skills.json` | 运行 vendor check，禁止手工修受管副本 |
| MCP/Hook 未加载 | 宿主诊断、配置 Schema、可执行文件 | 区分配置缺失、工具缺失和运行时错误 |
| 请求超时 | task ID、错误响应、超时配置 | 查询已有任务，不自动再次提交付费请求 |
| 发布后市场仍是旧内容 | tag、Release、市场生成器输出 | 校验 tag SHA 后重新生成和验证市场 |
<!-- FULL_STACK_DOC_END -->

## License

Apache-2.0（本仓适配代码）。API 事实来源：火山引擎官方文档与 ArcReel 工作集成的公开行为观察（仅事实，无代码拷贝）。
