import { useQuery } from '@tanstack/react-query';
import { fetchAnalyses, fetchAnalysisResult } from '../api/client';
import { useAnalysisContext } from '../context/AnalysisContext';
import { useNavigate } from 'react-router-dom';
import { History, Clock, FileText, ChevronRight, Loader2 } from 'lucide-react';
import { AnalysisResult } from '../types';

const HistoryPage = () => {
    const { setAnalysisResult } = useAnalysisContext();
    const navigate = useNavigate();

    const { data: analyses, isLoading } = useQuery({
        queryKey: ['analyses'],
        queryFn: fetchAnalyses,
    });

    const handleSelectAnalysis = async (analysisId: string) => {
        try {
            const result = await fetchAnalysisResult(analysisId);
            setAnalysisResult(result as AnalysisResult);
            navigate('/results');
        } catch (error) {
            console.error("Failed to load analysis:", error);
            // Optionally add toast notification here
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                    <History className="w-6 h-6 text-blue-600" />
                    Analysis History
                </h2>
                <p className="text-gray-500">View results from previous CopyKAT runs.</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
                <div className="px-6 py-4 border-b bg-gray-50 flex justify-between items-center">
                    <h3 className="font-medium text-gray-900">Completed Analyses</h3>
                    <span className="text-xs text-gray-500">{analyses?.length || 0} runs found</span>
                </div>
                
                <div className="divide-y">
                    {isLoading ? (
                        <div className="p-12 flex flex-col items-center text-gray-500">
                            <Loader2 className="w-8 h-8 animate-spin mb-2" />
                            Loading history...
                        </div>
                    ) : !analyses || analyses.length === 0 ? (
                        <div className="p-12 text-center text-gray-500">
                            No past analyses found.
                        </div>
                    ) : (
                        analyses.map((analysisId: string) => (
                            <div
                                key={analysisId}
                                onClick={() => handleSelectAnalysis(analysisId)}
                                className="px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors group"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="bg-blue-100 p-2 rounded-lg text-blue-600">
                                        <FileText className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                                            {analysisId}
                                        </p>
                                        <div className="flex items-center gap-4 mt-1">
                                            <span className="text-xs text-gray-500 flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {/* Try to parse timestamp from folder name if possible, else just show ID */}
                                                {analysisId.split('_').pop() || 'Unknown Date'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-gray-500" />
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default HistoryPage;



