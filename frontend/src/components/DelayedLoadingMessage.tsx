import React from 'react';
import { useDelayedLoadingMessage } from '../types/hooks';
import { useLanguage } from '../contexts/LanguageContext';

interface DelayedLoadingMessageProps {
  isLoading: boolean;
  delayMs?: number;
}

const DelayedLoadingMessage: React.FC<DelayedLoadingMessageProps> = ({ isLoading, delayMs = 3000 }) => {
  const showMessage = useDelayedLoadingMessage(isLoading, delayMs);
  const { t } = useLanguage();
  
  if (!showMessage) return null;
  
  return (
    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md max-w-md mx-auto text-sm text-blue-700 text-center">
      <p>{t('home.serverNotice')}</p>
    </div>
  );
};

export default DelayedLoadingMessage;