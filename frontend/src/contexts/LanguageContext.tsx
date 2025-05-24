import React, { createContext, useState, useContext} from 'react';

// Define available languages
export type Language = 'hu' | 'en';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

// Create the context
const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Create translation dictionary
const translations: Record<Language, Record<string, string>> = {
  hu: {
    // Navigation
    'nav.home': 'Főoldal',
    'nav.analysis': 'Elemzés',
    'nav.about': 'A Projektről',
    
    // Homepage
    'home.title': 'Magyar Hírek Összefoglaló',
    'home.loading': 'Összefoglalók betöltése...',
    'home.error': 'Hoppá! Hiba történt:',
    'home.noSummaries': 'Jelenleg nincsenek elérhető összefoglalók erre a napra. Nézz vissza később!',
    'home.readMore': 'Teljes összefoglaló',
    'home.serverNotice': 'Olyan szervert használunk aminek a betöltése több időt vehet igénybe. Kérjük, maradj az oldalon, hamarosan betölt az alkalmazás.',
    
    // Analysis page
    'analysis.title': 'Hírforrások Összehasonlító Elemzése',
    'analysis.loading': 'Elemzés betöltése...',
    'analysis.error': 'Hoppá! Hiba történt:',
    'analysis.topicsComparison': 'téma összehasonlítása',
    'analysis.differentSources': 'különböző hírforrásból',
    'analysis.noAnalysis': 'Erre a napra nem találtunk elemzést a témákról.',
    'analysis.detailedAnalysis': 'Részletes elemzés',
    'analysis.sentiment': 'Hangvétel',
    'analysis.positive': 'Pozitív',
    'analysis.neutral': 'Semleges',
    'analysis.negative': 'Negatív',
    'analysis.filterBySource': 'Szűrés hírforrás szerint:',
    'analysis.showAll': 'Összes mutatása',
    'analysis.topicsShowing': 'téma mutatása',
    'analysis.selectedSources': 'kiválasztott forrásból',
    'analysis.noMatchingTopics': 'A kiválasztott forrásokkal nincs találat.',

    // Sentiment and Political Leaning
    'sentiment.pozitív': 'Pozitív',
    'sentiment.semleges': 'Semleges',
    'sentiment.negatív': 'Negatív',
    'leaning.bal': 'Bal',
    'leaning.baloldali': 'Baloldali',
    'leaning.közép-bal': 'Közép-bal',
    'leaning.közép': 'Közép',
    'leaning.független': 'Független',
    'leaning.közép-jobb': 'Közép-jobb',
    'leaning.jobb': 'Jobb',
    'leaning.jobboldali': 'Jobboldali',
    
    // Dashboard
    'dashboard.title': 'Hírhangulati Elemzés',
    'dashboard.overallSentiment': 'Összes média hangvétele',
    'dashboard.bySource': 'Médiaforrásonként',
    'dashboard.politicalLeaning': 'Politikai beállítottság',
    'dashboard.topics': 'téma',
    'dashboard.left': 'Bal',
    'dashboard.centerLeft': 'Közép-bal',
    'dashboard.center': 'Közép',
    'dashboard.centerRight': 'Közép-jobb',
    'dashboard.right': 'Jobb',
    
    // Topic Modal
    'topic.sourcesCoverage': 'Hírforrások tudósítása',
    'topic.originalTopic': 'Eredeti téma',
    'topic.framing': 'Keretezés',
    'topic.keyPhrases': 'Kulcsmondatok',
    'topic.originalArticles': 'Eredeti cikkek',
    'topic.close': 'Bezárás',

    // About page
    'about.title': 'A Projektről',
    'about.whatIsTitle': 'Mi ez az oldal?',
    'about.whatIsParagraph1': 'A Magyar Hírek Összefoglaló egy innovatív, mesterséges intelligencia által működtetett hírportál, amely naponta feldolgozza a legnagyobb magyar hírforrások tartalmát. Az oldal egyedülálló módon nem csak összegyűjti, hanem elemzi és összehasonlítja a különböző médiumok hírtálalását és keretezését.',
    'about.whatIsParagraph2': 'A projekt célja kettős: egyrészt időt takarít meg azzal, hogy tömör, lényegre törő áttekintést ad a napi legfontosabb eseményekről, másrészt segít átlátni a különböző hírforrások közötti különbségeket és hasonlóságokat, így támogatva a médiatudatosságot.',
    'about.howWorksTitle': 'Hogyan működik?',
    'about.howWorksParagraph1': 'Az alkalmazás naponta többször, automatikusan begyűjti a nagy magyar hírportálok friss cikkeit, majd a Google Gemini mesterséges intelligencia segítségével elemzi őket.',
    'about.howWorksParagraph2': 'Minden hírforráshoz készül egy átfogó napi összefoglaló, ami a legfontosabb témakörök szerint rendszerezi az információkat. Emellett az alkalmazás összehasonlító elemzést is végez, amely részletesen bemutatja, hogyan tudósítanak az egyes médiumok ugyanazokról az eseményekről, kiemelve a hangvételbeli és keretezésbeli különbségeket.',
    'about.howWorksParagraph3': 'Az elemzések automatikusan készülnek, ezért előfordulhatnak pontatlanságok. Az oldal célja nem a hírforrások helyettesítése, hanem egy mélyebb rálátás biztosítása a magyar médiakörképre.',
    'about.technologyTitle': 'Technológiai háttér',
    'about.frontendTitle': 'Frontend',
    'about.backendTitle': 'Backend',
    'about.creatorTitle': 'Készítő',
    'about.creatorDescription': 'Az alkalmazást Marci készítette portfólió projektként.',

  },
  en: {
    // Navigation
    'nav.home': 'Home',
    'nav.analysis': 'Analysis',
    'nav.about': 'About',
    
    // Homepage
    'home.title': 'Hungarian News Summary',
    'home.loading': 'Loading summaries...',
    'home.error': 'Oops! An error occurred:',
    'home.noSummaries': 'No summaries available for today. Please check back later!',
    'home.readMore': 'Full Summary',
    'home.serverNotice': 'We\'re using a server that may take longer to load initially. Please stay on the page, the application will load shortly.',
    
    // Analysis page
    'analysis.title': 'News Sources Comparative Analysis',
    'analysis.loading': 'Loading analysis...',
    'analysis.error': 'Oops! An error occurred:',
    'analysis.topicsComparison': 'topics compared from',
    'analysis.differentSources': 'different news sources',
    'analysis.noAnalysis': 'No analysis found for topics on this date.',
    'analysis.detailedAnalysis': 'Detailed Analysis',
    'analysis.sentiment': 'Sentiment',
    'analysis.positive': 'Positive',
    'analysis.neutral': 'Neutral',
    'analysis.negative': 'Negative',
    'analysis.filterBySource': 'Filter by news source:',
    'analysis.showAll': 'Show all',
    'analysis.topicsShowing': 'topics showing from',
    'analysis.selectedSources': 'selected sources',
    'analysis.noMatchingTopics': 'No topics match the selected sources.',

    //Sentiment and political leaning
    'sentiment.pozitív': 'Positive',
    'sentiment.semleges': 'Neutral',
    'sentiment.negatív': 'Negative',
    'leaning.bal': 'Left',
    'leaning.baloldali': 'Left-wing',
    'leaning.közép-bal': 'Center-Left',
    'leaning.közép': 'Center',
    'leaning.független': 'Independent',
    'leaning.közép-jobb': 'Center-Right',
    'leaning.jobb': 'Right',
    'leaning.jobboldali': 'Right-wing',
    
    // Dashboard
    'dashboard.title': 'News Sentiment Analysis',
    'dashboard.overallSentiment': 'Overall Media Sentiment',
    'dashboard.bySource': 'By News Source',
    'dashboard.politicalLeaning': 'Political Leaning',
    'dashboard.topics': 'topics',
    'dashboard.left': 'Left',
    'dashboard.centerLeft': 'Center-Left',
    'dashboard.center': 'Center',
    'dashboard.centerRight': 'Center-Right',
    'dashboard.right': 'Right',
    
    // Topic Modal
    'topic.sourcesCoverage': 'News Sources Coverage',
    'topic.originalTopic': 'Original Topic',
    'topic.framing': 'Framing',
    'topic.keyPhrases': 'Key Phrases',
    'topic.originalArticles': 'Original Articles',
    'topic.close': 'Close',

    // About page
    'about.title': 'About the Project',
    'about.whatIsTitle': 'What is this site?',
    'about.whatIsParagraph1': 'Hungarian News Summary is an innovative, AI-powered news portal that processes content from major Hungarian news sources daily. The site uniquely not only collects but analyzes and compares how different media outlets present and frame their news.',
    'about.whatIsParagraph2': 'The project has a dual purpose: it saves time by providing concise, essential overviews of the day\'s most important events, while helping users understand the differences and similarities between news sources, thus promoting media literacy.',
    'about.howWorksTitle': 'How does it work?',
    'about.howWorksParagraph1': 'The application automatically collects fresh articles from major Hungarian news portals several times a day, then analyzes them using Google Gemini artificial intelligence.',
    'about.howWorksParagraph2': 'A comprehensive daily summary is created for each news source, organizing information by the most important topics. Additionally, the application conducts comparative analysis that details how different media outlets report on the same events, highlighting differences in tone and framing.',
    'about.howWorksParagraph3': 'The analyses are generated automatically, so inaccuracies may occur. The purpose of the site is not to replace news sources but to provide a deeper insight into the Hungarian media landscape.',
    'about.technologyTitle': 'Technology Stack',
    'about.frontendTitle': 'Frontend',
    'about.backendTitle': 'Backend',
    'about.creatorTitle': 'Creator',
    'about.creatorDescription': 'This application was created by Marci as a portfolio project.',
  },
};

export const LanguageProvider: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  // Try to get language from localStorage or default to Hungarian
  const [language, setLanguageState] = useState<Language>(() => {
    const savedLanguage = localStorage.getItem('language');
    return (savedLanguage === 'en' ? 'en' : 'hu') as Language;
  });

  // Translation function
  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  // Update language and save to localStorage
  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Custom hook for using the language context
export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};