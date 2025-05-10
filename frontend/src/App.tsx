import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import SummaryCard from './components/SummaryCard';
import SummaryModal from './components/SummaryModal';
import AboutPage from './components/AboutPage';
import TopicAnalysisPage from './components/TopicAnalysisPage';
import { Summary, SummaryApiResponse } from './types';
import { API_URL } from './config';
import DelayedLoadingMessage from './components/DelayedLoadingMessage';

// Homepage component
const HomePage = () => {
  const [summaries, setSummaries] = useState<Summary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSummary, setSelectedSummary] = useState<Summary | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  useEffect(() => {
    const fetchSummaries = async () => {
      setLoading(true);
      setError(null);
      try {
        console.log("API URL:", API_URL);
        const response = await fetch(`${API_URL}/summaries?language=hu`);
        if (!response.ok) {
          let errorDetail = `HTTP error! status: ${response.status}`;
          try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorDetail;
          } catch (parseError) {
            console.warn("Could not parse error response:", parseError);
          }
          throw new Error(errorDetail);
        }
        const data: SummaryApiResponse = await response.json();
        if (data.success && Array.isArray(data.summaries)) {
          setSummaries(data.summaries);
        } else {
          console.error("API response format incorrect:", data);
          throw new Error('Invalid data format received from API');
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
        console.error("Fetching summaries failed:", errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };
    fetchSummaries();
  }, []);

  // Modal control functions
  const openModal = (summary: Summary) => {
    setSelectedSummary(summary);
    setIsModalOpen(true);
    document.body.style.overflow = 'hidden';
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedSummary(null);
    document.body.style.overflow = '';
  };

  // Add keyboard support for closing modal
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isModalOpen) {
        closeModal();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isModalOpen]);

  return (
    <>
      <main className="flex-grow w-full">
        {loading && (
          <div className="flex flex-col justify-center items-center h-64 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
            <p className="text-lg text-text-light">
              Összefoglalók betöltése...
            </p>
            <DelayedLoadingMessage isLoading={loading} />
          </div>
        )}
        
        {error && (
          <div className="text-center p-6 md:p-8 bg-red-50 border-2 border-error rounded-lg max-w-2xl mx-auto">
            <p className="text-xl text-error font-semibold mb-2">Hoppá! Hiba történt:</p>
            <p className="text-text-light bg-red-100 p-2 rounded inline-block">{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
            {summaries.length > 0 ? (
              summaries.map((summary, index) => (
                <SummaryCard
                  key={summary.domain + summary.date}
                  summary={summary}
                  index={index}
                  onCardClick={() => openModal(summary)}
                />
              ))
            ) : (
              <p className="text-center text-xl text-text-muted py-12 md:col-span-2 lg:col-span-3">
                Jelenleg nincsenek elérhető összefoglalók erre a napra. Nézz vissza később!
              </p>
            )}
          </div>
        )}
      </main>

      {isModalOpen && <SummaryModal summary={selectedSummary} onClose={closeModal} />}
    </>
  );
};

function App() {
  return (
    <Router basename="/hungarian_news_summary">
      <div className="max-w-screen-xl mx-auto px-4 py-6 md:px-8 md:py-10 min-h-screen flex flex-col">
        <Header />
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/analysis" element={<TopicAnalysisPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        
        <Footer />
      </div>
    </Router>
  );
}

export default App;