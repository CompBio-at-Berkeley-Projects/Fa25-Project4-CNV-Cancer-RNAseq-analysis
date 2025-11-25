import React, { useState } from 'react';
import { useFiles, useUploadFile } from '../hooks/useFiles';
import { useAnalysisContext } from '../context/AnalysisContext';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import clsx from 'clsx';

const UploadPage = () => {
    const { data: files, isLoading } = useFiles();
    const uploadMutation = useUploadFile();
    const { selectedFile, setSelectedFile } = useAnalysisContext();
    const navigate = useNavigate();
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleUpload(e.dataTransfer.files[0]);
        }
    };

    const handleUpload = (file: File) => {
        uploadMutation.mutate(file, {
            onSuccess: (data) => {
                setSelectedFile(data.path);
            }
        });
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Upload Data</h2>
                <p className="text-gray-500">Upload your single-cell RNA-seq expression matrix (genes x cells).</p>
            </div>

            {/* Upload Area */}
            <div
                className={clsx(
                    "border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer",
                    dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400 bg-white"
                )}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
                    accept=".txt,.csv,.tsv,.gz"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center gap-4">
                        {uploadMutation.isPending ? (
                            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
                        ) : (
                            <UploadCloud className="w-12 h-12 text-gray-400" />
                        )}
                        <div>
                            <p className="text-lg font-medium text-gray-900">
                                {uploadMutation.isPending ? "Uploading..." : "Click or drag file to upload"}
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                                Supported formats: .txt, .csv, .tsv, .gz
                            </p>
                        </div>
                    </div>
                </label>
                {uploadMutation.isError && (
                    <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg flex items-center justify-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        Upload failed. Please try again.
                    </div>
                )}
            </div>

            {/* File List */}
            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
                <div className="px-6 py-4 border-b bg-gray-50">
                    <h3 className="font-medium text-gray-900">Available Files</h3>
                </div>
                <div className="divide-y">
                    {isLoading ? (
                        <div className="p-8 text-center text-gray-500">Loading files...</div>
                    ) : files?.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">No files available</div>
                    ) : (
                        files?.map((file) => (
                            <div
                                key={file.path}
                                onClick={() => setSelectedFile(file.path)}
                                className={clsx(
                                    "px-6 py-4 flex items-center justify-between cursor-pointer transition-colors",
                                    selectedFile === file.path ? "bg-blue-50" : "hover:bg-gray-50"
                                )}
                            >
                                <div className="flex items-center gap-3">
                                    <FileText className="w-5 h-5 text-gray-400" />
                                    <div>
                                        <p className="font-medium text-gray-900">{file.name}</p>
                                        <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 uppercase">
                                            {file.type}
                                        </span>
                                    </div>
                                </div>
                                {selectedFile === file.path && (
                                    <CheckCircle className="w-5 h-5 text-blue-600" />
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className="flex justify-end">
                <button
                    onClick={() => navigate('/configure')}
                    disabled={!selectedFile}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
                >
                    Next: Configure Analysis
                </button>
            </div>
        </div>
    );
};

export default UploadPage;

