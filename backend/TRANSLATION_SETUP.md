# Translation Architecture: Claude AI & DB-Driven UI

## 1. Dynamic Content (Claude AI)
- **Engine**: Claude 3.5 Sonnet.
- **Specialization**: Preserves F1 technical terms (e.g., DRS, MGU-K, Porpoising).
- **Storage**: Multi-language `Translation` model linked to `Article`.
- **Target Languages**: English, Traditional Chinese (zh-TW), Simplified Chinese (zh-CN), Spanish, Portuguese, etc.

## 2. Dynamic UI (Database-Driven)
- **Categories**: Category names are now stored in `NewsCategoryTranslation` (No longer static YAML).
- **Tags**: Automated translation of entity tags.

## 3. Static UI (python-i18n)
- Only used for fixed interface elements (Buttons, Nav, Loading states).
