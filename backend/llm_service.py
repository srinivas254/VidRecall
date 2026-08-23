from pathlib import Path

from config import (
    client,
    LLM_MODEL
)


SYSTEM_PROMPT = Path("system_prompt.txt").read_text(encoding="utf-8")


# Stores the previous 3 conversations
# 3 conversations = 3 user messages + 3 assistant messages = 6 messages
prev_messages = []


def llm_call(context: str, question: str) -> str:

    global prev_messages

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Add previous conversation history
    messages.extend(prev_messages)

    # Add current context and question
    messages.append(
        {
            "role": "user",
            "content": f"""
Context:
{context}

Question:
{question}
"""
        }
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.5,
        messages=messages
    )

    answer = response.choices[0].message.content

    # Store the current user question
    prev_messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Store the current assistant response
    prev_messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # Keep only the latest 3 conversations
    if len(prev_messages) > 6:
        prev_messages = prev_messages[-6:]

    return answer