def generate_english_prompt(question: str, file_content: str) -> str:
    return f"""
You are an assistant. Use ONLY the following file content to answer the question.

File content:
{file_content}

Question:
{question}

Answer in English:
"""
