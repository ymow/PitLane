"""Article categorization based on content analysis."""
import re
from apps.news.models import Category


class ArticleCategorizer:
    """
    Classify articles into categories based on content analysis.
    """

    CATEGORY_PATTERNS = {
        Category.BREAKING: [
            r'\bBREAKING\b',
            r'\bJUST IN\b',
            r'\bOFFICIAL\b.*\bannounce',
            r'\bconfirm(ed|s)?\b.*\b(sign|join|leave)',
        ],
        Category.RACE_REPORT: [
            r'\bwins?\b.*\b(GP|Grand Prix)\b',
            r'\brace\s+report\b',
            r'\brace\s+result\b',
            r'\bfinish(ed|es)?\b.*\b(first|second|third|P[1-9])\b',
        ],
        Category.QUALIFYING: [
            r'\bqualifying\b',
            r'\bpole\s+position\b',
            r'\bQ[123]\b',
            r'\bqualified\b',
        ],
        Category.PRACTICE: [
            r'\bFP[123]\b',
            r'\bfree\s+practice\b',
            r'\bpractice\s+session\b',
        ],
        Category.TECHNICAL: [
            r'\bupgrade\b',
            r'\baero(dynamic)?\b',
            r'\bfloor\b.*\b(change|update|new)\b',
            r'\bPU\b|\bpower\s+unit\b',
            r'\btechnical\s+directive\b',
        ],
        Category.TRANSFER: [
            r'\bsign(s|ed|ing)?\b.*\b(contract|deal)\b',
            r'\bjoin(s|ed|ing)?\b.*\b(team)\b',
            r'\bleav(e|es|ing)\b.*\b(team)\b',
            r'\breplac(e|es|ing)\b',
            r'\b(driver|seat)\s+market\b',
        ],
        Category.OPINION: [
            r'\bcolumn\b',
            r'\banalysis\b',
            r'\bopinion\b',
            r'\bexplained\b',
        ],
    }

    PRIORITY_PATTERNS = {
        'CRITICAL': [
            r'\bBREAKING\b',
            r'\bOFFICIAL\b',
            r'\bDEATH\b',
            r'\bDISQUALIF',
        ],
        'HIGH': [
            r'\bwins?\b.*\bGP\b',
            r'\bpole\b',
            r'\bcrash\b',
            r'\bcontract\b',
        ],
    }

    def categorize(self, title: str, body: str) -> str:
        """Determine article category."""
        full_text = f"{title} {body}"

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    return category

        return Category.NEWS

    def prioritize(self, title: str, body: str) -> str:
        """Determine article priority."""
        full_text = f"{title} {body}"

        for priority, patterns in self.PRIORITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    return priority

        return 'NORMAL'
