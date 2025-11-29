import { useLocation } from 'react-router-dom';
import clsx from 'clsx';
import { Check } from 'lucide-react';

const steps = [
    { path: '/', label: 'Upload Data', number: 1 },
    { path: '/configure', label: 'Configure Analysis', number: 2 },
    { path: '/results', label: 'View Results', number: 3 },
];

const StepIndicator = () => {
    const location = useLocation();
    
    // Helper to determine step status
    const getStepStatus = (stepPath: string, stepIndex: number) => {
        const currentPath = location.pathname;
        const currentIndex = steps.findIndex(s => s.path === currentPath);
        
        // Special case for root path matching
        if (currentPath === '/' && stepPath === '/') return 'current';
        
        if (currentIndex === stepIndex) return 'current';
        if (currentIndex > stepIndex) return 'completed';
        return 'upcoming';
    };

    return (
        <div className="w-full py-6">
            <div className="flex items-center justify-center max-w-3xl mx-auto relative">
                {/* Connector Line */}
                <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200 -z-10 transform -translate-y-1/2 mx-16"></div>
                
                <div className="flex justify-between w-full px-4">
                    {steps.map((step, index) => {
                        const status = getStepStatus(step.path, index);
                        
                        return (
                            <div key={step.path} className="flex flex-col items-center gap-2 bg-gray-50 px-2">
                                <div 
                                    className={clsx(
                                        "w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm transition-colors duration-200 ring-4 ring-gray-50",
                                        status === 'completed' ? "bg-green-500 text-white" :
                                        status === 'current' ? "bg-blue-600 text-white" :
                                        "bg-gray-200 text-gray-500"
                                    )}
                                >
                                    {status === 'completed' ? (
                                        <Check className="w-5 h-5" />
                                    ) : (
                                        step.number
                                    )}
                                </div>
                                <span 
                                    className={clsx(
                                        "text-sm font-medium whitespace-nowrap",
                                        status === 'current' ? "text-blue-700" :
                                        status === 'completed' ? "text-green-700" :
                                        "text-gray-500"
                                    )}
                                >
                                    {step.label}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default StepIndicator;

