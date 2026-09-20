# apps/resumes/services.py

import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

MAX_EXTRACTED_CHARS = 20000


class ResumeService:

    @staticmethod
    def extract_text(resume) -> str:
        """
        Reads the uploaded PDF and stores its text in resume.extracted_text.
        Never raises: a resume with unreadable text (scanned image PDF) should
        still upload successfully, the AI just gets less context.
        """
        try:
            resume.file.open("rb")
            reader = PdfReader(resume.file)

            pages = [(page.extract_text() or "") for page in reader.pages]
            raw = "\n".join(pages)
            # Drop null bytes / control chars that PDFs often carry, collapse blank runs
            cleaned = "".join(ch for ch in raw if ch in "\n\t" or ord(ch) >= 32)
            text = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
            text = text[:MAX_EXTRACTED_CHARS]

            resume.extracted_text = text
            resume.save(update_fields=["extracted_text", "updated_at"])
            return text

        except Exception:
            logger.exception("Resume text extraction failed for resume id=%s", resume.id)
            return ""

        finally:
            try:
                resume.file.close()
            except Exception:
                pass