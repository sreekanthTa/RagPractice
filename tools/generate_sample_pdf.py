from __future__ import annotations

from pathlib import Path
import textwrap


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample_rag_chromadb.pdf"


TITLE = "RAG Knowledge Base: ChromaDB PDF Sample"
PARAGRAPHS = [
    "Retrieval augmented generation, usually called RAG, helps an application answer questions by searching a trusted knowledge base before producing a response. Instead of asking a language model to rely only on its training data, the application retrieves relevant context and sends that context with the user's question.",
    "A typical PDF ingestion pipeline has four steps. First, the document loader extracts readable text from each PDF page. Second, the text splitter breaks long page text into smaller overlapping chunks. Third, an embedding model converts every chunk into a numeric vector. Fourth, ChromaDB stores the vectors, the original chunk text, and metadata such as source file, page number, and chunk id.",
    "Chunk size matters because it controls how much context each retrieved result contains. Chunks that are too small may lose important details. Chunks that are too large may mix unrelated topics and reduce retrieval quality. A common starting point is 500 to 1,000 characters with 50 to 150 characters of overlap.",
    "Metadata makes the vector database easier to use. For PDF content, useful metadata includes document name, page number, section title, creation date, and data owner. When the application returns an answer, metadata can be used to show citations so the user can verify where the information came from.",
    "ChromaDB can run locally for development and persist data to a folder on disk. A collection is similar to a table for embeddings. Each collection contains ids, documents, embeddings, and optional metadata. During a query, ChromaDB embeds the search text, compares it with stored vectors, and returns the nearest chunks.",
    "This sample document is intentionally small but realistic. It contains enough information to test PDF loading, text chunking, embedding creation, persistence, and similarity search. A good first query after ingestion is: What metadata should I store for PDF chunks?",
]


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_content_stream() -> bytes:
    lines = ["BT", "/F1 20 Tf", "72 735 Td", f"({escape_pdf_text(TITLE)}) Tj"]
    y_gap = 24

    lines.extend(["/F1 11 Tf", f"0 -{y_gap + 12} Td"])
    for paragraph in PARAGRAPHS:
        for wrapped in textwrap.wrap(paragraph, width=88):
            lines.append(f"({escape_pdf_text(wrapped)}) Tj")
            lines.append("0 -15 Td")
        lines.append("0 -9 Td")

    lines.append("ET")
    return ("\n".join(lines) + "\n").encode("ascii")


def pdf_object(number: int, body: bytes) -> bytes:
    return b"%d 0 obj\n" % number + body + b"\nendobj\n"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    stream = build_content_stream()

    objects = [
        pdf_object(1, b"<< /Type /Catalog /Pages 2 0 R >>"),
        pdf_object(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
        pdf_object(
            3,
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        ),
        pdf_object(4, b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"endstream"),
        pdf_object(5, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"),
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_offset = len(pdf)
    pdf.extend(b"xref\n0 6\n")
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        b"trailer\n<< /Root 1 0 R /Size 6 >>\n"
        + b"startxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )

    OUT.write_bytes(pdf)
    print(f"Generated {OUT}")


if __name__ == "__main__":
    main()
