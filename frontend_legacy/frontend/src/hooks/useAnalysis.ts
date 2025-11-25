import { useState } from 'react';
import { api } from '../api/client';
import { AnalysisRequest, AnalysisResponse } from '../api/types';

export const useAnalysis = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [uploadedFilePath, setUploadedFilePath] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResponse | null>(null);

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    try {
      const response = await api.uploadFile(file);
      setUploadedFilePath(response.path);
      return response;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || "Upload failed";
      setUploadError(msg);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  const runAnalysis = async (config: Omit<AnalysisRequest, 'input_file' | 'output_dir'>) => {
    if (!uploadedFilePath) {
      setAnalysisError("No file uploaded");
      return;
    }

    setIsRunning(true);
    setAnalysisError(null);
    setResults(null);

    try {
      // Construct full request with server-side paths
      const request: AnalysisRequest = {
        ...config,
        input_file: uploadedFilePath,
        output_dir: 'backend/results' // Fixed output dir for simplicity
      };

      const response = await api.runAnalysis(request);
      setResults(response);
      
      if (!response.success) {
        setAnalysisError(response.error || "Analysis failed without error message");
      }
      
      return response;
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || "Analysis failed";
      setAnalysisError(msg);
      throw err;
    } finally {
      setIsRunning(false);
    }
  };

  return {
    uploadFile,
    runAnalysis,
    isUploading,
    isRunning,
    uploadError,
    analysisError,
    uploadedFilePath,
    results,
    reset: () => {
      setResults(null);
      setAnalysisError(null);
      setUploadError(null);
    }
  };
};

