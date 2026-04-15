def map_chunks_to_schema(raw_result: dict) -> list[dict]:
    chunks = raw_result.get("chunks", [])
    policy_id = raw_result.get("policy_id")
    policy_name = raw_result.get("title")
    source_url = raw_result.get("url")

    mapped = []

    for idx, chunk in enumerate(chunks, start=1):
        mapped.append({
            "chunk_id": f"{policy_id}_{idx}",
            "policy_id": policy_id,
            "policy_name": policy_name,
            "issuing_org": "LH",
            "source_doc_name": policy_name,
            "source_url": source_url,
            "section_title": chunk.get("section"),
            "chunk_text": chunk.get("text"),
            "chunk_order": idx,
            "has_table": False,
            "doc_type": "web_page",
            "created_from": "section_chunking"
        })

    return mapped