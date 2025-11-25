import React from 'react';
import { useAnalysisContext } from '../context/AnalysisContext';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Download, BarChart2, PieChart } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const getResultUrl = (filePath: string | undefined): string | null => {
    if (!filePath) return null;
    const match = filePath.match(/backend\/results\/(.+)/);
    return match ? `${API_BASE_URL}/results/${match[1]}` : null;
};

const ResultsPage = () => {
    const { analysisResult } = useAnalysisContext();
    const navigate = useNavigate();

    if (!analysisResult) {
        return (
            <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                    <BarChart2 className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">No Results Yet</h3>
                <p className="text-gray-500 mt-1">Run an analysis to see results here.</p>
                <button
                    onClick={() => navigate('/configure')}
                    className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                    Start Analysis
                </button>
            </div>
        );
    }

    if (!analysisResult.success) {
        return (
            <div className="max-w-3xl mx-auto mt-8">
                <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                    <div className="flex items-start gap-4">
                        <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0" />
                        <div>
                            <h3 className="text-lg font-medium text-red-900">Analysis Failed</h3>
                            <p className="mt-1 text-red-700">{analysisResult.error}</p>
                            <button
                                onClick={() => navigate('/configure')}
                                className="mt-4 px-4 py-2 bg-white border border-red-300 text-red-700 rounded-lg hover:bg-red-50 text-sm font-medium"
                            >
                                Try Again
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
                    <p className="text-gray-500">Analysis completed in {analysisResult.runtime_minutes.toFixed(2)} minutes</p>
                </div>
                <div className="flex gap-2">
                    {getResultUrl(analysisResult.files.predictions) && (
                        <a
                            href={getResultUrl(analysisResult.files.predictions)!}
                            download
                            className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700"
                        >
                            <Download className="w-4 h-4" />
                            Predictions
                        </a>
                    )}
                    {getResultUrl(analysisResult.files.cna_results) && (
                        <a
                            href={getResultUrl(analysisResult.files.cna_results)!}
                            download
                            className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700"
                        >
                            <Download className="w-4 h-4" />
                            CNA Data
                        </a>
                    )}
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-xl shadow-sm border">
                    <p className="text-sm font-medium text-gray-500">Total Cells</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{analysisResult.summary.n_cells}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border">
                    <p className="text-sm font-medium text-gray-500">Aneuploid</p>
                    <p className="text-3xl font-bold text-amber-600 mt-2">{analysisResult.summary.n_aneuploid}</p>
                    <p className="text-xs text-gray-500 mt-1">{(analysisResult.summary.aneuploid_fraction * 100).toFixed(1)}%</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border">
                    <p className="text-sm font-medium text-gray-500">Diploid</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{analysisResult.summary.n_diploid}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border">
                    <p className="text-sm font-medium text-gray-500">Undefined</p>
                    <p className="text-3xl font-bold text-gray-400 mt-2">{analysisResult.summary.n_not_defined}</p>
                </div>
            </div>

            {/* Heatmap */}
            {getResultUrl(analysisResult.files.heatmap) && (
                <div className="bg-white p-6 rounded-xl shadow-sm border">
                    <h3 className="font-semibold text-lg text-gray-900 mb-4 flex items-center gap-2">
                        <PieChart className="w-5 h-5 text-gray-500" />
                        CNV Heatmap
                    </h3>
                    <div className="aspect-video bg-gray-50 rounded-lg overflow-hidden flex items-center justify-center">
                         <img
                            src={getResultUrl(analysisResult.files.heatmap)!}
                            alt="CNV Heatmap"
                            className="max-w-full max-h-full object-contain"
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ResultsPage;

