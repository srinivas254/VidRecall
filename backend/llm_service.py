from pathlib import Path
from config import (
    client,
    LLM_MODEL
)


SYSTEM_PROMPT = Path("system_prompt.txt").read_text(encoding="utf-8")


def llm_call(context: str, question: str) -> str:

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.5,
        messages = [
            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content": f"""
                Context:
                {context}

                Question:
                {question}
                """
            }
        ]
    )

    return response.choices[0].message.content

