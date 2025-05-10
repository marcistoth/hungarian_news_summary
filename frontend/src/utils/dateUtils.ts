// Date formatting utility
import { Language } from '../contexts/LanguageContext';

export const formatDate = (date: Date, language?: Language): string => {
  const options: Intl.DateTimeFormatOptions = { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  };
  
  // Hungarian locale for 'hu', English locale for 'en'
  const locale = language === 'en' ? 'en-US' : 'hu-HU';
  return date.toLocaleDateString(locale, options);
};