
import sys
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("pypdf not found")
        sys.exit(1)

reader = PdfReader("icf-cs-pcc-markers-2021.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"
print(text)
