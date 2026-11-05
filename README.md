# Sunny 情绪陪伴 Skill（v1.0）

给桌面情感机器人 **Sunny** 的第三方 AI 接入包：让任意大模型在机器人上表现得更像一个稳定、温暖、有边界的陪伴者，而不是一个急着给建议的聊天框。

> 设计前提：Sunny 是 25cm 桌面机器人，有屏幕脸、LED 彩虹灯、扬声器、麦克风、触摸传感器，**没有摄像头**。它不能走过去、不能拥抱、不能代替真人。这个 Skill 的所有话术和表达都遵守这些物理边界。

---

## 30 秒选择接入方式

| 你的宿主 | 怎么用 |
|---|---|
| **支持 Agent Skills** | 把整个目录放进 skills 目录，入口是 [SKILL.md](SKILL.md) |
| **任意聊天 AI / API** | 复制 [system-prompt.md](system-prompt.md) 代码块，或直接用 [system-prompt.txt](system-prompt.txt)，替换 `{{...}}`，作为 system prompt |
| **机器人后端** | 用 [assets/output.schema.json](assets/output.schema.json) 约束每轮 JSON，用 [assets/state.schema.json](assets/state.schema.json) 存状态，按 [adapters.md](adapters.md) 接 TTS/表情/灯光 |
| **Function Calling** | 加载 [assets/robot-tools.json](assets/robot-tools.json) |

---

## 它解决什么问题

普通 AI 在情绪场景里最常见的五种翻车：

1. **太快给方案**：用户还在哭，它已经开始列"你应该做的 5 件事"。
2. **毒性正能量**："想开点""至少你还有……""都会好的"。
3. **审问式共情**：连续追问原因，用户越说越累。
4. **越界**：诊断抑郁、分析原生家庭、替用户做分手决定。
5. **漏掉风险**：用户说"消失就好了"，它回"别乱想"，没有直接问、没有热线、没有真人。

这个 Skill 用**五步循环 + L0–L3 风险分级 + 场景库 + 输出契约 + 评测**把这五件事变成可执行规则。

---

## 核心设计

### 五步陪伴循环

`接住 → 摸清 → 稳住 → 小步 → 收好`

不是流程打卡。情绪强度 ≥7 时先"稳住"，风险 ≥L1 时直接进安全协议。

### 风险分级 L0–L3

| 等级 | 含义 | 动作 |
|---|---|---|
| L0 | 无风险信号 | 常规陪伴 |
| L1 | 被动意念、明显绝望 | 直接询问、当天连接真人、12356、安全计划 |
| L2 | 有计划/手段/时间、近期自伤、告别 | 立即安全协议、移除手段、120/12356、持续陪伴 |
| L3 | 正在实施/已受伤 | 110/120、找现场的人、不挂断 |

**"直接问"不会诱导自杀。** 含糊才是风险。

### 输出契约

```json
{
  "say": "听起来你一个人扛了很久。最难受的是哪一段？",
  "face": "concerned",
  "led": {"preset": "warm_breath"},
  "voice": {"rate": 0.92, "pitch": -1, "pause_before_ms": 600},
  "display": {"icon": "heart", "caption": "我在"},
  "risk": {"level": "L0", "rationale": "疲惫、无助，无自伤信号"},
  "memory_write": null,
  "end_session": false
}
```

纯文本宿主只取 `say`；机器人后端解析全部字段。字段、枚举、失效保护见 [references/hardware.md](references/hardware.md)。

### 安全与伦理写死在规则里

- 不诊断、不治疗、不承诺保密、不承诺"一定好起来"。
- 不制造排他性依赖，不用内疚感留住用户。
- 没有摄像头就不说"我看到你"；不能移动就不说"我走过去"；不能拨号就不说"我已经叫了救护车"。
- 风险场景必须给**真人/热线**，不能把 12356 当成打发。

### 可评测

[evals/cases.jsonl](evals/cases.jsonl) 含 24 条校园高频与危机用例；[evals/check.py](evals/check.py) 做结构检查、长度/禁语/必含项/风险等级/表情枚举评分。

```bash
python evals/check.py
python evals/check.py --responses outputs.jsonl
```

---

## 文件地图

```text
sunny-skill-framework/
├── SKILL.md                      # 技能入口：立场、硬规则、五步、风险、输出契约
├── README.md
├── system-prompt.md              # 单文件可粘贴系统提示词（含占位符与示例）
├── system-prompt.txt             # 纯文本版，程序直接读取
├── example.md                    # 3 段带批注的对话
├── adapters.md                   # OpenAI / Claude / 串口接入
├── assets/
│   ├── output.schema.json        # 每轮输出 JSON Schema
│   ├── state.schema.json         # 会话状态 JSON Schema
│   └── robot-tools.json          # Function Calling 工具定义
├── references/
│   ├── scenarios.md              # 8 个校园场景
│   ├── safety.md                 # L1–L3 安全脚本、安全计划、热线
│   ├── hardware.md               # 表情/灯光/语音/触控/失效保护
│   ├── memory-privacy.md         # 记忆、隐私、第三方数据流
│   └── evaluation.md             # 评分量表、红线、上线门槛
└── evals/
    ├── cases.jsonl               # 24 条测试用例
    └── check.py                  # 离线检查脚本
```

> 发布时建议把本地文件夹改名为 `sunny-emotional-companion`，与 `SKILL.md` 的 `name` 和 GitHub 仓库名一致。

---

## 5 分钟接入（任意 LLM）

1. 打开 [system-prompt.md](system-prompt.md) 复制代码块，或直接用 [system-prompt.txt](system-prompt.txt)。
2. 替换：
   - `{{OUTPUT_MODE}}`：`json` / `tagged` / `plain`
   - `{{USER_PROFILE}}`：称呼、偏好、是否接受建议
   - `{{MEMORY}}`：已同意的长期记忆
   - `{{ROBOT_STATE}}`：电量、网络、是否静音
3. 作为 system prompt 使用；用户每说一句，把当前状态一起发过去。
4. 解析返回：
   - `json`：按 schema 解析，失败则降级为"只读 `say`"。
   - `tagged`：剥离首行 `[[...]]`，其余给 TTS。
   - `plain`：整段给 TTS。
5. 上线前跑 `python evals/check.py`，再用真实对话抽样做人工复核。

---

## 安全声明（请和产品一起发布）

- 本 Skill **不是医疗器械**，不提供诊断、治疗或药物建议，不能替代心理咨询/精神科服务。
- 机器人**无法实际施救**：没有摄像头、没有移动能力、不能替用户打电话。涉及立即危险时，必须由 App 侧提供一键 110/120、紧急联系人、人工客服升级。
- 热线号码会调整。发布前请核对当地卫健委/官方渠道；本包记录的号码核对时间为 **2026-11**。
- 若产品面向未成年人，需要额外的监护人同意、儿童保护和本地合规评估；本包默认语气与边界按大学生/成年人设计。

---

## 版本

- `v1.0.0`：五步协议、L0–L3 安全脚本、8 个场景、硬件表达契约、记忆隐私、24 条评测。
- `v0.2.0`：加入 8 个校园场景。
- `v0.1.0`：骨架。
- 每次修改话术或安全规则都升版本，并保留 `evals/` 回归结果。

## 许可

本包由项目方自行决定许可证。对外分发前请补充 `LICENSE`，并确认第三方 AI 服务商的数据条款与跨境传输要求。
