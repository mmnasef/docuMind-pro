import fitz
import requests
from docx import Document
from bs4 import BeautifulSoup
from backend.core.ingest.cleaner import clean_text


def load_pdf(filepath: str) -> list:
    documents = []
    doc = fitz.open(filepath)
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            cleaned, language = clean_text(text)
            documents.append({
                "text": cleaned,
                "metadata": {
                    "source": filepath,
                    "page": page_num + 1,
                    "language": language,
                    "type": "pdf"
                }
            })
    return documents


def load_docx(filepath: str) -> list:
    documents = []
    doc = Document(filepath)
    full_text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    if full_text:
        cleaned, language = clean_text(full_text)
        documents.append({
            "text": cleaned,
            "metadata": {
                "source": filepath,
                "page": 1,
                "language": language,
                "type": "docx"
            }
        })
    return documents


def load_txt(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    if text.strip():
        cleaned, language = clean_text(text)
        return [{
            "text": cleaned,
            "metadata": {
                "source": filepath,
                "page": 1,
                "language": language,
                "type": "txt"
            }
        }]
    return []


def load_url(url: str) -> list:
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()
    text = soup.get_text(separator='\n')
    if text.strip():
        cleaned, language = clean_text(text)
        return [{
            "text": cleaned,
            "metadata": {
                "source": url,
                "page": 1,
                "language": language,
                "type": "url"
            }
        }]
    return []


def load_file(source: str) -> list:
    if source.startswith('http'):
        return load_url(source)
    elif source.endswith('.pdf'):
        return load_pdf(source)
    elif source.endswith('.docx'):
        return load_docx(source)
    elif source.endswith('.txt'):
        return load_txt(source)
    else:
        raise ValueError(f"Unsupported file type: {source}")