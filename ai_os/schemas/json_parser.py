# ai_os/schemas/json_parser.py

import json


def extract_json(text: str) -> dict:
    """
    Extracts JSON even if surrounded by extra text.
    """
    print("\n[JSON PARSER] Raw text received:")
    print(text)

    # find JSON inside text
    brace_count = 0
    json_start = None

    for i, char in enumerate(text):
        if char == "{":
            if brace_count == 0:
                json_start = i
            brace_count += 1

        elif char == "}":
            brace_count -= 1
            if brace_count == 0 and json_start is not None:
                candidate = text[json_start:i+1]
                print("\n[JSON PARSER] Candidate found:")
                print(candidate)

                try:
                    parsed = json.loads(candidate)
                    print("[JSON PARSER] Successfully parsed first JSON block.")
                    return parsed
                except Exception as e:
                    print("[JSON PARSER] Failed parsing candidate:", e)

    print("[JSON PARSER] No valid JSON found. Falling back to chat.")

    return {
        "action": "chat",
        "response": text
    }