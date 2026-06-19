from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx


def validate_response_shape(payload: dict) -> list[str]:
    errors: list[str] = []
    required = {"reply", "recommendations", "end_of_conversation"}
    missing = required - payload.keys()
    if missing:
        errors.append(f"Missing keys: {sorted(missing)}")
        return errors

    recs = payload.get("recommendations")
    if not isinstance(recs, list):
        errors.append("recommendations is not a list")
    else:
        if len(recs) not in (0,) and not (1 <= len(recs) <= 10):
            errors.append("recommendations length must be 0 or 1..10")
        for rec in recs:
            for key in ("name", "url", "test_type"):
                if key not in rec:
                    errors.append(f"recommendation missing '{key}'")
            if "url" in rec and not str(rec["url"]).startswith("https://www.shl.com/"):
                errors.append(f"non-SHL URL found: {rec['url']}")
    return errors


def run_eval(trace_file: Path, base_url: str) -> int:
    traces = json.loads(trace_file.read_text(encoding="utf-8"))
    failures = 0
    with httpx.Client(timeout=30.0) as client:
        for i, trace in enumerate(traces, start=1):
            messages = trace["messages"]
            response = client.post(f"{base_url}/chat", json={"messages": messages})
            if response.status_code != 200:
                failures += 1
                print(f"[trace {i}] non-200: {response.status_code}")
                continue
            payload = response.json()
            errors = validate_response_shape(payload)
            if errors:
                failures += 1
                print(f"[trace {i}] shape errors: {'; '.join(errors)}")
            else:
                print(f"[trace {i}] ok")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-file", required=True, type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    failures = run_eval(args.trace_file, args.base_url)
    if failures:
        raise SystemExit(1)
    print("All traces passed shape checks.")


if __name__ == "__main__":
    main()

