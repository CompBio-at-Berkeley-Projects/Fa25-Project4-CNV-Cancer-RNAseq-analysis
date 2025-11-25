import React, { useCallback } from 'react';

interface UploadStepProps {
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
  error: string | null;
  uploadedFileName: string | null;
  onNext: () => void;
}

export const UploadStep: React.FC<UploadStepProps> = ({ 
  onUpload, 
  isUploading, 
  error, 
  uploadedFileName,
  onNext
}) => {
  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await onUpload(e.target.files[0]);
    }
  }, [onUpload]);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">1. Upload Expression Matrix</h2>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
        <input
          type="file"
          id="file-upload"
          className="hidden"
          onChange={handleFileChange}
          accept=".txt,.csv,.tsv,.gz"
          disabled={isUploading}
        />
        <label 
          htmlFor="file-upload" 
          className="cursor-pointer flex flex-col items-center justify-center"
        >
          <div className="text-4xl mb-2">📤</div>
          <span className="text-blue-600 font-medium text-lg">
            {isUploading ? 'Uploading...' : 'Click to Upload File'}
          </span>
          <p className="text-gray-500 mt-2 text-sm">
            Supported formats: .txt, .csv, .tsv, .gz (Genes x Cells)
          </p>
        </label>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
          ⚠️ {error}
        </div>
      )}

      {uploadedFileName && (
        <div className="mt-6">
          <div className="p-3 bg-green-50 text-green-700 rounded-md border border-green-200 flex items-center justify-between">
             <span>✅ Uploaded: <strong>{uploadedFileName}</strong></span>
          </div>
          <button
            onClick={onNext}
            className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors font-medium"
          >
            Continue to Configuration →
          </button>
        </div>
      )}
    </div>
  );
};

