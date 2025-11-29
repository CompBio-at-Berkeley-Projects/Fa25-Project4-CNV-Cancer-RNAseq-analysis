import axios from 'axios';

// In production (Docker), use relative URL that nginx proxies
// In development, use the full backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const uploadFile = async (file: File): Promise<{ filename: string; path: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const fetchFiles = async () => {
    const response = await apiClient.get('/files');
    return response.data;
};

export const runAnalysis = async (params: unknown) => {
    const response = await apiClient.post('/run', params);
    return response.data;
};

export const getAnalysisStatus = async (taskId: string) => {
    const response = await apiClient.get(`/status/${taskId}`);
    return response.data;
};

export const fetchAnalyses = async () => {
    const response = await apiClient.get('/analyses');
    return response.data;
};

export const fetchAnalysisResult = async (analysisId: string) => {
    const response = await apiClient.get(`/results/${analysisId}`);
    return response.data;
};
