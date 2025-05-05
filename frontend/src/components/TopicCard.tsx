import React from 'react';
import { UnifiedTopic } from '../types/analysis';
import { getNewsSourceConfig } from '../config';

interface TopicCardProps {
  topic: UnifiedTopic;
  onClick: () => void;
}

const TopicCard: React.FC<TopicCardProps> = ({ topic, onClick }) => {
//   const sourcesCount = topic.source_coverage.length;
  
  // Group sources by sentiment
  const sentimentCounts = {
    pozitív: 0,
    semleges: 0,
    negatív: 0
  };
  
  topic.source_coverage.forEach((source: UnifiedTopic['source_coverage'][number]) => {
    if (source.sentiment in sentimentCounts) {
      sentimentCounts[source.sentiment as keyof typeof sentimentCounts] += 1;
    }
  });
  
  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 cursor-pointer"
      onClick={onClick}
    >
      <div className="p-5">
        <h3 className="text-xl font-bold text-primary mb-3">{topic.name}</h3>
        
        <div className="flex items-center gap-2 flex-wrap mb-4">
          {topic.source_coverage.map((source, index) => {
            const sourceConfig = getNewsSourceConfig(source.domain);
            console.log(sourceConfig);
            return (
              <div 
                key={`source-${index}`}
                className="flex items-center h-8 px-2 rounded-full"
                style={{ 
                  backgroundColor: sourceConfig.secondaryColor,
                  color: sourceConfig.primaryColor
                }}
              >
                <img 
                  src={sourceConfig.logo} 
                  alt={sourceConfig.name}
                  className="h-5 w-5 mr-1 rounded-full object-cover" 
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = '/hungarian_news_summary/logos/default-logo.png';
                  }}
                />
                <span className="text-xs font-medium">{sourceConfig.name}</span>
              </div>
            );
          })}
        </div>
        
        <div className="mb-4">
          <h4 className="text-sm font-medium text-text-light mb-2">Hangvétel megoszlása:</h4>
          <div className="flex space-x-2">
            {sentimentCounts.pozitív > 0 && (
              <div className="bg-green-100 text-green-800 text-xs font-medium px-2 py-0.5 rounded">
                Pozitív: {sentimentCounts.pozitív}
              </div>
            )}
            {sentimentCounts.semleges > 0 && (
              <div className="bg-gray-100 text-gray-800 text-xs font-medium px-2 py-0.5 rounded">
                Semleges: {sentimentCounts.semleges}
              </div>
            )}
            {sentimentCounts.negatív > 0 && (
              <div className="bg-red-100 text-red-800 text-xs font-medium px-2 py-0.5 rounded">
                Negatív: {sentimentCounts.negatív}
              </div>
            )}
          </div>
        </div>
        
        <div className="text-sm text-text-light line-clamp-2 mb-3">
          {topic.comparative_analysis.substring(0, 120)}...
        </div>
        
        <div 
          className="inline-flex items-center text-xs font-medium text-primary"
        >
          Részletes elemzés
          <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default TopicCard;