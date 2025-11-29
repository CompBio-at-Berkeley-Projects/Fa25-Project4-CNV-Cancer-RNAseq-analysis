import React, { useState } from 'react';
import { Info } from 'lucide-react';

interface TooltipProps {
    content: string;
    children?: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
    const [isVisible, setIsVisible] = useState(false);

    return (
        <div 
            className="relative inline-flex items-center"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
        >
            {children || <Info className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help" />}
            
            {isVisible && (
                <div className="absolute z-50 w-64 p-2 mt-2 text-xs font-medium text-white bg-gray-900 rounded-lg shadow-sm bottom-full left-1/2 transform -translate-x-1/2 mb-2">
                    {content}
                    <div className="absolute top-100 left-1/2 -ml-1 border-4 border-transparent border-t-gray-900"></div>
                </div>
            )}
        </div>
    );
};

export default Tooltip;

