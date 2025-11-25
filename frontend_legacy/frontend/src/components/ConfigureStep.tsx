import React, { useState } from 'react';
import { AnalysisRequest } from '../api/types';

interface ConfigureStepProps {
  onRun: (config: Omit<AnalysisRequest, 'input_file' | 'output_dir'>) => Promise<void>;
  isRunning: boolean;
  error: string | null;
}

const DEFAULT_CONFIG: Omit<AnalysisRequest, 'input_file' | 'output_dir'> = {
  sample_name: 'sample_001',
  genome: 'hg20',
  ngene_chr: 5,
  LOW_DR: 0.05,
  UP_DR: 0.10,
  win_size: 25,
  n_cores: 4,
  distance: 'euclidean',
  cell_line: 'no',
  plot_genes: true
};

export const ConfigureStep: React.FC<ConfigureStepProps> = ({ onRun, isRunning, error }) => {
  const [config, setConfig] = useState(DEFAULT_CONFIG);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let finalValue: any = value;

    if (type === 'number') {
      finalValue = parseFloat(value);
    } else if (type === 'checkbox') {
      finalValue = (e.target as HTMLInputElement).checked;
    }

    setConfig(prev => ({ ...prev, [name]: finalValue }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onRun(config);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-6 text-gray-800">2. Configure Analysis</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Essential Parameters */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-700 border-b pb-2">Core Settings</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Sample Name</label>
              <input
                type="text"
                name="sample_name"
                value={config.sample_name}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Genome</label>
              <select
                name="genome"
                value={config.genome}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
              >
                <option value="hg20">Human (hg20)</option>
                <option value="mm10">Mouse (mm10)</option>
              </select>
            </div>
          </div>

          {/* Advanced Parameters */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-700 border-b pb-2">Algorithm Parameters</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Window Size</label>
                <input
                  type="number"
                  name="win_size"
                  value={config.win_size}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">CPU Cores</label>
                <input
                  type="number"
                  name="n_cores"
                  value={config.n_cores}
                  onChange={handleChange}
                  max={64}
                  min={1}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2"
                />
              </div>
            </div>

            <div>
               <label className="block text-sm font-medium text-gray-700">Smoothing (LOW_DR)</label>
               <input
                 type="number"
                 name="LOW_DR"
                 value={config.LOW_DR}
                 onChange={handleChange}
                 step="0.01"
                 className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2"
               />
            </div>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
            ⚠️ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isRunning}
          className={`w-full py-3 px-4 rounded-md text-white font-medium text-lg transition-colors
            ${isRunning 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-green-600 hover:bg-green-700'
            }`}
        >
          {isRunning ? 'Running Analysis...' : '🚀 Run CopyKAT Analysis'}
        </button>
      </form>
    </div>
  );
};

