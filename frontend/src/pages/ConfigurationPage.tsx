import { useEffect, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { useAnalysisContext } from '../context/AnalysisContext';
import { useRunAnalysis } from '../hooks/useAnalysis';
import { useNavigate } from 'react-router-dom';
import { AnalysisRequest, Genome, DistanceMetric, CellLine } from '../types';
import { Loader2, Play, Terminal } from 'lucide-react';
import Tooltip from '../components/ui/Tooltip';
import { getAnalysisStatus } from '../api/client';

const ConfigurationPage = () => {
    const { selectedFile, analysisParams, setAnalysisParams, setAnalysisResult } = useAnalysisContext();
    const navigate = useNavigate();
    const runMutation = useRunAnalysis();
    
    // Log viewer state
    const [taskId, setTaskId] = useState<string | null>(null);
    const [logs, setLogs] = useState<string[]>([]);
    const [status, setStatus] = useState<string>('idle');
    const logsEndRef = useRef<HTMLDivElement>(null);

    const { register, handleSubmit, watch, formState: { errors } } = useForm<AnalysisRequest>({
        defaultValues: {
            input_file: selectedFile || '',
            sample_name: analysisParams.sample_name || 'sample_' + new Date().toISOString().slice(0, 10).replace(/-/g, ''),
            output_dir: analysisParams.output_dir || 'backend/results',
            genome: analysisParams.genome || Genome.hg20,
            ngene_chr: analysisParams.ngene_chr || 5,
            LOW_DR: analysisParams.LOW_DR || 0.05,
            UP_DR: analysisParams.UP_DR || 0.10,
            win_size: analysisParams.win_size || 25,
            KS_cut: analysisParams.KS_cut || 0.10,
            distance: analysisParams.distance || DistanceMetric.euclidean,
            n_cores: analysisParams.n_cores || 4,
            cell_line: analysisParams.cell_line || CellLine.no,
            plot_genes: analysisParams.plot_genes !== undefined ? analysisParams.plot_genes : true,
        }
    });

    // Update context when form values change (for persistence)
    const formValues = watch();
    useEffect(() => {
        setAnalysisParams(formValues);
    }, [JSON.stringify(formValues), setAnalysisParams]);

    // Auto-scroll logs
    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    // Poll for status
    useEffect(() => {
        let intervalId: any;
        
        if (taskId && status === 'running') {
            intervalId = setInterval(async () => {
                try {
                    const data: any = await getAnalysisStatus(taskId);
                    if (data.status === 'completed') {
                        setStatus('completed');
                        setAnalysisResult(data.result);
                        navigate('/results');
                    } else if (data.status === 'failed') {
                        setStatus('failed');
                        setLogs(prev => [...prev, `ERROR: ${data.error || 'Unknown error'}`]);
                    } else {
                        // Update logs if new ones available
                        // Since backend returns all logs, we just replace or parse
                        // For simplicity, let's assume backend returns "logs" list
                        // But our updated backend returns "logs" which is a list of strings
                        if (data.logs) {
                            setLogs(data.logs);
                        }
                    }
                } catch (e) {
                    console.error("Polling error", e);
                }
            }, 1000); // Poll every second
        }

        return () => clearInterval(intervalId);
    }, [taskId, status, navigate, setAnalysisResult]);

    const onSubmit = (data: AnalysisRequest) => {
        setStatus('running');
        setLogs(['Initializing analysis...', 'Sending request to backend...']);
        
        runMutation.mutate(data, {
            onSuccess: (response: unknown) => {
                const res = response as { task_id?: string; success?: boolean; error?: string };
                // Check if response has task_id (async) or full result (sync legacy)
                if (res.task_id) {
                    setTaskId(res.task_id);
                    setLogs(prev => [...prev, `Task started: ${res.task_id}`, 'Waiting for logs...']);
                } else if (res.success) {
                    // Legacy sync response
                    setAnalysisResult(res as unknown as import('../types').AnalysisResult);
                    navigate('/results');
                } else {
                    setStatus('failed');
                    setLogs(prev => [...prev, `Immediate failure: ${res.error}`]);
                }
            },
            onError: (error) => {
                setStatus('failed');
                setLogs(prev => [...prev, `Request failed: ${error.message}`]);
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

    // Live Execution View
    if (status === 'running' || status === 'failed') {
        return (
            <div className="max-w-4xl mx-auto space-y-6">
                 <div>
                    <h2 className="text-2xl font-bold text-gray-900">Running Analysis</h2>
                    <p className="text-gray-500">
                        {status === 'running' ? 'Processing your data. This may take a few minutes.' : 'Analysis failed. Please check the logs below.'}
                    </p>
                </div>

                <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg border border-gray-800 font-mono text-sm">
                    <div className="bg-gray-800 px-4 py-2 flex items-center gap-2 border-b border-gray-700">
                        <Terminal className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-200">Analysis Logs</span>
                        {status === 'running' && <Loader2 className="w-3 h-3 text-blue-400 animate-spin ml-auto" />}
                    </div>
                    <div className="p-4 h-96 overflow-y-auto text-gray-300 space-y-1">
                        {logs.map((log, i) => (
                            <div key={i} className="break-words border-l-2 border-transparent hover:border-gray-700 pl-2">
                                <span className="text-gray-500 select-none mr-2">
                                    {new Date().toLocaleTimeString()} &gt;
                                </span>
                                {log}
                            </div>
                        ))}
                        <div ref={logsEndRef} />
                    </div>
                </div>
                
                {status === 'failed' && (
                    <div className="flex justify-end">
                        <button
                            onClick={() => { setStatus('idle'); setLogs([]); setTaskId(null); }}
                            className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                        >
                            Back to Configuration
                        </button>
                    </div>
                )}
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
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Sample Name</label>
                                <Tooltip content="A unique identifier for this analysis run. Used in output filenames." />
                            </div>
                            <input
                                {...register('sample_name', { required: true, pattern: /^[a-zA-Z0-9_]+$/ })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                            {errors.sample_name && <span className="text-xs text-red-500">Invalid sample name (alphanumeric and underscores only)</span>}
                        </div>
                        
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Genome</label>
                                <Tooltip content="Reference genome for chromosome coordinates." />
                            </div>
                            <select
                                {...register('genome')}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="hg20">Human (hg20)</option>
                                <option value="mm10">Mouse (mm10)</option>
                            </select>
                        </div>

                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">CPU Cores</label>
                                <Tooltip content="Number of processor cores to use for parallel processing." />
                            </div>
                            <input
                                type="number"
                                {...register('n_cores', { min: 1, max: 64, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>

                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Cell Line?</label>
                                <Tooltip content="Set to 'Yes' if analyzing cell line data (uses different baseline assumptions)." />
                            </div>
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
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Window Size</label>
                                <Tooltip content="Number of genes per window for smoothing. Smaller values = higher resolution but more noise." />
                            </div>
                            <input
                                type="number"
                                {...register('win_size', { min: 10, max: 150, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                            <p className="text-xs text-gray-500 mt-1">Genes per window (default: 25)</p>
                        </div>

                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Min Genes/Chr</label>
                                <Tooltip content="Minimum number of genes required per chromosome to include it in analysis." />
                            </div>
                            <input
                                type="number"
                                {...register('ngene_chr', { min: 1, max: 20, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>

                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Smoothing (LOW_DR)</label>
                                <Tooltip content="Threshold for outlier removal during smoothing. Must be <= UP_DR." />
                            </div>
                            <input
                                type="number"
                                step="0.01"
                                {...register('LOW_DR', { min: 0.01, max: 0.5, valueAsNumber: true })}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>

                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Segmentation (UP_DR)</label>
                                <Tooltip content="Threshold for segmentation. Higher values result in fewer segments." />
                            </div>
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
                        <Play className="w-4 h-4" />
                        Run Analysis
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
