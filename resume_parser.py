from pypdf import PdfReader

def read_pdf(file_path: str) -> str:
    """读取PDF简历，返回文本"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
