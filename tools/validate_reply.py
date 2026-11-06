"""Validate a provider reply before passing it to the robot."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "assets" / "output.schema.json"
VALIDATOR = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


def reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON number")


def unique_fields(pairs: list[tuple]) -> dict:
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ValueError("Duplicate JSON field")
    return fields


def validate_reply(raw: str) -> dict:
    """Return a valid candidate reply. The caller still owns safety and playback."""
    if not isinstance(raw, str) or len(raw) > 8192:
        raise ValueError("Invalid reply size or type")
    try:
        reply = json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_fields)
        valid = VALIDATOR.is_valid(reply)
    except (ValueError, RecursionError):
        raise ValueError("Invalid reply JSON") from None
    if not valid:
        raise ValueError("Reply does not match Sunny's output schema")
    say = reply["say"].strip()
    if not say:
        raise ValueError("Empty speech")
    questions = say.count("?") + say.count("？")
    if questions > (2 if reply["risk"]["level"] != "L0" else 1):
        raise ValueError("Too many questions")
    reply["say"] = say
    return reply
