import React, { createContext, useContext, useState } from 'react';

export const SUPPORTED_LANGS = [
    { code: 'en', label: 'English' },
    { code: 'zh-TW', label: '繁體中文' },
    { code: 'zh-CN', label: '简体中文' },
    { code: 'ja', label: '日本語' },
    { code: 'ko', label: '한국어' },
    { code: 'de', label: 'Deutsch' },
    { code: 'es', label: 'Español' },
    { code: 'fr', label: 'Français' },
    { code: 'pt', label: 'Português' },
    { code: 'it', label: 'Italiano' },
    { code: 'nl', label: 'Nederlands' },
    { code: 'ar', label: 'العربية' },
];

interface LanguageContextType {
    lang: string;
    setLang: (lang: string) => void;
    supportedLangs: typeof SUPPORTED_LANGS;
}

const LanguageContext = createContext<LanguageContextType>({
    lang: 'zh-TW',
    setLang: () => {},
    supportedLangs: SUPPORTED_LANGS,
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    const [lang, setLangState] = useState<string>(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('pitlane_lang') || 'zh-TW';
        }
        return 'zh-TW';
    });

    const setLang = (newLang: string) => {
        setLangState(newLang);
        if (typeof window !== 'undefined') {
            localStorage.setItem('pitlane_lang', newLang);
        }
    };

    return (
        <LanguageContext.Provider value={{ lang, setLang, supportedLangs: SUPPORTED_LANGS }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    return useContext(LanguageContext);
}
