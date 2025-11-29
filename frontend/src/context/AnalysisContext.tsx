import { createContext, useContext, useState, ReactNode } from 'react';
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

const STORAGE_KEYS = {
    SELECTED_FILE: 'copykat_selected_file',
    ANALYSIS_PARAMS: 'copykat_analysis_params',
    ANALYSIS_RESULT: 'copykat_analysis_result',
};

export const AnalysisProvider = ({ children }: { children: ReactNode }) => {
    // Initialize state from localStorage
    const [selectedFile, setSelectedFileState] = useState<string | null>(() => {
        const stored = localStorage.getItem(STORAGE_KEYS.SELECTED_FILE);
        return stored ? JSON.parse(stored) : null;
    });

    const [analysisParams, setAnalysisParamsState] = useState<Partial<AnalysisRequest>>(() => {
        const stored = localStorage.getItem(STORAGE_KEYS.ANALYSIS_PARAMS);
        return stored ? JSON.parse(stored) : {};
    });

    const [analysisResult, setAnalysisResultState] = useState<AnalysisResult | null>(() => {
        const stored = localStorage.getItem(STORAGE_KEYS.ANALYSIS_RESULT);
        return stored ? JSON.parse(stored) : null;
    });

    // Wrapper setters to update localStorage
    const setSelectedFile = (path: string | null) => {
        setSelectedFileState(path);
        if (path) {
            localStorage.setItem(STORAGE_KEYS.SELECTED_FILE, JSON.stringify(path));
        } else {
            localStorage.removeItem(STORAGE_KEYS.SELECTED_FILE);
        }
    };

    const setAnalysisParams = (params: Partial<AnalysisRequest>) => {
        setAnalysisParamsState(params);
        localStorage.setItem(STORAGE_KEYS.ANALYSIS_PARAMS, JSON.stringify(params));
    };

    const setAnalysisResult = (result: AnalysisResult | null) => {
        setAnalysisResultState(result);
        if (result) {
            localStorage.setItem(STORAGE_KEYS.ANALYSIS_RESULT, JSON.stringify(result));
        } else {
            localStorage.removeItem(STORAGE_KEYS.ANALYSIS_RESULT);
        }
    };

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
