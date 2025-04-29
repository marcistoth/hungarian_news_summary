import React from 'react';
import { formatDate } from '../utils/dateUtils';
import { Summary } from '../types';
import { getNewsSourceConfig } from '../config';
import { getSummaryPreview } from '../utils/parseSummary';

interface SummaryCardProps {
  summary: Summary;
  index: number;
  onCardClick: () => void;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ summary, onCardClick }) => {
  const { date, domain } = summary;
  const sourceConfig = getNewsSourceConfig(domain);
  
  // Get first paragraph of content as preview
  const contentPreview = getSummaryPreview(summary.content);
  const formattedDate = formatDate(new Date(date));
  
  // Custom styles for each news source
  const cardStyle = {
    borderTop: `4px solid ${sourceConfig.primaryColor}`,
    borderRadius: '8px',
  };
  
  return (
    <div 
      className="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-xl transform hover:-translate-y-1 cursor-pointer"
      style={cardStyle}
      onClick={onCardClick}
      aria-label={`${sourceConfig.name} news summary`}
    >
      <div className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <img 
              src={sourceConfig.logo} 
              alt={`${sourceConfig.name} logo`}
              className="h-7 mr-2" 
              onError={(e) => {
                // Fallback if logo fails to load
                const target = e.target as HTMLImageElement;
                target.src = '/hungarian_news_summary/logos/default-logo.png';
              }}
            />
            <h3 
              className="text-xl font-bold" 
              style={{ color: sourceConfig.primaryColor }}
            >
              {sourceConfig.name}
            </h3>
          </div>
          <span className="text-text-muted text-sm">{formattedDate}</span>
        </div>
        
        <div className="mb-3">
          <p className="text-text-light">
            {contentPreview}
          </p>
        </div>
        
        <div 
          className="mt-4 py-2 px-3 text-sm inline-flex items-center rounded-full" 
          style={{ backgroundColor: sourceConfig.secondaryColor, color: sourceConfig.primaryColor }}
        >
          Teljes összefoglaló
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default SummaryCard;