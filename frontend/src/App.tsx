import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import UploadPage from './pages/UploadPage';
import ConfigurationPage from './pages/ConfigurationPage';
import ResultsPage from './pages/ResultsPage';
import { AnalysisProvider } from './context/AnalysisContext';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AnalysisProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<UploadPage />} />
              <Route path="configure" element={<ConfigurationPage />} />
              <Route path="results" element={<ResultsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AnalysisProvider>
    </QueryClientProvider>
  );
}

export default App;
