import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex border rounded-md overflow-hidden shadow-sm">
      <button
        onClick={() => setLanguage('hu')}
        className={`p-1 transition-colors cursor-pointer flex items-center justify-center ${
          language === 'hu'
            ? 'bg-[#2657A7] text-white ring-1 ring-[#2657A7]'
            : 'bg-gray-50 text-gray-700 hover:bg-[#e7edf7]'
        }`}
        aria-label="Switch to Hungarian language"
        title="Magyar"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="24" 
          height="18" 
          viewBox="0 0 24 18" 
          className="w-6 h-4"
        >
          <rect width="24" height="6" fill="#CE2939" />
          <rect y="6" width="24" height="6" fill="#FFFFFF" />
          <rect y="12" width="24" height="6" fill="#477050" />
        </svg>
      </button>
      
      <button
        onClick={() => setLanguage('en')}
        className={`p-1 transition-colors cursor-pointer flex items-center justify-center ${
          language === 'en'
            ? 'bg-[#2657A7] text-white ring-1 ring-[#2657A7]'
            : 'bg-gray-50 text-gray-700 hover:bg-[#e7edf7]'
        }`}
        aria-label="Switch to English language"
        title="English"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="24" 
          height="18" 
          viewBox="0 0 24 18" 
          className="w-6 h-4"
        >
          <rect width="24" height="18" fill="#00247D" />
          <path d="M0 0 L24 18 M24 0 L0 18" stroke="#FFFFFF" strokeWidth="3" />
          <path d="M12 0 V18 M0 9 H24" stroke="#FFFFFF" strokeWidth="5" />
          <path d="M12 0 V18 M0 9 H24" stroke="#CF142B" strokeWidth="3" />
          <path d="M0 0 L24 18 M24 0 L0 18" stroke="#CF142B" strokeWidth="1" />
        </svg>
      </button>
    </div>
  );
};

export default LanguageSwitcher;