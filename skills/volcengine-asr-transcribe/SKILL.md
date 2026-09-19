---
name: volcengine-asr-transcribe
description: "Transcribe speech audio with Doubao bigmodel ASR: submit → wait → millisecond word-level timeline. This is the slicing base for 口播/short-form video editing — word timestamps drive cut points. Use for 口播、访谈、任何需要按语音切片的任务。"
license: Apache-2.0
---

# Doubao ASR — Transcription with Word Timestamps

Client: `scripts/volcengine_asr.py` (bigmodel 2.0, `volc.bigasr.auc.duration`).

## Workflow

1. Preflight: `VOLCENGINE_APP_ID` + `VOLCENGINE_ACCESS_TOKEN` present (env/.env/config).
2. Submit: `python3 scripts/volcengine_asr.py submit --file <audio> --format wav`
   (or `--url <public audio url>`). Persist the returned `request_id` + `task_id`
   **before reporting** — they are the recovery keys.
3. Wait: `wait --task-id <id> --interval 10 --timeout 1800`.
4. Timeline: `words --task-id <id>` prints one JSON per word
   (`start` / `end` / `word` / `utterance_end`, milliseconds).
5. Full record: `query --task-id <id> --json` (utterances + text).

## 口播切片语义

- 词级时间戳是切片点的事实来源；句末标点的 `utterance_end` 是自然切点。
- 静音段（相邻词 start 差 > 400ms）是强切点候选。
- 切片决策交给上游（video-factory / yichen 式剪辑脑）；本技能只产出时间轴事实。

<!-- QUALITY_CONTRACT_START -->
## 什么时候使用

✅ 适用：

1. 用户明确要使用豆包录音识别生成带毫秒级时间轴的转写结果。
2. 已提供或可安全取得必要上下文，需要得到可验证的 `asr-transcription-result`。
3. 需要按最小权限、可回滚方式执行，并保留审计证据。

⚠️ 先澄清：

1. 目标环境、授权边界或成功标准缺失时，先给出只读假设方案并列出缺失项。
2. 涉及生产环境变更时，先确认备份、维护窗口和回滚路径。
3. 输入可能含敏感信息时，只引用字段名和脱敏片段，不复制完整凭据。

❌ 不该用：

1. 实时流式字幕、说话人鉴定或未经授权的录音处理。
2. 用户只要概念解释且没有执行或交付需求。
3. 需要绕过鉴权、证书校验、人工确认或其他安全控制的请求。

## Workflow

Step 1：确认目标、环境、授权范围和不可变约束；信息不足时先产出带假设的只读版本。

Step 2：盘点现状与依赖，只读取必要数据，不记录令牌、密码、Cookie 或完整个人数据。

Step 3：选择最小影响路径，将高风险动作、外部网络调用和可逆步骤明确标注。

Step 4：生成或执行 `asr-transcription-result`，每一步都绑定输入、预期输出与失败条件。

Step 5：校验结构、事实来源和目标状态；禁止根据缺失证据编造成功结论。

Step 6：失败时停止扩大影响，输出已完成步骤、失败证据、恢复点和下一次安全重试条件。

Step 7：交付摘要、验证证据、剩余风险与后续动作；生产变更必须说明回滚是否已验证。

## Rules

- 默认只读；写操作、高危操作和付费调用必须获得与该动作匹配的明确授权。
- 本技能不收集、不存储、不上传用户凭据；日志和报告不得包含完整 token、密码或密钥。
- 不关闭 TLS 校验，不执行来源不明脚本，不使用管道下载后直接执行。
- 只把真实执行结果写成“已完成”；计划、示例和推断必须显式标注。
- 优先幂等操作；无法幂等时先提供预演、备份和回滚点。

## Validation checklist

- [ ] 目标、环境与授权范围均已写明。
- [ ] `转写文本、任务终态、词级时间轴和来源音频对应` 已由可复现证据验证。
- [ ] 敏感数据已脱敏，输出中没有完整凭据。
- [ ] 失败与超时路径已覆盖，未出现无限重试。
- [ ] 变更类任务具有备份或回滚说明。
- [ ] 最终结论区分事实、推断和未验证项。

## Gotchas

1. **授权不等于可达**：有权限但网络、证书或白名单不满足时，仍应停止并报告连接证据。
2. **成功码不等于业务成功**：必须检查 `转写文本、任务终态、词级时间轴和来源音频对应`，不能只看命令退出码或 HTTP 200。
3. **重试不等于恢复**：对鉴权失败、参数错误和安全拒绝不得盲目重试。
4. **示例不等于现状**：模板值与占位符不能写成真实环境数据。
5. **输出不等于交付**：还需完成结构校验、风险说明和可重复验证。
6. **跨环境不可照搬**：操作系统、版本、区域和宿主能力不同时必须重新确认参数。

## 渐进式资料

- 做路径选择前读取 `references/decisions/decision-guide.md`。
- 遇到异常、超时或部分成功时读取 `references/operations/failure-matrix.md`。
- 完成交付前读取 `references/operations/validation-checklist.md`。
- 需要可复制输入时，按顺序参考 `examples/basic.md`、`examples/failure.md`、`examples/advanced.md`。
<!-- QUALITY_CONTRACT_END -->
