from pathlib import Path

from docx import Document
from pypdf import PdfReader

from apps.candidates.exceptions import CVParsingError


class CVParser:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    def parse(self, file):
        extension = Path(file.name).suffix.lower()

        if extension == ".pdf":
            return self._parse_pdf(file)

        if extension == ".docx":
            return self._parse_docx(file)

        raise CVParsingError(
            f"Unsupported CV format: {extension}",
        )

    def _parse_pdf(self, file):
        try:
            reader = PdfReader(file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise CVParsingError(
                "Unable to parse PDF file.",
            ) from exc

        return self._normalize_text(text)

    def _parse_docx(self, file):
        try:
            document = Document(file)
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        except Exception as exc:
            raise CVParsingError(
                "Unable to parse DOCX file.",
            ) from exc

        return self._normalize_text(text)

    def _normalize_text(self, text):
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())
