


SEPARATORS_ARABIC = ["\n\n", "\n", ".", "،", "؟", "!", " "]
SEPARATORS_ENGLISH = ["\n\n", "\n", ".", "?", "!", " "]


def get_splitter(language: str, chunk_size: int, chunk_overlap: int):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    separators = SEPARATORS_ARABIC if language == 'arabic' else SEPARATORS_ENGLISH
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=len
    )

def chunk_documents(documents: list) -> list:
    all_chunks = []

    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]
        language = metadata.get("language", "english")

        parent_splitter = get_splitter(language, chunk_size=1024, chunk_overlap=100)
        child_splitter = get_splitter(language, chunk_size=256, chunk_overlap=30)

        parent_chunks = parent_splitter.split_text(text)

        for parent_idx, parent_text in enumerate(parent_chunks):
            child_chunks = child_splitter.split_text(parent_text)

            for child_idx, child_text in enumerate(child_chunks):
                if child_text.strip():
                    all_chunks.append({
                        "child_text": child_text,
                        "parent_text": parent_text,
                        "metadata": {
                            **metadata,
                            "parent_idx": parent_idx,
                            "child_idx": child_idx,
                            "language": language
                        }
                    })

    return all_chunks