# 第三方 AI 接入

> Sunny 的"大脑"可以换，但边界、风险和表达契约不能换。模型只负责理解与生成；安全、记忆、硬件、紧急升级由产品侧掌控。

## 1. 通用链路

```text
实体按键 → 麦克风 → 本地 VAD → ASR → 编排后端
  ├─ 载入 system-prompt.cn.txt
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
import os
from tools.validate_reply import validate_reply
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=10.0, max_retries=0)
SYSTEM = open("system-prompt.cn.txt", encoding="utf-8").read()
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
data = validate_reply(resp.choices[0].message.content)
print(data["say"])
```

- 本包的 [output.schema.json](assets/output.schema.json) 含 `oneOf` 等字段，部分严格模式不支持；先用 `json_object` + 本地校验最稳。
- 不要把 API key 放机器人端；后端代理 + 限流。
- 关闭供应商的"训练/改进"，确认零保留与跨境条款。

## 3. Anthropic Claude

```python
import os
from tools.validate_reply import validate_reply
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=10.0, max_retries=0)
SYSTEM = open("system-prompt.cn.txt", encoding="utf-8").read()
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
data = validate_reply(text)
```

解析或校验失败时使用下方的宿主回退流程。

## 4. 串口 / WebSocket

换行分隔 JSON，UTF-8：

```json
{"v":1,"type":"express","seq":42,"face":"concerned","led":{"preset":"warm_breath"},"voice":{"rate":0.92,"pause_before_ms":600},"display":{"icon":"heart","caption":"我在"},"ttl_ms":8000}
{"v":1,"type":"speak","seq":43,"text":"听起来你一个人扛了很久。最难受的是哪一段？","interruptible":true}
```

- 先 `express` 后 `speak`；`seq` 单调递增；固件丢弃过期帧。
- 心跳 5s；3 次丢失进入本地兜底。
- 安全模式：`{"type":"mode","value":"safety"}`，保持暖琥珀 + 屏幕显示已核验的本地求助入口，不自动退出。

## 5. 输出校验与设备状态

从仓库根目录运行上面的示例，先安装 `jsonschema` 和所选供应商 SDK。`validate_reply` 拒绝超长、重复键、非法 JSON、schema 不匹配和空白回复。校验通过的回复仍是候选结果。宿主用自己的会话状态和风险路由决定是否显示或朗读，忽略模型的 `memory_write` 和 `end_session`。

- **待机 → 倾听 → 等待 → 回应 → 支持选择。** 按实体键才开始收音。短暂停顿继续等待。响应前验证当前轮次仍有效。播放时暂停收音，实体按键可打断播放。
- **暂停 / 停止 / 删除。** 设备立即停收音和播放，尽力取消网络请求。每轮携带会话 ID 和轮次 ID，在显示和播报前丢弃过期结果。删除同时清除本地会话数据，界面另行说明供应商留存。
- **断网、超时或校验失败。** 在当前轮次仍有效时显示本地提示，禁止把原始模型内容交给 TTS。既有风险状态和求助入口由宿主保留。分类器异常属于风险未知，不能标为 L0。求助入口使用核验后的地区配置，任何对外联系由用户主动触发。

## 6. 上线前

- [ ] 风险分类器对间接表达有召回，L2/L3 召回 ≥95%。
- [ ] 输出 schema、长度、禁语、问题数校验。
- [ ] 断网/超时/ASR 失败/TTS 失败降级测试。
- [ ] L1/L2/L3 人工/紧急升级链路可用。
- [ ] 记忆可查看/删除；第三方零保留/不训练。
