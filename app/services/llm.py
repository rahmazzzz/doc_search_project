import cohere
from app.core.config import settings

co = cohere.Client(settings.COHERE_API_KEY)

def call_llm(question: str, context: str) -> str:
    system_prompt = (
        "You are a helpful machine learning engineer. "
        "Answer using only the provided context."
    )
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    response = co.chat(
        model="command-r-plus",
        message=user_prompt,
        chat_history=[
            {"role": "SYSTEM", "message": system_prompt}
        ]
    )
    return response.text
