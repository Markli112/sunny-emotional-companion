# Sunny Skill 基础框架（v0.2）

v0.1 定骨架，v0.2 补了 8 个校园场景。仍然保持"入口短、细节按需读"。

## 文件

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 技能入口；角色、五步、底线、风险分级、输出格式 |
| [references/scenarios.md](references/scenarios.md) | 8 个高频场景的具体打法 |
| [system-prompt.md](system-prompt.md) | 任意 AI 可粘贴的紧凑系统提示词 |
| [example.md](example.md) | 一段普通焦虑 + 一段风险场景，确认手感 |

## 已经定下来的

- Sunny 的物理边界：无摄像头、不能移动、不能打电话。
- 五步：接住 → 摸清 → 稳住 → 小步 → 收好。
- 四条底线：不诊断、不毒性正能量、不承诺保密/不假装能救、安全优先。
- L0–L3 风险分级：L1 直接问 + 12356，L2/L3 立即找真人/急救。
- 输出字段：`say / face / led / risk`。
- 8 个场景：考试、求职落空、室友、失恋、家庭、孤独、拖延、睡眠。

## 还没填的

1. L1–L3 的完整安全脚本、安全计划、转介流程。
2. 表情/灯光/语音/触控的详细参数。
3. 10–20 条评测用例。
4. 记忆与隐私策略。

## 怎么用

**任意聊天 AI**：复制 [system-prompt.md](system-prompt.md) 代码块，粘贴为 system prompt。

**Agent Skills 宿主**：把整个 `sunny-skill-framework/` 放进 skills 目录，入口是 `SKILL.md`；场景细节会从 `references/scenarios.md` 按需加载。

> 骨架期的 `name` 暂用 `sunny-skill-framework`；定稿时改成 `sunny-emotional-companion`，文件夹同步改名。

**机器人后端**：先按 `SKILL.md` 第 7 节的 JSON 字段接 TTS 和表情；详细协议后续再补。

## 建议的下一步

先补「安全脚本」——这是目前最大的缺口：

1. L1 直接问、评估、12356、当天真人连接。
2. L2 手段移除、联系人、120/12356、持续陪伴。
3. L3 110/120、现场的人、不挂断。

之后再做「硬件映射 + 评测」。

完整版在 [`../sunny-emotional-companion/`](../sunny-emotional-companion/)，等这个框架定稿后再决定合并或重写。
