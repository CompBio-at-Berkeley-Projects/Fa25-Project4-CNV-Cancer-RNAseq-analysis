import React, { createContext, useContext, useState, ReactNode } from 'react';
import { AnalysisRequest, AnalysisResult } from '../types';

interface AnalysisContextType {
    selectedFile: string | null;
    setSelectedFile: (path: string | null) => void;
    analysisParams: Partial<AnalysisRequest>;
    setAnalysisParams: (params: Partial<AnalysisRequest>) => void;
    analysisResult: AnalysisResult | null;
    setAnalysisResult: (result: AnalysisResult | null) => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export const AnalysisProvider = ({ children }: { children: ReactNode }) => {
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [analysisParams, setAnalysisParams] = useState<Partial<AnalysisRequest>>({});
    const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

    return (
        <AnalysisContext.Provider value={{
            selectedFile,
            setSelectedFile,
            analysisParams,
            setAnalysisParams,
            analysisResult,
            setAnalysisResult
        }}>
            {children}
        </AnalysisContext.Provider>
    );
};

export const useAnalysisContext = () => {
    const context = useContext(AnalysisContext);
    if (context === undefined) {
        throw new Error('useAnalysisContext must be used within an AnalysisProvider');
    }
    return context;
};

