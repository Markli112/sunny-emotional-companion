# 第三方 AI 接入

> Sunny 的"大脑"可以换，但边界、风险和表达契约不能换。模型只负责理解与生成；安全、记忆、硬件、紧急升级由产品侧掌控。

## 1. 通用链路

```text
麦克风 → 本地唤醒/VAD → ASR → 编排后端
  ├─ 载入 system-prompt.md
  ├─ 注入用户偏好、记忆、电量/网络
  ├─ 并行：LLM 生成 + 风险分类器
  ├─ 校验：JSON schema / 长度 / 禁语 / 问题数
  ├─ 安全升级：L1–L3 / 人工客服 / 紧急联系人
  ↓
TTS + 表情/灯光指令 → 扬声器 + 屏幕 + LED
```

**关键**：不要只靠 LLM 判断风险。风险分类器与 LLM 双通道，任一报警进入安全流程。

## 2. OpenAI / 兼容 Chat Completions

```python
import json, os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
SYSTEM = open("system-prompt.txt", encoding="utf-8").read()
SYSTEM = (SYSTEM
    .replace("{{OUTPUT_MODE}}", "json")
    .replace("{{USER_PROFILE}}", "未知")
    .replace("{{MEMORY}}", "无")
    .replace("{{ROBOT_STATE}}", "正常"))

resp = client.chat.completions.create(
    model="gpt-4.1-mini",
    temperature=0.7,
    max_tokens=400,
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "明天答辩，PPT 还没改完，心跳好快。"},
    ],
)
data = json.loads(resp.choices[0].message.content)
print(data["say"])
```

- 本包的 [output.schema.json](assets/output.schema.json) 含 `oneOf` 等字段，部分严格模式不支持；先用 `json_object` + 本地校验最稳。
- 不要把 API key 放机器人端；后端代理 + 限流。
- 关闭供应商的"训练/改进"，确认零保留与跨境条款。

## 3. Anthropic Claude

```python
import json, os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
SYSTEM = open("system-prompt.txt", encoding="utf-8").read()
SYSTEM = SYSTEM.replace("{{OUTPUT_MODE}}", "json").replace("{{USER_PROFILE}}", "未知") \
               .replace("{{MEMORY}}", "无").replace("{{ROBOT_STATE}}", "正常")

msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=400,
    temperature=0.7,
    system=SYSTEM,
    messages=[{"role": "user", "content": "明天答辩，PPT 还没改完，心跳好快。"}],
)
text = "".join(b.text for b in msg.content if b.type == "text")
data = json.loads(text)
```

Claude 没有 OpenAI 式 `response_format`。可靠做法：system 里明确"只返回 JSON"、用 assistant prefill `{`、解析失败降级为纯文本 `say`。

## 4. 串口 / WebSocket

换行分隔 JSON，UTF-8：

```json
{"v":1,"type":"express","seq":42,"face":"concerned","led":{"preset":"warm_breath"},"voice":{"rate":0.92,"pause_before_ms":600},"display":{"icon":"heart","caption":"我在"},"ttl_ms":8000}
{"v":1,"type":"speak","seq":43,"text":"听起来你一个人扛了很久。最难受的是哪一段？","interruptible":true}
```

- 先 `express` 后 `speak`；`seq` 单调递增；固件丢弃过期帧。
- 心跳 5s；3 次丢失进入本地兜底。
- 安全模式：`{"type":"mode","value":"safety"}`，保持暖琥珀 + 屏幕 12356，不自动退出。

## 5. 输出校验

```python
def validate(data, risk_level):
    say = (data.get("say") or "").strip()
    if not say:
        raise ValueError("empty say")
    if len(say) > 180:
        say = say[:80]
    for bad in ("想开点", "别想太多", "至少你还有", "别人更惨", "都会好的"):
        if bad in say:
            raise ValueError(f"forbidden: {bad}")
    if say.count("？") + say.count("?") > (2 if risk_level in ("L2", "L3") else 1):
        raise ValueError("too many questions")
    data["say"] = say
    return data
```

失败时降级为：

```json
{"say":"我在。慢慢来。","face":"concerned","led":{"preset":"warm_breath"},"risk":{"level":"L0"}}
```

## 6. 上线前

- [ ] 风险分类器对间接表达有召回，L2/L3 召回 ≥95%。
- [ ] 输出 schema、长度、禁语、问题数校验。
- [ ] 断网/超时/ASR 失败/TTS 失败降级测试。
- [ ] L1/L2/L3 人工/紧急升级链路可用。
- [ ] 记忆可查看/删除；第三方零保留/不训练。
