import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { CrossSourceAnalysisResponse, UnifiedTopic } from '../types/analysis';
import { API_URL } from '../config';
import TopicCard from './TopicCard';
import TopicAnalysisModal from './TopicAnalysisModal';
import { formatDate } from '../utils/dateUtils';

const TopicAnalysisPage: React.FC = () => {
  const [analysis, setAnalysis] = useState<CrossSourceAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<UnifiedTopic | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const dateParam = queryParams.get('date');

  useEffect(() => {
    const fetchAnalysis = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const url = dateParam 
          ? `${API_URL}/cross-source-analysis?date=${dateParam}`
          : `${API_URL}/cross-source-analysis`;
          
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data: CrossSourceAnalysisResponse = await response.json();
        
        if (data.success && data.analysis) {
          setAnalysis(data);
        } else {
          setError(data.message || 'Nem sikerült betölteni az elemzést');
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Hiba történt az adatok lekérése közben';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalysis();
  }, [dateParam]);

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

  return (
    <div className="max-w-6xl mx-auto px-4">
      <h1 className="text-3xl font-bold mb-6 bg-gradient-to-r from-primary to-primary-dark bg-clip-text text-transparent">
        Hírforrások Összehasonlító Elemzése
      </h1>
      
      {loading && (
        <div className="flex flex-col justify-center items-center h-64 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p className="text-lg text-text-light">Elemzés betöltése...</p>
        </div>
      )}
      
      {error && (
        <div className="text-center p-6 md:p-8 bg-red-50 border-2 border-error rounded-lg max-w-3xl mx-auto">
          <p className="text-xl text-error font-semibold mb-2">Hoppá! Hiba történt:</p>
          <p className="text-text-light bg-red-100 p-2 rounded inline-block">{error}</p>
        </div>
      )}
      
      {!loading && !error && analysis && analysis.analysis && (
        <>
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-semibold mb-2">
              {formatDate(new Date(analysis.date))}
            </h2>
            <p className="text-text-light">
              {analysis.analysis.unified_topics.length} téma összehasonlítása {countUniqueSources(analysis.analysis.unified_topics)} különböző hírforrásból
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
            {analysis.analysis.unified_topics.map((topic, index) => (
              <TopicCard 
                key={`topic-${index}`}
                topic={topic}
                onClick={() => openModal(topic)}
              />
            ))}
          </div>
          
          {analysis.analysis.unified_topics.length === 0 && (
            <div className="text-center p-10 bg-background-alt rounded-lg shadow-md">
              <p className="text-xl text-text-muted">Erre a napra nem találtunk elemzést a témákról.</p>
            </div>
          )}
        </>
      )}
      
      {isModalOpen && selectedTopic && (
        <TopicAnalysisModal 
          topic={selectedTopic}
          onClose={closeModal}
        />
      )}
    </div>
  );
};

// Helper to count unique sources across all topics
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