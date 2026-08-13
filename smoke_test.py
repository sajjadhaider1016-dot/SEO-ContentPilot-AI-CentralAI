import os
import sys
import json

print("IMPORT TEST", end=" ")

try:
    import agent
    print("OK")
except Exception as exc:
    print("FAILED")
    print(f"Import error: {exc}")
    sys.exit(1)


print("LOCAL EXECUTION TEST", end=" ")

# Do not require a personal API key for local package validation.
# Central AI supplies the OpenAI credential at runtime.
if not os.getenv("OPENAI_API_KEY"):
    print("SKIPPED: OPENAI_API_KEY is not set.")
    print("PACKAGE VALIDATION OK")
    sys.exit(0)


print("OPENAI_API_KEY detected")
print("API SMOKE TEST", end=" ")

try:
    result = agent.run_agent(
        {
            "task": "Give three SEO title ideas for a blog about AI productivity tools."
        }
    )

    if not isinstance(result, dict):
        print("FAILED")
        print("Agent did not return a JSON object.")
        sys.exit(1)

    if not result.get("ok"):
        print("FAILED")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    if not isinstance(result.get("result"), str):
        print("FAILED")
        print("Agent result is not text.")
        sys.exit(1)

    print("OK")
    print("API SMOKE TEST PASSED")

except Exception as exc:
    print("FAILED")
    print(f"Error: {exc}")
    sys.exit(1)