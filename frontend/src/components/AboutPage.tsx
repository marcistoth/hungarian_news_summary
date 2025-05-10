import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';


const AboutPage: React.FC = () => {

  const { t } = useLanguage();


  return (
    <div className="max-w-3xl mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6 bg-gradient-to-r from-primary to-primary-dark bg-clip-text text-transparent">
        {t('about.title')}
      </h1>
      
      <section className="mb-10 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-primary-dark">{t('about.whatIsTitle')}</h2>
        <p className="mb-4">
          {t('about.whatIsParagraph1')}
        </p>
        <p>
          {t('about.whatIsParagraph2')}
        </p>
      </section>
      
      <section className="mb-10 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-primary-dark">{t('about.howWorksTitle')}</h2>
        <p className="mb-4">
          {t('about.howWorksParagraph1')}
        </p>
        <p className="mb-4">
          {t('about.howWorksParagraph2')}
        </p>
        <p>
          {t('about.howWorksParagraph3')}
        </p>
      </section>

      <section className="mb-10 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-primary-dark">{t('about.technologyTitle')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-xl font-medium mb-2 text-primary">{t('about.frontendTitle')}</h3>
            <ul className="list-disc list-inside space-y-1">
              <li>React + TypeScript</li>
              <li>Tailwind CSS</li>
              <li>Vite build tool</li>
            </ul>
          </div>
          <div>
            <h3 className="text-xl font-medium mb-2 text-primary">{t('about.backendTitle')}</h3>
            <ul className="list-disc list-inside space-y-1">
              <li>FastAPI (Python)</li>
              <li>PostgreSQL (Neon.tech)</li>
              <li>Google Gemini AI</li>
              <li>Beautiful Soup (web scraping)</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-primary-dark">{t('about.creatorTitle')}</h2>
        <p className="mb-2">
          {t('about.creatorDescription')}
        </p>
        <div className="flex space-x-4 mt-4">
          <a href="https://github.com/marcistoth" target="_blank" rel="noopener noreferrer" className="flex items-center text-primary hover:text-primary-dark">
            <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
            </svg>
            GitHub
          </a>
          <a href="https://linkedin.com/in/marcellstoth" target="_blank" rel="noopener noreferrer" className="flex items-center text-primary hover:text-primary-dark">
            <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
            </svg>
            LinkedIn
          </a>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;