import fitz  # PyMuPDF

def extract_text_and_chunks(file_bytes: bytes, chunk_size: int = 500) -> list:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_text = " ".join(words[i:i+chunk_size])
        chunks.append({"text": chunk_text})
    return chunks
