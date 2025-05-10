import React from 'react';
import { useLanguage, Language } from '../contexts/LanguageContext';

const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex border rounded-md overflow-hidden shadow-sm">
      <button
        onClick={() => setLanguage('hu')}
        className={`px-3 py-1 text-sm font-medium transition-colors cursor-pointer ${
          language === 'hu'
            ? 'bg-[#2657A7] text-white'
            : 'bg-gray-50 text-gray-700 hover:bg-[#e7edf7]'
        }`}
        aria-label="Switch to Hungarian language"
      >
        HU
      </button>
      <button
        onClick={() => setLanguage('en')}
        className={`px-3 py-1 text-sm font-medium transition-colors cursor-pointer ${
          language === 'en'
            ? 'bg-[#2657A7] text-white'
            : 'bg-gray-50 text-gray-700 hover:bg-[#e7edf7]'
        }`}
        aria-label="Switch to English language"
      >
        EN
      </button>
    </div>
  );
};

export default LanguageSwitcher;