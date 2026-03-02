import React, { createContext, useContext, useState, useEffect } from 'react';

export const SUPPORTED_LANGUAGES = [
    { code: 'zh-TW', label: '繁體中文' },
    { code: 'en',    label: 'English' },
    { code: 'ja',    label: '日本語' },
    { code: 'zh-CN', label: '简体中文' },
    { code: 'es',    label: 'Español' },
    { code: 'de',    label: 'Deutsch' },
    { code: 'fr',    label: 'Français' },
    { code: 'it',    label: 'Italiano' },
    { code: 'nl',    label: 'Nederlands' },
    { code: 'pt-BR', label: 'Português' },
] as const;

export type LangCode = typeof SUPPORTED_LANGUAGES[number]['code'];

const STORAGE_KEY = 'pitlane_lang';
const DEFAULT_LANG: LangCode = 'zh-TW';

interface LanguageContextValue {
    lang: LangCode;
    setLang: (lang: LangCode) => void;
}

const LanguageContext = createContext<LanguageContextValue>({
    lang: DEFAULT_LANG,
    setLang: () => {},
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    // Start with DEFAULT_LANG to avoid SSR hydration mismatch.
    // Client reads localStorage in useEffect after mount.
    const [lang, setLangState] = useState<LangCode>(DEFAULT_LANG);

    useEffect(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored && SUPPORTED_LANGUAGES.some(l => l.code === stored)) {
            setLangState(stored as LangCode);
        }
    }, []);

    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, lang);
    }, [lang]);

    return (
        <LanguageContext.Provider value={{ lang, setLang: setLangState }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage(): LanguageContextValue {
    return useContext(LanguageContext);
}
