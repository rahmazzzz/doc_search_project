def generate_arabic_prompt(question: str, file_content: str) -> str:
    return f"""
أنت مساعد ذكي. استخدم فقط محتوى الملف التالي للإجابة على السؤال.

محتوى الملف:
{file_content}

السؤال:
{question}

أجب باللغة العربية:
"""