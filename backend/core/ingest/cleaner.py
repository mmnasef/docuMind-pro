import re
import unicodedata
import pyarabic.araby as araby


def normalize_arabic_numbers(text: str) -> str:
    arabic_nums = '٠١٢٣٤٥٦٧٨٩'
    for i, num in enumerate(arabic_nums):
        text = text.replace(num, str(i))
    return text


def remove_noise(text: str) -> str:
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F.,،؟?!]', ' ', text)
    return text


def detect_language(text: str) -> str:
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total = arabic_chars + english_chars
    if total == 0:
        return 'unknown'
    if arabic_chars / total > 0.5:
        return 'arabic'
    return 'english'


def remove_duplicates(text: str) -> str:
    lines = text.split('\n')
    seen = set()
    unique_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            unique_lines.append(line)
    return '\n'.join(unique_lines)


def clean_arabic_text(text: str) -> str:
    text = araby.strip_tashkeel(text)
    text = araby.normalize_hamza(text)
    text = araby.normalize_ligature(text)
    text = normalize_arabic_numbers(text)
    return text

def clean_text(text: str) -> str:
    text = unicodedata.normalize('NFC', text)
    text = remove_noise(text)
    language = detect_language(text)
    if language == 'arabic':
        text = clean_arabic_text(text)
    text = remove_duplicates(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text, language