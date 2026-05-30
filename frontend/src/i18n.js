import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import en from "./i18n/en.json";
import mr from "./i18n/mr.json";
import hi from "./i18n/hi.json";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: { en: { translation: en }, mr: { translation: mr }, hi: { translation: hi } },
    fallbackLng: "en",
    interpolation: { escapeValue: false },
  });

export default i18n;
