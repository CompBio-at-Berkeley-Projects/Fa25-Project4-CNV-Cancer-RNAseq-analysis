import React from 'react';
import { AnalysisResponse } from '../api/types';

interface ResultsViewProps {
  results: AnalysisResponse;
  onReset: () => void;
}

const SERVER_URL = 'http://localhost:8000';

export const ResultsView: React.FC<ResultsViewProps> = ({ results, onReset }) => {
  // Helper to format server paths to URLs
  const getUrl = (path?: string) => {
    if (!path) return undefined;
    // Assume backend/results/... path, map to /results/...
    // Replace 'backend/results' with '/results'
    return `${SERVER_URL}${path.replace('backend', '')}`;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <h2 className="text-2xl font-bold text-gray-800">Analysis Results</h2>
        <button 
          onClick={onReset}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          ← New Analysis
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Summary Stats */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">Summary Statistics</h3>
            <div className="space-y-2">
              <StatRow label="Total Cells" value={results.summary.n_cells} />
              <StatRow label="Aneuploid" value={results.summary.n_aneuploid} />
              <StatRow label="Diploid" value={results.summary.n_diploid} />
              <StatRow label="Undefined" value={results.summary.n_not_defined} />
              <div className="pt-2 mt-2 border-t border-blue-200">
                <StatRow label="Aneuploid Fraction" value={`${((results.summary.aneuploid_fraction || 0) * 100).toFixed(1)}%`} />
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Downloads</h3>
            <div className="flex flex-col space-y-2">
              <DownloadLink label="Predictions (TXT)" url={getUrl(results.files.predictions)} />
              <DownloadLink label="CNA Results (TXT)" url={getUrl(results.files.cna_results)} />
              <DownloadLink label="Heatmap (JPEG)" url={getUrl(results.files.heatmap)} />
            </div>
          </div>
        </div>

        {/* Visualizations */}
        <div className="lg:col-span-2 space-y-6">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-gray-700 mb-2">CNV Heatmap</h3>
            {results.files.heatmap ? (
              <img 
                src={getUrl(results.files.heatmap)} 
                alt="CNV Heatmap" 
                className="w-full h-auto rounded shadow-sm"
              />
            ) : (
              <div className="h-64 flex items-center justify-center bg-gray-100 text-gray-400">
                No heatmap generated
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatRow = ({ label, value }: { label: string, value: any }) => (
  <div className="flex justify-between items-center text-sm">
    <span className="text-gray-600">{label}</span>
    <span className="font-bold text-gray-900">{value ?? 'N/A'}</span>
  </div>
);

const DownloadLink = ({ label, url }: { label: string, url?: string }) => {
  if (!url) return null;
  return (
    <a 
      href={url} 
      target="_blank" 
      rel="noopener noreferrer"
      className="text-blue-600 hover:text-blue-800 hover:underline text-sm flex items-center"
    >
      📄 {label}
    </a>
  );
};

