
import sys
from pypdf import PdfReader

def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

if __name__ == "__main__":
    files = [
        "c:\\Demandas\\Contas-a-pagar-e-receber\\Projeto.pdf",
        "c:\\Demandas\\Contas-a-pagar-e-receber\\Projeto Físico.pdf"
    ]
    for f in files:
        print(f"--- CONTENT OF {f} ---")
        print(extract_text(f))
        print("\n\n")
