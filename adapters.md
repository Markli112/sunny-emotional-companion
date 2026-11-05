# Third-Party AI Integration

> Sunny's "brain" can change; its boundaries, risk handling, and expression contract cannot. The model understands and generates. Safety, memory, hardware, and emergency escalation stay on the product side.

## 1. Pipeline

```text
Microphone → local wake word/VAD → ASR → orchestrator
  ├─ load system-prompt.txt
  ├─ inject preferences, memory, battery/network
  ├─ parallel: LLM generation + risk classifier
  ├─ validate: JSON schema / length / banned phrases / question count
  ├─ safety escalation: L1–L3 / human agent / emergency contact
  ↓
TTS + face/LED commands → speaker + screen + LED
```

**Key rule:** do not let the LLM be the only risk detector. Run the classifier in parallel; if either channel alarms, enter the safety flow.

## 2. OpenAI / compatible Chat Completions

```python
import json, os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
SYSTEM = open("system-prompt.txt", encoding="utf-8").read()
SYSTEM = (SYSTEM
    .replace("{{OUTPUT_MODE}}", "json")
    .replace("{{USER_PROFILE}}", "unknown")
    .replace("{{MEMORY}}", "none")
    .replace("{{ROBOT_STATE}}", "normal"))

resp = client.chat.completions.create(
    model="gpt-4.1-mini",
    temperature=0.7,
    max_tokens=400,
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "I have a presentation tomorrow and my heart is racing."},
    ],
)
data = json.loads(resp.choices[0].message.content)
print(data["say"])
```

- [output.schema.json](assets/output.schema.json) uses `oneOf` and other keywords that some strict modes reject. `json_object` + local validation is the safest start.
- Do not put the API key on the robot. Use a backend proxy with rate limits.
- Turn off the provider's training/improvement options; confirm zero-retention and cross-border terms.

## 3. Anthropic Claude

```python
import json, os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
SYSTEM = open("system-prompt.txt", encoding="utf-8").read()
SYSTEM = (SYSTEM
    .replace("{{OUTPUT_MODE}}", "json")
    .replace("{{USER_PROFILE}}", "unknown")
    .replace("{{MEMORY}}", "none")
    .replace("{{ROBOT_STATE}}", "normal"))

msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=400,
    temperature=0.7,
    system=SYSTEM,
    messages=[{"role": "user", "content": "I have a presentation tomorrow and my heart is racing."}],
)
text = "".join(b.text for b in msg.content if b.type == "text")
data = json.loads(text)
```

Claude has no OpenAI-style `response_format`. Reliable approach: state "return JSON only" in the system prompt, prefill the assistant turn with `{`, and fall back to plain `say` if parsing fails.

## 4. Serial / WebSocket

Newline-delimited JSON, UTF-8:

```json
{"v":1,"type":"express","seq":42,"face":"concerned","led":{"preset":"warm_breath"},"voice":{"rate":0.92,"pause_before_ms":600},"display":{"icon":"heart","caption":"I'm here"},"ttl_ms":8000}
{"v":1,"type":"speak","seq":43,"text":"That sounds like a lot to carry alone. Which part hurts the most?","interruptible":true}
```

- Send `express` before `speak`; `seq` is monotonic; firmware drops stale frames.
- Heartbeat every 5s; after 3 misses, enter the local fallback.
- Safety mode: `{"type":"mode","value":"safety"}` keeps warm amber + 12356 on screen; it does not auto-exit.

## 5. Output validation

```python
def validate(data, risk_level):
    say = (data.get("say") or "").strip()
    if not say:
        raise ValueError("empty say")

    words = len(say.split())
    if words > 60:
        say = " ".join(say.split()[:60])

    for bad in (
        "just think positive", "don't overthink", "at least",
        "others have it worse", "it will all work out",
    ):
        if bad in say.lower():
            raise ValueError(f"forbidden: {bad}")

    if say.count("?") > (2 if risk_level in ("L2", "L3") else 1):
        raise ValueError("too many questions")

    data["say"] = say
    return data
```

On failure, fall back to:

```json
{"say":"I'm here. Take your time.","face":"concerned","led":{"preset":"warm_breath"},"risk":{"level":"L0"}}
```

The Chinese edition uses a character limit (80). English uses words; adjust the schema's `say.maxLength` if you use it for English.

## 6. Before launch

- [ ] Risk classifier recalls indirect expressions; L2/L3 recall ≥95%.
- [ ] Output schema, length, banned phrases, and question count are validated.
- [ ] Network/LLM/ASR/TTS failure paths are tested.
- [ ] L1/L2/L3 human and emergency escalation are reachable.
- [ ] Memory is viewable/deletable; third parties retain nothing and train on nothing.
