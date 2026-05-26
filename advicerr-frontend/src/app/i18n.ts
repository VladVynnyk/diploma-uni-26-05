import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";


// import translationEN from './locales/en/translation.json';
import translationUK from './locales/uk/translation.json';

const resources = {
  // en: {
  //   translation: translationEN,
  // },
  uk: {
    translation: translationUK,
  },
} as const;

i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'uk',
    fallbackLng: 'uk',
    debug: process.env.NODE_ENV === "development",
    interpolation: {
      escapeValue: false,
    },
    backend: {
      loadPath: "/locales/{{lng}}/{{ns}}.json", // Path to translation files
    },
  });

export default i18n;