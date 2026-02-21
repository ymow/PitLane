"""Article categorization based on content analysis with multi-language support."""
import re
from apps.news.models import NewsCategory as Category


class ArticleCategorizer:
    """
    Classify articles into categories based on multi-language content analysis.
    """

    # Localized patterns for major languages
    # Key: Category Slug, Value: Dict of Lang -> List of Regex
    LOCALIZED_PATTERNS = {
        'breaking': {
            'en': [r'\bBREAKING\b', r'\bJUST IN\b', r'\bOFFICIAL\b.*\bannounce', r'\bURGENT\b', r'\bALERT\b'],
            'it': [r'\bULTIM\'ORA\b', r'\bUFFICIALE\b', r'\bANNUNCIO\b', r'\bURGENTE\b'],
            'es': [r'\bULTIMA HORA\b', r'\bOFICIAL\b', r'\bANUNCIO\b', r'\bURGENTE\b', r'\bALERTA\b'],
            'fr': [r'\bDERNIÈRE MINUTE\b', r'\bOFFICIEL\b', r'\bURGENT\b', r'\bANNONCE\b'],
            'de': [r'\bEILMELDUNG\b', r'\bOFFIZIELL\b', r'\bDRINGEND\b', r'\bBEKANNTGABE\b'],
            'pt': [r'\bULTIMA HORA\b', r'\bOFICIAL\b', r'\bURGENTE\b', r'\bAVISO\b'],
            'nl': [r'\bLAATSTE NIEUWS\b', r'\bOFFICIEEL\b', r'\bURGENT\b'],
        },
        'race-reports': {
            'en': [r'\bwins?\b.*\bGP\b', r'\brace\s+report\b', r'\brace\s+result\b', r'\bvictory\b', r'\bfinishes?\b'],
            'it': [r'\bvince\b.*\bGP\b', r'\bvincitore\b', r'\bresoconto\s+gara\b', r'\brisultati?\s+gara\b', r'\btraguardo\b'],
            'es': [r'\bgana\b.*\bGP\b', r'\bvictoria\b', r'\bcrónica\s+carrera\b', r'\bresultados?\s+carrera\b', r'\btriunfo\b'],
            'fr': [r'\bvictoire\b', r'\bgagne\b', r'\brésumé\s+course\b', r'\brésultats?\s+course\b', r'\btriomphe\b'],
            'de': [r'\bsieg(t|er)?\b', r'\brennen\s+bericht\b', r'\bergebnis(se)?\s+rennen\b', r'\bgewinnt\b'],
            'pt': [r'\bvitória\b', r'\bganha\b', r'\brelatório\s+corrida\b', r'\bresultados?\s+corrida\b'],
            'nl': [r'\bwint\b', r'\boverwinning\b', r'\brace\s+verslag\b', r'\buitslagen?\b'],
        },
        'qualifying': {
            'en': [r'\bqualifying\b', r'\bpole\s+position\b', r'\bQ[123]\b', r'\bgrid\s+position\b', r'\bfront\s+row\b'],
            'it': [r'\bqualifiche\b', r'\bpole\s+position\b', r'\bgriglia\s+partenza\b', r'\bprima\s+fila\b'],
            'es': [r'\bclasificación\b', r'\bcalificación\b', r'\bparrilla\s+salida\b', r'\bprimera\s+fila\b'],
            'fr': [r'\bqualification\b', r'\bgrille\s+départ\b', r'\bpremier\s+rang\b'],
            'de': [r'\bqualifikation\b', r'\bqualifying\b', r'\bstartplatz\b', r'\berste\s+reihe\b'],
            'pt': [r'\bclassificação\b', r'\bqualificação\b', r'\bgrid\s+largada\b'],
            'nl': [r'\bkwalificatie\b', r'\bstartopstelling\b', r'\bpole\s+positie\b'],
        },
        'technical': {
            'en': [r'\bupgrade\b', r'\baero\b', r'\btechnical\b', r'\bpower\s+unit\b', r'\bengine\b', r'\bsetup\b', r'\bdevelopment\b'],
            'it': [r'\baggiornamento\b', r'\baerodinamica\b', r'\btecnico\b', r'\bunità\s+potenza\b', r'\bmotore\b', r'\bsviluppo\b'],
            'es': [r'\bmejora\b', r'\baerodinámica\b', r'\btécnico\b', r'\bunidad\s+potencia\b', r'\bmotor\b', r'\bdesarrollo\b'],
            'fr': [r'\bamélioration\b', r'\baérodynamique\b', r'\btechnique\b', r'\bunité\s+puissance\b', r'\bmoteur\b'],
            'de': [r'\bupgrade\b', r'\baerodynamik\b', r'\btechnisch\b', r'\bantriebseinheit\b', r'\bmotor\b', r'\bentwicklung\b'],
            'pt': [r'\bmelhoria\b', r'\baerodinâmica\b', r'\btécnico\b', r'\bunidade\s+potência\b', r'\bmotor\b'],
            'nl': [r'\bupgrade\b', r'\baerodynamica\b', r'\btechnisch\b', r'\bkrachtbron\b', r'\bmotor\b'],
        },
        'transfers': {
            'en': [r'\bsign(s|ed|ing)?\b', r'\bcontract\b', r'\btransfer\b', r'\bmove(s|d)?\s+to\b', r'\bjoin(s|ed)?\b'],
            'it': [r'\bfirma\b', r'\bcontratto\b', r'\btrasferimento\b', r'\bsi\s+unisce\b', r'\baccordo\b'],
            'es': [r'\bfirma\b', r'\bcontrato\b', r'\btransferencia\b', r'\bse\s+une\b', r'\bacuerdo\b'],
            'fr': [r'\bsigne\b', r'\bcontrat\b', r'\btransfert\b', r'\brejoint\b', r'\baccord\b'],
            'de': [r'\bunterzeichnet\b', r'\bvertrag\b', r'\btransfer\b', r'\bwechselt\b', r'\bvereinbarung\b'],
            'pt': [r'\bassina\b', r'\bcontrato\b', r'\btransferência\b', r'\bjunta-se\b', r'\bacordo\b'],
            'nl': [r'\btekent\b', r'\bcontract\b', r'\btransfer\b', r'\bsluit\s+aan\b', r'\bovereenkomst\b'],
        },
        'penalties': {
            'en': [r'\bpenalt(y|ies)\b', r'\bstewards\b', r'\binvestigation\b', r'\bdisqualif\w+\b', r'\btime\s+penalty\b'],
            'it': [r'\bpenalit(à|y)\b', r'\bcommissari\b', r'\bindagine\b', r'\bsqualific\w+\b'],
            'es': [r'\bpenalit(y|ies)\b', r'\bcomisarios\b', r'\binvestigación\b', r'\bdescalific\w+\b'],
            'fr': [r'\bpénalit(é|y)\b', r'\bcommissaires\b', r'\benquête\b', r'\bdisqualific\w+\b'],
            'de': [r'\bstrafe\b', r'\brennkommissare\b', r'\buntersuchung\b', r'\bdisqualifik\w+\b'],
            'pt': [r'\bpenalidad(e|es)\b', r'\bcomissários\b', r'\binvestigação\b', r'\bdesqualific\w+\b'],
            'nl': [r'\bstraf\b', r'\bstewards\b', r'\bonderzoek\b', r'\bdiskwalific\w+\b'],
        }
    }

    # Universal Priority patterns (often high-impact words are similar or English is used)
    PRIORITY_PATTERNS = {
        'CRITICAL': [r'\bBREAKING\b', r'\bOFFICIAL\b', r'\bUFFICIALE\b', r'\bOFICIAL\b', r'\bDEATH\b'],
        'HIGH': [r'\bwins?\b.*\bGP\b', r'\bpole\b', r'\bcrash\b', r'\bcontract\b'],
    }

    def categorize(self, title: str, body: str, lang: str = 'en') -> str:
        """Determine article category based on language-specific patterns."""
        full_text = f"{title} {body}".upper()

        # Try localized patterns first
        for cat_slug, lang_map in self.LOCALIZED_PATTERNS.items():
            # Get patterns for specific lang, fallback to 'en'
            patterns = lang_map.get(lang, lang_map.get('en', []))
            
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    # Find category object by slug
                    try:
                        cat = Category.objects.get(slug=cat_slug)
                        return cat
                    except Category.DoesNotExist:
                        continue

        # Default fallback: 'news' category, then first active category
        try:
            return Category.objects.get(slug='news')
        except Category.DoesNotExist:
            return Category.objects.filter(is_active=True).order_by('display_order').first()

    def prioritize(self, title: str, body: str) -> str:
        """Determine article priority (Universal)."""
        full_text = f"{title} {body}".upper()

        for priority, patterns in self.PRIORITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    return priority

        return 'NORMAL'
