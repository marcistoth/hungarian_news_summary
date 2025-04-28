import React from 'react';
import { Summary } from '../types';
import { getSummaryPreview } from '../utils/parseSummary'; // Import preview helper

interface SummaryCardProps {
  summary: Summary;
  index: number;
  onCardClick: () => void; // Add callback prop for clicking
}

const SummaryCard: React.FC<SummaryCardProps> = ({ summary, index, onCardClick }) => {
  const cardBg = index % 2 === 0 ? 'bg-background-alt' : 'bg-secondary-light/20';
  const previewContent = getSummaryPreview(summary.content); // Get preview

  return (
    <article
      className={`
        ${cardBg}
        rounded-xl shadow-md border border-gray-200/60
        p-6 flex flex-col group cursor-pointer  /* Add cursor-pointer */
        transition duration-300 ease-in-out
        hover:shadow-xl hover:border-primary/30 hover:-translate-y-1.5
      `}
      onClick={onCardClick} // Attach the click handler
      role="button" // Add role for accessibility
      tabIndex={0} // Make it focusable
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onCardClick()} // Keyboard activation
    >
      {/* Header section */}
      <div className="mb-4 pb-3 border-b border-gray-200/80">
        <h2 className="text-2xl font-semibold text-primary-dark mb-1 capitalize group-hover:text-primary transition-colors duration-300">
          {summary.domain || 'Általános'}
        </h2>
        <p className="text-sm text-text-muted font-medium">{summary.date}</p>
      </div>

      {/* Preview Content */}
      <p className="text-text-light mb-5 flex-grow leading-relaxed text-base">
        {previewContent} {/* Display preview instead of full content */}
      </p>

      {/* Footer section */}
      <div className="mt-auto pt-3 border-t border-gray-200/50 flex justify-between items-center">
         <span className="text-xs font-medium text-primary bg-primary-light/20 px-2 py-0.5 rounded">
            {summary.language.toUpperCase()}
         </span>
         <span className="text-xs font-medium text-primary group-hover:underline">
            Részletek... {/* Indicate clickability */}
         </span>
      </div>
    </article>
  );
};

export default SummaryCard;