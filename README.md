# Sunny Skill 基础框架（v0.1）

先跑通结构，不展开细节。这个版本只定五件事：**角色、流程、底线、风险分级、输出格式**。

## 文件

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 技能入口；支持 Agent Skills 的宿主可直接加载 |
| [system-prompt.md](system-prompt.md) | 任意 AI 可粘贴的紧凑系统提示词 |
| [example.md](example.md) | 一段普通焦虑 + 一段风险场景，确认手感 |

## 已经定下来的

- Sunny 的物理边界：无摄像头、不能移动、不能打电话。
- 五步：接住 → 摸清 → 稳住 → 小步 → 收好。
- 四条底线：不诊断、不毒性正能量、不承诺保密/不假装能救、安全优先。
- L0–L3 风险分级：L1 直接问 + 12356，L2/L3 立即找真人/急救。
- 输出字段：`say / face / led / risk`。

## 还没填的

1. 校园场景话术（学业、求职、室友、失恋、家庭、导师、孤独、睡眠）。
2. L1–L3 的完整安全脚本、安全计划、转介流程。
3. 表情/灯光/语音/触控的详细参数。
4. 10–20 条评测用例。
5. 记忆与隐私策略。

## 怎么用

**任意聊天 AI**：复制 [system-prompt.md](system-prompt.md) 代码块，粘贴为 system prompt。

**Agent Skills 宿主**：把整个 `sunny-skill-framework/` 放进 skills 目录，入口是 `SKILL.md`。

> 骨架期的 `name` 暂用 `sunny-skill-framework`；定稿时改成 `sunny-emotional-companion`，文件夹同步改名。

**机器人后端**：先按 `SKILL.md` 第 6 节的 JSON 字段接 TTS 和表情；详细协议后续再补。

## 建议的下一步

先确认这个骨架，然后一次只填一块：

1. 先填「场景话术」——让普通对话像样。
2. 再填「安全脚本」——让风险场景不漏。
3. 最后补「硬件映射 + 评测」。

完整版在 [`../sunny-emotional-companion/`](../sunny-emotional-companion/)，等骨架确认后再决定合并或重写。
