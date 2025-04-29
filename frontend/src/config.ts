// Application configuration settings

export const API_URL = import.meta.env.VITE_API_URL;

// News source configuration
export interface NewsSourceConfig {
  name: string;
  domain: string;
  primaryColor: string;
  secondaryColor: string;
  textColor: string;
  logo: string;
}

export const NEWS_SOURCES: Record<string, NewsSourceConfig> = {
  telex: {
    name: "Telex",
    domain: "telex",
    primaryColor: "#2657A7",       // keeping current blue
    secondaryColor: "#e3eaf7",     // light blue
    textColor: "#ffffff",          // white text
    logo: "/hungarian_news_summary/logos/telex-logo.jpg"
  },
  "444": {
    name: "444.hu",
    domain: "444",
    primaryColor: "#2657A7",       // keeping current blue
    secondaryColor: "#e3eaf7",     // light blue
    textColor: "#ffffff",          // white text
    logo: "/hungarian_news_summary/logos/444-logo.png"
  },
  hvg: {
    name: "HVG",
    domain: "hvg",
    primaryColor: "#2657A7",       // keeping current blue
    secondaryColor: "#e3eaf7",     // light blue
    textColor: "#ffffff",          // white text
    logo: "/hungarian_news_summary/logos/hvg-logo.png"
  },
  origo: {
    name: "Origo",
    domain: "origo",
    primaryColor: "#2657A7",       // keeping current blue
    secondaryColor: "#e3eaf7",     // light blue
    textColor: "#ffffff",          // white text
    logo: "/hungarian_news_summary/logos/origo-logo.png"
  },
  mandiner: {
    name: "Mandiner", 
    domain: "mandiner",
    primaryColor: "#2657A7",       // keeping current blue
    secondaryColor: "#e3eaf7",     // light blue
    textColor: "#ffffff",          // white text
    logo: "/hungarian_news_summary/logos/mandiner-logo.png"
  },
  "24.hu": {
    name: "24.hu", 
    domain: "24.hu",
    primaryColor: "#2657A7",       // keeping current blue
    secondaryColor: "#e3eaf7",     // light blue
    textColor: "#ffffff",          // white text
    logo: "/hungarian_news_summary/logos/24hu-logo.jpg"
  }
};

// Utility function to get news source config by domain
export const getNewsSourceConfig = (domain: string): NewsSourceConfig => {
  return NEWS_SOURCES[domain] || {
    name: domain,
    domain: domain,
    primaryColor: "#00796b", // Default primary color
    secondaryColor: "#c8e6c9", // Default secondary color
    textColor: "#ffffff",
    logo: "/logos/default-logo.png"
  };
};