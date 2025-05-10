import React from 'react';
import { useDelayedLoadingMessage } from '../types/hooks';

interface DelayedLoadingMessageProps {
  isLoading: boolean;
  delayMs?: number;
}

const DelayedLoadingMessage: React.FC<DelayedLoadingMessageProps> = ({ isLoading, delayMs = 3000 }) => {
  const showMessage = useDelayedLoadingMessage(isLoading, delayMs);
  
  if (!showMessage) return null;
  
  return (
    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md max-w-md mx-auto text-sm text-blue-700 text-center">
      <p>
        Olyan szervert használunk, aminek az első betöltéséhez hosszabb idő kell. 
        Kérjük, ne lépj el, hamarosan betölt az alkalmazás.
      </p>
    </div>
  );
};

export default DelayedLoadingMessage;