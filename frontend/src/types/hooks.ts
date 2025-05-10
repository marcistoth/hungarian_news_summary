import { useState, useEffect } from 'react';

/**
 * Hook that shows a loading message after a specified delay
 * @param isLoading Boolean indicating if content is loading
 * @param delayMs Delay in milliseconds before showing the message (default: 3000ms)
 * @returns Boolean indicating whether to show the delayed message
 */
export const useDelayedLoadingMessage = (isLoading: boolean, delayMs = 3000) => {
  const [showLoadingMessage, setShowLoadingMessage] = useState(false);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    
    if (isLoading) {
      timer = setTimeout(() => {
        setShowLoadingMessage(true);
      }, delayMs);
    } else {
      setShowLoadingMessage(false);
    }

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isLoading, delayMs]);

  return showLoadingMessage;
};