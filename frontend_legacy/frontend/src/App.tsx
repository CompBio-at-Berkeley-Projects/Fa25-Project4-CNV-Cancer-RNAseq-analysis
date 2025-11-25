import { useState } from 'react';
import { UploadStep } from './components/UploadStep';
import { ConfigureStep } from './components/ConfigureStep';
import { ResultsView } from './components/ResultsView';
import { useAnalysis } from './hooks/useAnalysis';

function App() {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const { 
    uploadFile, 
    runAnalysis, 
    isUploading, 
    isRunning, 
    uploadError, 
    analysisError, 
    uploadedFilePath,
    results,
    reset 
  } = useAnalysis();

  const handleNext = () => setStep(2);
  
  const handleRun = async (config: any) => {
    try {
      await runAnalysis(config);
      setStep(3);
    } catch (e) {
      console.error(e);
      // Error is handled in hook state
    }
  };

  const handleReset = () => {
    reset();
    setStep(1);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🧬</span>
            <h1 className="text-2xl font-bold text-gray-800">CopyKAT Analysis</h1>
          </div>
          <div className="text-sm text-gray-500">
            v1.0 • React + FastAPI
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="max-w-3xl mx-auto mt-8 mb-8 px-4">
        <div className="flex justify-between relative">
          <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 rounded"></div>
          <StepIndicator number={1} label="Upload" active={step >= 1} current={step === 1} />
          <StepIndicator number={2} label="Configure" active={step >= 2} current={step === 2} />
          <StepIndicator number={3} label="Results" active={step >= 3} current={step === 3} />
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {step === 1 && (
          <UploadStep 
            onUpload={uploadFile} 
            isUploading={isUploading}
            error={uploadError}
            uploadedFileName={uploadedFilePath ? uploadedFilePath.split('/').pop() || 'file' : null}
            onNext={handleNext}
          />
        )}

        {step === 2 && (
          <ConfigureStep 
            onRun={handleRun}
            isRunning={isRunning}
            error={analysisError}
          />
        )}

        {step === 3 && results && (
          <ResultsView 
            results={results}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  );
}

const StepIndicator = ({ number, label, active, current }: { number: number, label: string, active: boolean, current: boolean }) => (
  <div className="flex flex-col items-center bg-gray-50 px-2">
    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold mb-2 transition-colors
      ${current ? 'bg-blue-600 text-white ring-4 ring-blue-100' : 
        active ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-500'}`}>
      {active && !current ? '✓' : number}
    </div>
    <span className={`text-sm font-medium ${current ? 'text-blue-600' : 'text-gray-500'}`}>
      {label}
    </span>
  </div>
);

export default App;
