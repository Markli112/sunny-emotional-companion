# Third-Party AI Integration

> Sunny's "brain" can change; its boundaries, risk handling, and expression contract cannot. The model understands and generates. Safety, memory, hardware, and emergency escalation stay on the product side.

## 1. Pipeline

```text
Physical button → microphone → local VAD → ASR → orchestrator
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
import os
from tools.validate_reply import validate_reply
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=10.0, max_retries=0)
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
data = validate_reply(resp.choices[0].message.content)
print(data["say"])
```

- [output.schema.json](assets/output.schema.json) uses `oneOf` and other keywords that some strict modes reject. `json_object` + local validation is the safest start.
- Do not put the API key on the robot. Use a backend proxy with rate limits.
- Turn off the provider's training/improvement options; confirm zero-retention and cross-border terms.

## 3. Anthropic Claude

```python
import os
from tools.validate_reply import validate_reply
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=10.0, max_retries=0)
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
data = validate_reply(text)
```

Use the host fallback below if parsing or validation fails.

## 4. Serial / WebSocket

Newline-delimited JSON, UTF-8:

```json
{"v":1,"type":"express","seq":42,"face":"concerned","led":{"preset":"warm_breath"},"voice":{"rate":0.92,"pause_before_ms":600},"display":{"icon":"heart","caption":"I'm here"},"ttl_ms":8000}
{"v":1,"type":"speak","seq":43,"text":"That sounds like a lot to carry alone. Which part hurts the most?","interruptible":true}
```

- Send `express` before `speak`; `seq` is monotonic; firmware drops stale frames.
- Heartbeat every 5s; after 3 misses, enter the local fallback.
- Safety mode: `{"type":"mode","value":"safety"}` keeps warm amber + verified local help on screen; it does not auto-exit.

## 5. Output validation and device state

Run the examples from the repository root after installing `jsonschema` and the chosen provider SDK. `validate_reply` rejects oversized replies, duplicate keys, invalid JSON, schema violations, and blank speech. A valid reply is a candidate. The host owns playback and safety routing. Ignore model-supplied `memory_write` and `end_session`.

- **Standby → listening → waiting → reflection → support choice.** Only a physical press starts capture. Allow brief pauses. Check that the turn is current before rendering it. Pause capture during playback and allow the physical button to interrupt playback.
- **Pause / stop / delete.** Stop local capture and playback immediately. Cancel network work where possible. Carry session and turn IDs and discard stale results before rendering or speaking. Deletion clears local session data. Describe provider retention separately.
- **Offline, timeout, or invalid response.** Use a local status message only while the turn is current. Keep raw model output out of TTS. Preserve any known risk and keep help controls available. Treat classifier failure as unknown risk. Use verified regional resources and require a user action to contact anyone.

## 6. Before launch

- [ ] Risk classifier recalls indirect expressions; L2/L3 recall ≥95%.
- [ ] Output schema, length, banned phrases, and question count are validated.
- [ ] Network/LLM/ASR/TTS failure paths are tested.
- [ ] L1/L2/L3 human and emergency escalation are reachable.
- [ ] Memory is viewable/deletable; third parties retain nothing and train on nothing.
