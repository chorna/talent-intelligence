import re


class CandidateDataExtractor:
    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    )

    PHONE_PATTERN = re.compile(
        r"(?:\+?\d[\d\s().-]{7,}\d)",
    )

    LINKEDIN_PATTERN = re.compile(
        r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9._-]+",
        re.IGNORECASE,
    )

    GITHUB_PATTERN = re.compile(
        r"https?://(?:www\.)?github\.com/[A-Za-z0-9._-]+",
        re.IGNORECASE,
    )

    def extract(self, text):
        if not text or not text.strip():
            return self._empty_result()

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        return {
            "first_name": self._extract_first_name(lines),
            "last_name": self._extract_last_name(lines),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "linkedin_url": self._extract_linkedin(text),
            "github_url": self._extract_github(text),
            "headline": self._extract_headline(lines),
            "summary": self._extract_summary(lines),
        }

    def _extract_first_name(self, lines):
        name = self._extract_name(lines)

        if not name:
            return ""

        return name.split()[0]

    def _extract_last_name(self, lines):
        name = self._extract_name(lines)

        if not name:
            return ""

        parts = name.split()

        return " ".join(parts[1:])

    def _extract_name(self, lines):
        for line in lines[:5]:
            if (
                "@" not in line
                and not line.startswith(("http://", "https://"))
                and not self.PHONE_PATTERN.fullmatch(line)
                and len(line.split()) in (2, 3)
            ):
                return line

        return ""

    def _extract_email(self, text):
        match = self.EMAIL_PATTERN.search(text)

        return match.group(0) if match else ""

    def _extract_phone(self, text):
        match = self.PHONE_PATTERN.search(text)

        return match.group(0).strip() if match else ""

    def _extract_linkedin(self, text):
        match = self.LINKEDIN_PATTERN.search(text)

        return match.group(0) if match else ""

    def _extract_github(self, text):
        match = self.GITHUB_PATTERN.search(text)

        return match.group(0) if match else ""

    def _extract_headline(self, lines):
        name = self._extract_name(lines)

        if not name:
            return ""

        try:
            index = lines.index(name)
        except ValueError:
            return ""

        if index + 1 < len(lines):
            return lines[index + 1]

        return ""

    def _extract_summary(self, lines):
        summary_markers = {
            "summary",
            "profile",
            "professional summary",
            "about",
            "about me",
        }

        for index, line in enumerate(lines):
            normalized = line.rstrip(":").strip().lower()

            if normalized in summary_markers:
                summary_lines = []

                for next_line in lines[index + 1 :]:
                    if self._is_section_heading(next_line):
                        break

                    summary_lines.append(next_line)

                return " ".join(summary_lines)

        return ""

    def _is_section_heading(self, line):
        normalized = line.rstrip(":").strip().lower()

        return normalized in {
            "experience",
            "work experience",
            "employment",
            "education",
            "skills",
            "technical skills",
            "projects",
            "certifications",
        }

    def _empty_result(self):
        return {
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": "",
            "linkedin_url": "",
            "github_url": "",
            "headline": "",
            "summary": "",
        }
