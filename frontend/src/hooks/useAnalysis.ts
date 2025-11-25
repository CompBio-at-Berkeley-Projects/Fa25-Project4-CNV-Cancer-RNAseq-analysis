import { useMutation } from '@tanstack/react-query';
import { runAnalysis } from '../api/client';
import { AnalysisRequest, AnalysisResult } from '../types';

export const useRunAnalysis = () => {
    return useMutation<AnalysisResult, Error, AnalysisRequest>({
        mutationFn: (params: AnalysisRequest) => runAnalysis(params),
    });
};

