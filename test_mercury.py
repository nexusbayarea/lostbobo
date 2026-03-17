import os
import requests
import json


def test_mercury():
    api_key = os.getenv("MERCURY_API_KEY")
    if not api_key:
        print("Missing API key")
        return False

    url = "https://api.inceptionlabs.ai/v1/chat/completions"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": "mercury",
        "messages": [
            {"role": "user", "content": "Return EXACTLY the string SIMHPC_OK"}
        ],
        "temperature": 0,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)

        print("STATUS:", r.status_code)
        print("RAW TEXT:", r.text)

        data = r.json()

        print("\nPARSED JSON:")
        print(json.dumps(data, indent=2))

        # Flexible parsing
        content = None

        if "choices" in data:
            content = data["choices"][0].get("message", {}).get("content")

        elif "output" in data:
            content = data["output"]

        elif "text" in data:
            content = data["text"]

        if content:
            print("EXTRACTED:", content)

            if "SIMHPC_OK" in content:
                print("✅ SUCCESS")
                return True

        print("❌ FAILED: Could not validate response")
        return False

    except Exception as e:
        print("ERROR:", str(e))
        return False


if __name__ == "__main__":
    success = test_mercury()
    exit(0 if success else 1)
