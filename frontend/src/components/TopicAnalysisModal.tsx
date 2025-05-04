import React from 'react';
import { UnifiedTopic } from '../types/analysis';
import { getNewsSourceConfig } from '../config';

interface TopicAnalysisModalProps {
  topic: UnifiedTopic;
  onClose: () => void;
}

const TopicAnalysisModal: React.FC<TopicAnalysisModalProps> = ({ topic, onClose }) => {
  // Prevent clicks inside the modal from closing it
  const handleModalContentClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };
  
  // Helper to get color for sentiment
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'pozitív': return 'bg-green-100 text-green-800';
      case 'negatív': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Helper to get color for political leaning
  const getLeaningColor = (leaning: string) => {
    switch (leaning.toLowerCase()) {
      case 'bal':
      case 'közép-bal': return 'bg-blue-100 text-blue-800';
      case 'közép': return 'bg-gray-100 text-gray-800';
      case 'közép-jobb':
      case 'jobb': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto"
        onClick={handleModalContentClick}
      >
        {/* Header */}
        <div className="px-6 py-4 bg-primary text-white flex justify-between items-center">
          <h2 className="text-xl font-bold">
            {topic.name}
          </h2>
          <button
            onClick={onClose}
            className="text-white hover:bg-opacity-20 hover:bg-black bg-opacity-0 transition-colors rounded-full p-1 text-2xl"
            aria-label="Close modal"
          >
            &times;
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6">
          {/* Comparative Analysis */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3 pb-2 border-b border-gray-200">
              Összehasonlító elemzés
            </h3>
            <div className="prose max-w-none text-text-light">
              {topic.comparative_analysis.split('\n').map((paragraph, idx) => (
                paragraph.trim() ? <p key={idx} className="mb-3">{paragraph}</p> : null
              ))}
            </div>
          </div>
          
          {/* Sources Coverage */}
          <h3 className="text-lg font-semibold mb-4 pb-2 border-b border-gray-200">
            Hírforrások tudósítása
          </h3>
          
          <div className="space-y-6">
            {topic.source_coverage.map((source, idx) => {
              const sourceConfig = getNewsSourceConfig(source.domain);
              
              return (
                <div key={`source-${idx}`} className="bg-background p-4 rounded-lg border border-gray-100">
                  {/* Source Header */}
                  <div 
                    className="flex items-center mb-3 pb-2 border-b"
                    style={{ borderColor: sourceConfig.secondaryColor }}
                  >
                    <img 
                      src={sourceConfig.logo} 
                      alt={sourceConfig.name}
                      className="h-8 w-8 mr-2 rounded" 
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = '/hungarian_news_summary/logos/default-logo.png';
                      }}
                    />
                    <h4 
                      className="text-lg font-semibold"
                      style={{ color: sourceConfig.primaryColor }}
                    >
                      {sourceConfig.name}
                    </h4>
                  </div>
                  
                  {/* Source Content */}
                  <div className="space-y-3">
                    <div className="flex flex-wrap gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded ${getSentimentColor(source.sentiment)}`}>
                        {source.sentiment}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded ${getLeaningColor(source.political_leaning)}`}>
                        {source.political_leaning}
                      </span>
                    </div>
                    
                    <p className="text-sm text-text-light">
                      <span className="font-medium">Eredeti téma:</span> {source.original_topic_name}
                    </p>
                    
                    <p className="text-sm text-text-light">
                      <span className="font-medium">Keretezés:</span> {source.framing}
                    </p>
                    
                    {source.key_phrases.length > 0 && (
                      <div className="mt-2">
                        <p className="text-sm font-medium mb-1">Kulcsmondatok:</p>
                        <ul className="list-disc list-inside text-sm text-text-light space-y-1">
                          {source.key_phrases.map((phrase, i) => (
                            <li key={`phrase-${idx}-${i}`} className="italic">"{phrase}"</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopicAnalysisModal;