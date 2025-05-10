import { useState, useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { CrossSourceAnalysisResponse, UnifiedTopic } from '../types/analysis';
import { API_URL, getNewsSourceConfig } from '../config';
import TopicCard from './TopicCard';
import TopicAnalysisModal from './TopicAnalysisModal';
import SentimentDashboard from './SentimentDashboard';
import { formatDate } from '../utils/dateUtils';
import DelayedLoadingMessage from './DelayedLoadingMessage';
import { useLanguage } from '../contexts/LanguageContext';

const TopicAnalysisPage: React.FC = () => {
  const [analysis, setAnalysis] = useState<CrossSourceAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<UnifiedTopic | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const dateParam = queryParams.get('date');
  const { language, t } = useLanguage();

  // Extract all sources from analysis
  const allSources = useMemo(() => {
    if (!analysis?.analysis?.unified_topics) return [];
    
    const sources = new Set<string>();
    analysis.analysis.unified_topics.forEach(topic => {
      topic.source_coverage.forEach(source => {
        sources.add(source.domain);
      });
    });
    
    return Array.from(sources).sort();
  }, [analysis]);
  
  // Filter topics based on selected sources
  const filteredTopics = useMemo(() => {
    if (!analysis?.analysis?.unified_topics) return [];
    
    if (selectedSources.length === 0) {
      // If no sources selected, show all topics
      return analysis.analysis.unified_topics;
    }
    
    // Filter topics that have at least one of the selected sources
    return analysis.analysis.unified_topics.filter(topic => {
      return topic.source_coverage.some(source => 
        selectedSources.includes(source.domain)
      );
    });
  }, [analysis, selectedSources]);

  useEffect(() => {
    const fetchAnalysis = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const url = dateParam 
          ? `${API_URL}/cross-source-analysis?date=${dateParam}&language=${language}`
          : `${API_URL}/cross-source-analysis?language=${language}`;
          
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data: CrossSourceAnalysisResponse = await response.json();
        
        if (data.success && data.analysis) {
          setAnalysis(data);
        } else {
          setError(data.message || t('analysis.noAnalysis'));
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : t('analysis.error');
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalysis();
  }, [dateParam, language, t]);

  const openModal = (topic: UnifiedTopic) => {
    setSelectedTopic(topic);
    setIsModalOpen(true);
    document.body.style.overflow = 'hidden';
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedTopic(null);
    document.body.style.overflow = '';
  };
  
  const toggleSource = (domain: string) => {
    setSelectedSources(prev => {
      if (prev.includes(domain)) {
        // Remove source if already selected
        return prev.filter(s => s !== domain);
      } else {
        // Add source if not selected
        return [...prev, domain];
      }
    });
  };

  return (
    <div className="max-w-6xl mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6 bg-gradient-to-r from-primary to-primary-dark bg-clip-text text-transparent">
        {t('analysis.title')}
      </h1>
      
      {loading && (
        <div className="flex flex-col justify-center items-center h-64 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p className="text-lg text-text-light">{t('analysis.loading')}</p>
          <DelayedLoadingMessage isLoading={loading} />
        </div>
      )}
      
      {error && (
        <div className="text-center p-6 md:p-8 bg-red-50 border-2 border-error rounded-lg max-w-3xl mx-auto">
          <p className="text-xl text-error font-semibold mb-2">{t('analysis.error')}</p>
          <p className="text-text-light bg-red-100 p-2 rounded inline-block">{error}</p>
        </div>
      )}
      
      {!loading && !error && analysis && analysis.analysis && (
        <>
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-semibold mb-2">
              {formatDate(new Date(analysis.date), language)}
            </h2>
            <p className="text-text-light">
              {analysis.analysis.unified_topics.length} {t('analysis.topicsComparison')} {countUniqueSources(analysis.analysis.unified_topics)} {t('analysis.differentSources')}
            </p>
          </div>
          
          {/* Source filters */}
          {allSources.length > 0 && (
            <div className="mb-6">
              <h3 className="font-medium text-base mb-2">{t('analysis.filterBySource')}</h3>
              <div className="flex flex-wrap gap-2">
                {allSources.map(domain => {
                  const sourceConfig = getNewsSourceConfig(domain);
                  const isSelected = selectedSources.includes(domain);
                  
                  return (
                    <button
                      key={domain}
                      onClick={() => toggleSource(domain)}
                      className={`flex items-center px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer ${
                        isSelected 
                          ? 'bg-[#2657A7] text-white'
                          : 'bg-gray-50 text-gray-700 hover:bg-[#e7edf7]'
                      }`}
                    >
                      <img 
                        src={sourceConfig.logo} 
                        alt={sourceConfig.name}
                        className="w-4 h-4 rounded-full mr-2 object-cover" 
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.src = '/hungarian_news_summary/logos/default-logo.png';
                        }}
                      />
                      {sourceConfig.name}
                    </button>
                  );
                })}
                {selectedSources.length > 0 && (
                  <button
                    onClick={() => setSelectedSources([])}
                    className="text-sm text-gray-500 hover:text-gray-700 underline ml-2 self-center cursor-pointer"
                  >
                    {t('analysis.showAll')}
                  </button>
                )}
              </div>
            </div>
          )}
          
          {/* Display filtered topics count */}
          {selectedSources.length > 0 && (
            <div className="mb-4 text-sm text-text-light">
              <p>
                {filteredTopics.length} {t('analysis.topicsShowing')} {selectedSources.length} {t('analysis.selectedSources')}
              </p>
            </div>
          )}
          
          {/* Topic cards with filtering applied */}
          {filteredTopics.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
              {filteredTopics.map((topic, index) => (
                <TopicCard 
                  key={`topic-${index}`}
                  topic={topic}
                  onClick={() => openModal(topic)}
                  highlightSources={selectedSources.length > 0 ? selectedSources : undefined}
                />
              ))}
            </div>
          ) : (
            <div className="text-center p-10 bg-background-alt rounded-lg shadow-md mb-10">
              <p className="text-xl text-text-muted">
                {selectedSources.length > 0 
                  ? t('analysis.noMatchingTopics')
                  : t('analysis.noAnalysis')}
              </p>
              {selectedSources.length > 0 && (
                <button
                  onClick={() => setSelectedSources([])}
                  className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
                >
                  {t('analysis.showAll')}
                </button>
              )}
            </div>
          )}
          
          {/* Pass selected sources to the dashboard for filtered view */}
          <SentimentDashboard 
            analysis={analysis.analysis} 
            selectedSources={selectedSources.length > 0 ? selectedSources : undefined}
          />
        </>
      )}
      
      {isModalOpen && selectedTopic && (
        <TopicAnalysisModal 
          topic={selectedTopic}
          onClose={closeModal}
          highlightSources={selectedSources.length > 0 ? selectedSources : undefined}
        />
      )}
    </div>
  );
};

// Helper function to count unique sources
const countUniqueSources = (topics: UnifiedTopic[]): number => {
  const uniqueSources = new Set<string>();
  
  topics.forEach(topic => {
    topic.source_coverage.forEach(source => {
      uniqueSources.add(source.domain);
    });
  });
  
  return uniqueSources.size;
};

export default TopicAnalysisPage;