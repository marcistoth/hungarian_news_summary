import React from 'react';
import { formatDate } from '../utils/dateUtils';
import { parseSummaryContent } from '../utils/parseSummary';
import { Summary } from '../types';
import { getNewsSourceConfig } from '../config';

interface SummaryModalProps {
  summary: Summary | null;
  onClose: () => void;
}

const SummaryModal: React.FC<SummaryModalProps> = ({ summary, onClose }) => {
  if (!summary) return null;

  const parsedSections = parseSummaryContent(summary.content);
  const sourceConfig = getNewsSourceConfig(summary.domain);
  
  // Prevent clicks inside the modal from closing it
  const handleModalContentClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    // Overlay backdrop
    <div
      className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm p-4"
      onClick={onClose}
    >
      {/* Modal Content */}
      <div
        className="bg-white rounded-lg shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto"
        onClick={handleModalContentClick}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        {/* Header with source branding */}
        <div 
          className="px-6 py-4 flex items-center justify-between"
          style={{ backgroundColor: sourceConfig.primaryColor, color: sourceConfig.textColor }}
        >
          <div className="flex items-center">
            <img 
              src={sourceConfig.logo} 
              alt={`${sourceConfig.name} logo`}
              className="h-8 mr-3 rounded p-1" 
            />
            <h2 
              id="modal-title"
              className="text-xl font-bold"
            >
              {sourceConfig.name} Összefoglaló
            </h2>
          </div>
          
          <span className="text-sm opacity-90">
            {formatDate(new Date(summary.date))}
          </span>
        </div>
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 flex items-center justify-center w-10 h-10 rounded-full bg-black bg-opacity-20 hover:bg-opacity-40 hover:shadow-lg shadow-md transition-all transform hover:scale-105 cursor-pointer"
          aria-label="Close modal"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        {/* Content */}
        <div className="p-6 md:p-8">
          {parsedSections.map((section, index) => (
            <div key={`section-${index}`} className="mb-6 last:mb-0">
              <h3 
                className="text-xl font-semibold mb-3 pb-2 border-b"
                style={{ borderColor: sourceConfig.secondaryColor, color: sourceConfig.primaryColor }}
              >
                {section.title}
              </h3>
              <div className="prose max-w-none">
                {section.content.split('\n').map((paragraph, pIndex) => (
                  paragraph.trim() ? (
                    <p key={`p-${index}-${pIndex}`} className="mb-3">
                      {paragraph}
                    </p>
                  ) : null
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SummaryModal;