import React, { useMemo } from 'react';
import { CrossSourceAnalysis } from '../types/analysis';
import { getNewsSourceConfig } from '../config';
import { useLanguage } from '../contexts/LanguageContext';

interface SentimentDashboardProps {
  analysis: CrossSourceAnalysis;
  selectedSources?: string[];
}

const SentimentDashboard: React.FC<SentimentDashboardProps> = ({ analysis, selectedSources }) => {
  const { t } = useLanguage();
  
  // Analyze data to extract sentiment metrics
  const metrics = useMemo(() => {
    // Initialize counters
    const sentimentBySource: Record<string, {pozitív: number, semleges: number, negatív: number}> = {};
    const politicalBySource: Record<string, {bal: number, 'közép-bal': number, közép: number, 'közép-jobb': number, jobb: number}> = {};
    const sourceCounts: Record<string, number> = {};
    
    // Count sources used in the analysis
    const uniqueSources = new Set<string>();
    
    // Process each topic and its coverage
    analysis.unified_topics.forEach(topic => {
      topic.source_coverage.forEach(coverage => {
        const domain = coverage.domain;
        
        // Skip if we're filtering and this source isn't selected
        if (selectedSources && !selectedSources.includes(domain)) return;
        
        uniqueSources.add(domain);
        
        // Initialize counters for this source if needed
        if (!sentimentBySource[domain]) {
          sentimentBySource[domain] = { pozitív: 0, semleges: 0, negatív: 0 };
          politicalBySource[domain] = { 
            'bal': 0, 'közép-bal': 0, 'közép': 0, 'közép-jobb': 0, 'jobb': 0 
          };
          sourceCounts[domain] = 0;
        }
        
        // Increment counters
        sourceCounts[domain]++;
        sentimentBySource[domain][coverage.sentiment as keyof typeof sentimentBySource[typeof domain]]++;
        politicalBySource[domain][coverage.political_leaning as keyof typeof politicalBySource[typeof domain]]++;
      });
    });
    
    return {
      sentimentBySource,
      politicalBySource,
      sourceCounts,
      uniqueSources: Array.from(uniqueSources)
    };
  }, [analysis, selectedSources]);

  // Calculate overall sentiment distribution
  const overallSentiment = useMemo(() => {
    let positive = 0, neutral = 0, negative = 0, total = 0;
    
    Object.values(metrics.sentimentBySource).forEach(counts => {
      positive += counts.pozitív;
      neutral += counts.semleges;
      negative += counts.negatív;
      total += counts.pozitív + counts.semleges + counts.negatív;
    });
    
    return {
      positive: total ? (positive / total * 100).toFixed(1) : "0",
      neutral: total ? (neutral / total * 100).toFixed(1) : "0",
      negative: total ? (negative / total * 100).toFixed(1) : "0",
      total
    };
  }, [metrics]);

  return (
    <div className="bg-white rounded-lg shadow-md p-5 mb-8">
      <h2 className="text-xl font-semibold mb-4 text-primary-dark">{t('dashboard.title')}</h2>
      
      {/* Overall sentiment */}
      <div className="mb-5">
        <h3 className="text-base font-medium mb-2">{t('dashboard.overallSentiment')}</h3>
        <div className="flex items-center mb-2">
          <div className="w-full h-6 bg-gray-100 rounded-full overflow-hidden flex">
            <div 
              className="h-full bg-green-500" 
              style={{width: `${overallSentiment.positive}%`}}
              title={`${t('analysis.positive')}: ${overallSentiment.positive}%`}
            ></div>
            <div 
              className="h-full bg-gray-300" 
              style={{width: `${overallSentiment.neutral}%`}}
              title={`${t('analysis.neutral')}: ${overallSentiment.neutral}%`}
            ></div>
            <div 
              className="h-full bg-red-500" 
              style={{width: `${overallSentiment.negative}%`}}
              title={`${t('analysis.negative')}: ${overallSentiment.negative}%`}
            ></div>
          </div>
        </div>
        <div className="flex justify-between text-xs text-text-light">
          <span>{t('analysis.positive')} ({overallSentiment.positive}%)</span>
          <span>{t('analysis.neutral')} ({overallSentiment.neutral}%)</span>
          <span>{t('analysis.negative')} ({overallSentiment.negative}%)</span>
        </div>
      </div>
      
      {/* Per source sentiment */}
      <h3 className="text-base font-medium mb-3">{t('dashboard.bySource')}</h3>
      <div className="space-y-3">
        {metrics.uniqueSources.map(domain => {
          const sentimentCounts = metrics.sentimentBySource[domain];
          const total = sentimentCounts.pozitív + sentimentCounts.semleges + sentimentCounts.negatív;
          const sourceConfig = getNewsSourceConfig(domain);
          
          return (
            <div key={domain} className="flex items-center">
              <div className="w-28 flex items-center">
                <img 
                  src={sourceConfig.logo} 
                  alt={sourceConfig.name} 
                  className="w-6 h-6 mr-2 rounded"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = '/hungarian_news_summary/logos/default-logo.png';
                  }}
                />
                <span className="text-sm font-medium truncate">{sourceConfig.name}</span>
              </div>
              <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden flex mr-3">
                <div 
                  className="bg-green-500 h-full" 
                  style={{width: `${total ? (sentimentCounts.pozitív/total*100) : 0}%`}}
                ></div>
                <div 
                  className="bg-gray-300 h-full" 
                  style={{width: `${total ? (sentimentCounts.semleges/total*100) : 0}%`}}
                ></div>
                <div 
                  className="bg-red-500 h-full" 
                  style={{width: `${total ? (sentimentCounts.negatív/total*100) : 0}%`}}
                ></div>
              </div>
              <div className="w-28 text-xs flex justify-between">
                <span className="text-green-600">{sentimentCounts.pozitív}</span>
                <span className="text-gray-600">{sentimentCounts.semleges}</span>
                <span className="text-red-600">{sentimentCounts.negatív}</span>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Political leaning chart */}
      <h3 className="text-base font-medium mt-6 mb-3">{t('dashboard.politicalLeaning')}</h3>
      <div className="space-y-3">
        {metrics.uniqueSources.map(domain => {
          const politicalCounts = metrics.politicalBySource[domain];
          const total = politicalCounts.bal + politicalCounts['közép-bal'] + 
                       politicalCounts.közép + politicalCounts['közép-jobb'] + 
                       politicalCounts.jobb;
          const sourceConfig = getNewsSourceConfig(domain);
          
          return (
            <div key={`pol-${domain}`} className="flex items-center">
              <div className="w-28 flex items-center">
                <img 
                  src={sourceConfig.logo} 
                  alt={sourceConfig.name} 
                  className="w-6 h-6 mr-2 rounded"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = '/hungarian_news_summary/logos/default-logo.png';
                  }} 
                />
                <span className="text-sm font-medium truncate">{sourceConfig.name}</span>
              </div>
              <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden flex mr-3">
                <div 
                  className="bg-blue-600 h-full" 
                  style={{width: `${total ? (politicalCounts.bal/total*100) : 0}%`}}
                  title={t('dashboard.left')}
                ></div>
                <div 
                  className="bg-blue-400 h-full" 
                  style={{width: `${total ? (politicalCounts['közép-bal']/total*100) : 0}%`}}
                  title={t('dashboard.centerLeft')}
                ></div>
                <div 
                  className="bg-gray-400 h-full" 
                  style={{width: `${total ? (politicalCounts.közép/total*100) : 0}%`}}
                  title={t('dashboard.center')}
                ></div>
                <div 
                  className="bg-orange-400 h-full" 
                  style={{width: `${total ? (politicalCounts['közép-jobb']/total*100) : 0}%`}}
                  title={t('dashboard.centerRight')}
                ></div>
                <div 
                  className="bg-orange-600 h-full" 
                  style={{width: `${total ? (politicalCounts.jobb/total*100) : 0}%`}}
                  title={t('dashboard.right')}
                ></div>
              </div>
              <div className="w-16 text-xs">
                {total} {t('dashboard.topics')}
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-text-muted flex justify-between">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-600 rounded-full mr-1"></div>
          <span>{t('dashboard.left')}</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-400 rounded-full mr-1"></div>
          <span>{t('dashboard.centerLeft')}</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-gray-400 rounded-full mr-1"></div>
          <span>{t('dashboard.center')}</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-orange-400 rounded-full mr-1"></div>
          <span>{t('dashboard.centerRight')}</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-orange-600 rounded-full mr-1"></div>
          <span>{t('dashboard.right')}</span>
        </div>
      </div>
    </div>
  );
};

export default SentimentDashboard;