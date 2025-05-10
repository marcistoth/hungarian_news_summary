import React, { useMemo } from 'react';
import { UnifiedTopic } from '../types/analysis';
import { getNewsSourceConfig } from '../config';
import { useLanguage } from '../contexts/LanguageContext';

interface TopicCardProps {
  topic: UnifiedTopic;
  onClick: () => void;
  highlightSources?: string[];
}

const TopicCard: React.FC<TopicCardProps> = ({ topic, onClick, highlightSources }) => {
  const { t } = useLanguage();
  
  // Calculate sentiment counts
  const sentimentCounts = useMemo(() => {
    const counts = {
      pozitív: 0,
      semleges: 0,
      negatív: 0
    };
    
    topic.source_coverage.forEach(source => {
      if (source.sentiment === 'pozitív') counts.pozitív++;
      else if (source.sentiment === 'negatív') counts.negatív++;
      else counts.semleges++;
    });
    
    return counts;
  }, [topic]);

  const cardStyle = {
    borderTop: `4px solid #2657A7`,  // Same blue color used in the app
    borderRadius: '8px',
  };
  
  return (
    <div 
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
      onClick={onClick}
      style={cardStyle}
    >
      <div className="p-5">
        <h3 className="text-xl font-semibold mb-4 text-primary-dark">
          {topic.name}
        </h3>
        
        <div className="flex flex-wrap gap-2 mb-3">
          {(() => {
            const renderedDomains = new Set<string>();
            
            return topic.source_coverage.map((source, index) => {
              // Skip if this domain has already been rendered
              if (renderedDomains.has(source.domain)) {
                return null;
              }
              renderedDomains.add(source.domain);
              
              const sourceConfig = getNewsSourceConfig(source.domain);
              const isHighlighted = highlightSources?.includes(source.domain);
              
              return (
                <div 
                  key={`source-${index}`}
                  className={`flex items-center h-8 px-2 rounded-full transition-all ${
                    isHighlighted ? 'ring-2 ring-primary shadow-sm scale-105' : ''
                  }`}
                  style={{ 
                    backgroundColor: sourceConfig.secondaryColor,
                    color: sourceConfig.primaryColor
                  }}
                >
                  <img 
                    src={sourceConfig.logo} 
                    alt={sourceConfig.name}
                    className="w-5 h-5 mr-1 rounded" 
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = '/hungarian_news_summary/logos/default-logo.png';
                    }}
                  />
                  <span className="text-xs font-medium">{sourceConfig.name}</span>
                </div>
              );
            }).filter(Boolean);
          })()}
        </div>
        <div className="mb-4">
          <h4 className="text-sm font-medium text-text-light mb-2">{t('analysis.sentiment')}:</h4>
          <div className="flex space-x-2">
            {sentimentCounts.pozitív > 0 && (
              <div className="bg-green-100 text-green-800 text-xs font-medium px-2 py-0.5 rounded">
                {t('analysis.positive')}: {sentimentCounts.pozitív}
              </div>
            )}
            {sentimentCounts.semleges > 0 && (
              <div className="bg-gray-100 text-gray-800 text-xs font-medium px-2 py-0.5 rounded">
                {t('analysis.neutral')}: {sentimentCounts.semleges}
              </div>
            )}
            {sentimentCounts.negatív > 0 && (
              <div className="bg-red-100 text-red-800 text-xs font-medium px-2 py-0.5 rounded">
                {t('analysis.negative')}: {sentimentCounts.negatív}
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
          {t('analysis.detailedAnalysis')}
          <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default TopicCard;