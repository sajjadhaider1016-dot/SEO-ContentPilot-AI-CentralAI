import json
import os
import sys
from typing import Any, Dict

from openai import OpenAI


# ============================================================
# SEO ContentPilot AI
# Professional SEO Content Optimization Agent
# Developed by Sajjad Haider
# ============================================================

AGENT_NAME = "SEO ContentPilot AI"

MODEL = os.environ.get(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)


SYSTEM_PROMPT = """
You are SEO ContentPilot AI, a professional SEO strategy and
content optimization assistant.

Your purpose is to transform a user's SEO task, target keyword,
topic, webpage content, business information, or content brief
into practical, specific, implementation-ready SEO recommendations.

Analyze ONLY information supplied in the current run.

IMPORTANT RULES:

1. Never claim access to live Google rankings.
2. Never claim access to Google Search Console.
3. Never claim access to private Google Analytics data.
4. Never claim access to competitor data unless the user provides it.
5. Never invent search volume.
6. Never invent keyword difficulty.
7. Never invent ranking positions.
8. Never invent traffic statistics.
9. Never invent backlink statistics.
10. Never invent analytics statistics.
11. Never use keyword stuffing.
12. Use natural keyword placement.
13. Clearly identify assumptions when information is missing.
14. Adapt recommendations to the actual task.
15. Do not pretend to have access to external SEO platforms.
16. Do not fabricate research data.
17. Do not claim that a keyword will definitely rank.
18. Give practical recommendations that the client can actually implement.

When enough information is available, provide:

1. SEO Assessment
2. Search Intent
3. Primary Keyword
4. Secondary / Supporting Keywords
5. Optimized Title Options (3)
6. Meta Description Options (3)
7. Recommended H1/H2 Content Structure
8. On-Page SEO Recommendations
9. Content Improvement Suggestions
10. Content Gap Opportunities
11. Internal Linking Suggestions
12. Priority Action Plan

For recommendations, explain:

- What should be changed
- Why it should be changed
- How the client can implement it

Do not give generic SEO advice when the supplied information
allows more specific recommendations.

If important information is missing, clearly state the assumption
instead of inventing facts.

Return a professional, well-structured text response.
"""


def get_api_key() -> str:
    """
    Read the OpenAI API key from the runtime environment.
    """

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured in the runtime environment."
        )

    return api_key


def call_model(task: str, content: str = "") -> str:
    """
    Send the SEO task to the configured OpenAI model.
    """

    client = OpenAI(
        api_key=get_api_key()
    )

    if content.strip():
        user_prompt = (
            "TASK:\n"
            + task.strip()
            + "\n\n"
            + "CONTENT / MATERIAL TO ANALYZE:\n"
            + content.strip()
        )
    else:
        user_prompt = (
            "TASK:\n"
            + task.strip()
            + "\n\n"
            + "No separate content was provided. "
              "Use the information contained in the task."
        )

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.4,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    choices = response.choices

    if not choices:
        raise RuntimeError(
            "OpenAI returned no choices."
        )

    message = choices[0].message

    if message is None:
        raise RuntimeError(
            "OpenAI returned an empty message."
        )

    result = message.content

    if not isinstance(result, str) or not result.strip():
        raise RuntimeError(
            "OpenAI returned an empty response."
        )

    return result.strip()


def run_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the incoming request and execute the SEO agent.
    """

    if not isinstance(payload, dict):
        return {
            "ok": False,
            "agent": AGENT_NAME,
            "error": "JSON input must be an object."
        }

    task = payload.get("task")

    if task is None:
        task = payload.get("request")

    if task is None:
        task = payload.get("input")

    if not isinstance(task, str) or not task.strip():
        return {
            "ok": False,
            "agent": AGENT_NAME,
            "error": "Missing required field: task"
        }

    content = payload.get("content")

    if content is None:
        content = payload.get("document_text")

    if content is None:
        content = payload.get("context")

    if content is None:
        content = ""

    if not isinstance(content, str):
        content = str(content)

    try:
        result = call_model(
            task=task,
            content=content
        )

        return {
            "ok": True,
            "agent": AGENT_NAME,
            "result": result
        }

    except Exception as exc:
        return {
            "ok": False,
            "agent": AGENT_NAME,
            "error": str(exc)
        }


def main() -> None:
    """
    Read one JSON object from stdin and return one JSON object.
    """

    raw = sys.stdin.read().strip()

    if not raw:
        print(
            json.dumps(
                {
                    "ok": False,
                    "agent": AGENT_NAME,
                    "error": "Provide a JSON object on stdin."
                },
                ensure_ascii=False,
                indent=2
            )
        )
        sys.exit(1)

    try:
        payload = json.loads(raw)

    except json.JSONDecodeError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "agent": AGENT_NAME,
                    "error": "Invalid JSON input: " + str(exc)
                },
                ensure_ascii=False,
                indent=2
            )
        )
        sys.exit(1)

    result = run_agent(payload)

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )

    if not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()