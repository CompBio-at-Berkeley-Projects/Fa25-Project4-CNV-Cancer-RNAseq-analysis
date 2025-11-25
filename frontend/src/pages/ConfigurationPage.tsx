import React from 'react';
import { useForm } from 'react-hook-form';
import { useAnalysisContext } from '../context/AnalysisContext';
import { useRunAnalysis } from '../hooks/useAnalysis';
import { useNavigate } from 'react-router-dom';
import { AnalysisRequest, Genome, DistanceMetric, CellLine } from '../types';
import { Loader2, Play } from 'lucide-react';

const ConfigurationPage = () => {
    const { selectedFile, setAnalysisResult } = useAnalysisContext();
    const navigate = useNavigate();
    const runMutation = useRunAnalysis();
    
    const { register, handleSubmit, formState: { errors } } = useForm<AnalysisRequest>({
        defaultValues: {
            input_file: selectedFile || '',
            sample_name: 'sample_' + new Date().toISOString().slice(0, 10).replace(/-/g, ''),
            output_dir: 'backend/results',
            genome: Genome.hg20,
            ngene_chr: 5,
            LOW_DR: 0.05,
            UP_DR: 0.10,
            win_size: 25,
            KS_cut: 0.10,
            distance: DistanceMetric.euclidean,
            n_cores: 4,
            cell_line: CellLine.no,
            plot_genes: true,
        }
    });

    const onSubmit = (data: AnalysisRequest) => {
        runMutation.mutate(data, {
            onSuccess: (result) => {
                setAnalysisResult(result);
                navigate('/results');
            }
        });
    };

    if (!selectedFile) {
        return (
            <div className="text-center py-12">
                <p className="text-gray-500">Please select a file first.</p>
                <button
                    onClick={() => navigate('/')}
                    className="mt-4 px-4 py-2 text-blue-600 hover:text-blue-800 font-medium"
                >
                    Go to Upload
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">Configure Analysis</h2>
                <p className="text-gray-500">Set parameters for the CopyKAT algorithm.</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                {/* Basic Settings */}
                <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
                    <h3 className="font-semibold text-lg text-gray-900 border-b pb-2">Basic Settings</h3>
                    
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Sample Name</label>
                            <input
                                {...register('sample_name', { required: true, pattern: /^[a-zA-Z0-9_]+$/ })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                            {errors.sample_name && <span className="text-xs text-red-500">Invalid sample name</span>}
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Genome</label>
                            <select
                                {...register('genome')}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="hg20">Human (hg20)</option>
                                <option value="mm10">Mouse (mm10)</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">CPU Cores</label>
                            <input
                                type="number"
                                {...register('n_cores', { min: 1, max: 64, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Cell Line?</label>
                            <select
                                {...register('cell_line')}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Advanced Parameters */}
                <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
                    <h3 className="font-semibold text-lg text-gray-900 border-b pb-2">Advanced Parameters</h3>
                    
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Window Size</label>
                            <input
                                type="number"
                                {...register('win_size', { min: 10, max: 150, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                            <p className="text-xs text-gray-500 mt-1">Genes per window (default: 25)</p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Min Genes/Chr</label>
                            <input
                                type="number"
                                {...register('ngene_chr', { min: 1, max: 20, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Smoothing (LOW_DR)</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('LOW_DR', { min: 0.01, max: 0.5, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Segmentation (UP_DR)</label>
                            <input
                                type="number"
                                step="0.01"
                                {...register('UP_DR', { min: 0.01, max: 0.5, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex justify-end gap-4">
                    <button
                        type="button"
                        onClick={() => navigate('/')}
                        className="px-6 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition-colors"
                    >
                        Back
                    </button>
                    <button
                        type="submit"
                        disabled={runMutation.isPending}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors flex items-center gap-2"
                    >
                        {runMutation.isPending ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Running Analysis...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4" />
                                Run Analysis
                            </>
                        )}
                    </button>
                </div>

                {runMutation.isError && (
                    <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
                        <p className="font-medium">Analysis Failed</p>
                        <p className="text-sm mt-1">{runMutation.error?.message}</p>
                    </div>
                )}
            </form>
        </div>
    );
};

export default ConfigurationPage;

