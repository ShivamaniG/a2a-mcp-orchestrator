import base64
from io import BytesIO

from fastmcp import FastMCP
from PyPDF2 import PdfReader

mcp = FastMCP("PDF Processing Tools")


@mcp.tool
def extract_pdf_text(base64_pdf: str) -> str:
    """Extract text from base64-encoded PDF."""
    try:
        pdf_bytes = base64.b64decode(base64_pdf)
        reader = PdfReader(BytesIO(pdf_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        return "".join(text_parts)[:4000]
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def summarize_pdf(pdf_text: str) -> str:
    """Summarize PDF text for demo purposes."""
    summary = (
        "PDF Summary:\n"
        f"- Length: {len(pdf_text)} chars\n"
        f"- First 200 chars: {pdf_text[:200]}...\n"
        "- Key topics: documents, analysis"
    )
    return summary


if __name__ == "__main__":
    print("MCP PDF Server running...")
    mcp.run()
