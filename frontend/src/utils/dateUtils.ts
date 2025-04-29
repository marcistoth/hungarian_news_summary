// Date formatting utility
export const formatDate = (date: Date): string => {
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      weekday: 'long'
    };
    
    return date.toLocaleDateString('hu-HU', options);
  };