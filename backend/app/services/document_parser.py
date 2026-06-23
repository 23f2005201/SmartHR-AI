import io
from pypdf import PdfReader
from docx import Document

class DocumentParserService:
    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        """Extracts text content from PDF or DOCX file streams in memory."""
        extension = filename.split(".")[-1].lower()
        extracted_text = ""

        try:
            if extension == "pdf":
                pdf_stream = io.BytesIO(file_bytes)
                reader = PdfReader(pdf_stream)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
                        
            elif extension in ["docx", "doc"]:
                docx_stream = io.BytesIO(file_bytes)
                doc = Document(docx_stream)
                for paragraph in doc.paragraphs:
                    if paragraph.text:
                        extracted_text += paragraph.text + "\n"
            else:
                raise ValueError(f"Unsupported file extension: .{extension}")

            return extracted_text.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to parse document string stream: {str(e)}")

document_parser = DocumentParserService()