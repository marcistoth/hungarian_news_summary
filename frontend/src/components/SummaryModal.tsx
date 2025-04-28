import React from 'react';
import { Summary } from '../types';
import { parseSummaryContent, ParsedSummarySection } from '../utils/parseSummary';

interface SummaryModalProps {
  summary: Summary | null;
  onClose: () => void;
}

const SummaryModal: React.FC<SummaryModalProps> = ({ summary, onClose }) => {
  if (!summary) return null;

  const parsedSections = parseSummaryContent(summary.content);

  // Prevent clicks inside the modal from closing it
  const handleModalContentClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    // Overlay backdrop
    <div
      className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm p-4"
      onClick={onClose} // Close when clicking the backdrop
    >
      {/* Modal Content */}
      <div
        className="bg-background-alt bg-white rounded-lg shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6 md:p-8 relative"
        onClick={handleModalContentClick}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-text-muted hover:text-error transition-colors text-2xl"
          aria-label="Close modal"
        >
          &times; {/* Simple X icon */}
        </button>

        {/* Modal Header */}
        <div className="mb-6 pb-4 border-b border-gray-200">
          <h2 className="text-3xl font-bold text-primary-dark mb-1 capitalize">
            {summary.domain || 'Részletes Összefoglaló'}
          </h2>
          <p className="text-sm text-text-muted font-medium">{summary.date}</p>
        </div>

        {/* Modal Body - Render Sections */}
        <div className="space-y-6">
          {parsedSections.length > 0 ? (
            parsedSections.map((section, index) => (
              <section key={index} aria-labelledby={`section-title-${index}`}>
                <h3
                  id={`section-title-${index}`}
                  className="text-xl font-semibold text-primary mb-2 border-l-4 border-primary-light pl-2"
                >
                  {section.title}
                </h3>
                {/* Use whitespace-pre-wrap to preserve line breaks from the summary */}
                <p className="text-text-light leading-relaxed whitespace-pre-wrap">
                  {section.content}
                </p>
              </section>
            ))
          ) : (
            // Fallback if parsing fails or content is unstructured
            <p className="text-text-light leading-relaxed whitespace-pre-wrap">
              {summary.content}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SummaryModal;