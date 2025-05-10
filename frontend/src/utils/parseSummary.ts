import { Language } from '../contexts/LanguageContext';

export interface ParsedSummarySection {
    title: string;
    content: string;
  }
  
  const sectionTitles: Record<Language, Record<string, string>> = {
    hu: {
      BEVEZETO: "Bevezető",
      BELFOLD: "Belpolitika",
      GAZDASAG: "Gazdaság",
      KULFOLD: "Külföld",
      TARSADALOM: "Társadalom, Kultúra, Tudomány",
      ZARAS: "Zárás",
    },
    en: {
      BEVEZETO: "Introduction",
      BELFOLD: "Domestic Politics",
      GAZDASAG: "Economy",
      KULFOLD: "Foreign Affairs",
      TARSADALOM: "Society, Culture & Science",
      ZARAS: "Conclusion",
    }
  };
  
  /**
   * Cleans the raw LLM output string by removing any leading characters
   * before the first expected marker ([START_SHORT_SUMMARY] or [START_MAIN_SUMMARY]).
   * @param rawContent The raw string from the LLM.
   * @returns The cleaned string starting from the first marker, or the original string if no marker is found.
   */
  const cleanRawContent = (rawContent: string): string => {
      if (!rawContent) return "";
  
      const shortSummaryMarker = "[START_SHORT_SUMMARY]";
      const mainSummaryMarker = "[START_MAIN_SUMMARY]"; // Check for this too, just in case
  
      const shortIndex = rawContent.indexOf(shortSummaryMarker);
      const mainIndex = rawContent.indexOf(mainSummaryMarker);
  
      let startIndex = -1;
  
      if (shortIndex !== -1 && mainIndex !== -1) {
          startIndex = Math.min(shortIndex, mainIndex); // Find the earliest marker
      } else if (shortIndex !== -1) {
          startIndex = shortIndex;
      } else if (mainIndex !== -1) {
          startIndex = mainIndex;
      }
  
      if (startIndex > 0) {
          // If a marker is found and it's not at the beginning, trim the start
          return rawContent.substring(startIndex);
      } else if (startIndex === 0) {
          // Marker is already at the start
          return rawContent;
      } else {
          // No relevant start marker found, return original (might be unstructured)
          console.warn("Could not find expected start markers in raw content.");
          return rawContent;
      }
  };
  
  
  export const parseSummaryContent = (rawContentInput: string, language: Language = 'hu'): ParsedSummarySection[] => {
    // Clean the input first
    const rawContent = cleanRawContent(rawContentInput);
  
    if (!rawContent) {
      return [];
    }
  
    const sections: ParsedSummarySection[] = [];
    // Regex assumes markers are correctly placed after cleaning
    const regex = /\[START_([A-Z_]+)\]([\s\S]*?)\[END_\1\]/g;
    let match;


    // Titles for current language
    const currentTitles = sectionTitles[language];
  
    // Find the main summary block first if it exists
    const mainSummaryMatch = rawContent.match(/\[START_MAIN_SUMMARY\]([\s\S]*?)\[END_MAIN_SUMMARY\]/);
    const contentToParse = mainSummaryMatch ? mainSummaryMatch[1] : rawContent; // Parse within MAIN_SUMMARY or whole string
  
    while ((match = regex.exec(contentToParse)) !== null) {
      const key = match[1];
      // Skip the outer MAIN_SUMMARY markers if found within the loop
      if (key === 'MAIN_SUMMARY' || key === 'SHORT_SUMMARY') continue;
  
      let content = match[2].trim();
      const title = currentTitles[key] || key.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  
      const titlePattern = new RegExp(`^\\*\\*${title}\\*\\*\\s*\\n?`);
      content = content.replace(titlePattern, '').trim();
  
      if (content) {
        sections.push({ title, content });
      }
    }
  
     // Handle content outside specific section markers but within MAIN_SUMMARY
     const textBeforeFirstSection = contentToParse.split(/\[START_[A-Z_]+\]/)[0]?.trim();
     if (textBeforeFirstSection && !sections.some(s => s.title === sectionTitles[language].BEVEZETO)) {
         sections.unshift({ title: sectionTitles[language].BEVEZETO, content: textBeforeFirstSection });
     } else if (!sections.length && contentToParse) {
         // If no sections found within MAIN_SUMMARY, treat its content as general
         sections.push({ title: "Összefoglaló", content: contentToParse });
     } else if (!sections.length && !mainSummaryMatch && rawContent) {
          // If no MAIN_SUMMARY and no sections, treat original cleaned content as general
          sections.push({ title: "Összefoglaló", content: rawContent });
     }
  
    return sections;
  };
  
  export const getSummaryPreview = (rawContentInput: string, language: Language = 'hu'): string => {
    // Clean the input first
    const rawContent = cleanRawContent(rawContentInput);
  
    if (!rawContent) return sectionTitles[language].ERROR;
  
    // Extract content between SHORT_SUMMARY markers
    const shortSummaryRegex = /\[START_SHORT_SUMMARY\]([\s\S]*?)\[END_SHORT_SUMMARY\]/;
    const shortMatch = rawContent.match(shortSummaryRegex);
  
    if (shortMatch && shortMatch[1]) {
      return shortMatch[1].trim(); // Return the captured short summary
    }
  
    // Fallback: If SHORT_SUMMARY markers are missing after cleaning, try BEVEZETO
    const sections = parseSummaryContent(rawContent, language); // Use the already cleaned content
    const bevezeto = sections.find(s => s.title === sectionTitles[language].BEVEZETO);
    if (bevezeto?.content) {
      return bevezeto.content;
    }
  
    // Final Fallback: return first 150 chars of the cleaned content
    console.warn("BEVEZETO not found, using substring fallback for preview.");
    const fallbackContent = rawContent.split(/\[START_|\[END_/)[0].trim(); // Try text before any marker
    return (fallbackContent || rawContent).substring(0, 150) + ((fallbackContent || rawContent).length > 150 ? '...' : '');
  };