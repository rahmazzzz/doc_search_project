import re

def is_arabic(text: str) -> bool:
    arabic_pattern = re.compile("[\u0600-\u06FF]")
    return bool(arabic_pattern.search(text))