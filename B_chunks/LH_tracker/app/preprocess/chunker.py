from app.config import LH_SECTION_HINTS

def split_lines(text: str) -> list[str]:
    return [line.strip() for line in text.split("\n") if line.strip()]

def build_chunks(lines: list[str]) -> list[dict]:
    chunks = []
    current_section = "기타"
    current_text = []

    for line in lines:
        if line in LH_SECTION_HINTS:
            if current_text:
                chunks.append({
                    "section": current_section,
                    "text": " ".join(current_text).strip()
                })
                current_text = []
            current_section = line
        else:
            current_text.append(line)

    if current_text:
        chunks.append({
            "section": current_section,
            "text": " ".join(current_text).strip()
        })

    return chunks

def get_chunk_text(chunks: list[dict], section_name: str) -> str:
    for chunk in chunks:
        if chunk["section"] == section_name:
            return chunk["text"]
    return ""