import React, { useEffect } from 'react';
import { X, ZoomIn } from 'lucide-react';

interface ImageModalProps {
    src: string;
    alt: string;
}

const ImageModal: React.FC<ImageModalProps> = ({ src, alt }) => {
    const [isOpen, setIsOpen] = React.useState(false);

    // Close on escape key
    useEffect(() => {
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setIsOpen(false);
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, []);

    if (!isOpen) {
        return (
            <div 
                className="relative group cursor-pointer inline-block"
                onClick={() => setIsOpen(true)}
            >
                <img 
                    src={src} 
                    alt={alt} 
                    className="max-w-full h-auto rounded-lg shadow-sm hover:shadow-md transition-shadow"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all rounded-lg flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 bg-white p-2 rounded-full shadow-lg transform translate-y-2 group-hover:translate-y-0 transition-all">
                        <ZoomIn className="w-5 h-5 text-gray-700" />
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-80 p-4" onClick={() => setIsOpen(false)}>
            <div className="relative max-w-7xl max-h-[90vh] w-full h-full flex items-center justify-center">
                <button 
                    onClick={(e) => { e.stopPropagation(); setIsOpen(false); }}
                    className="absolute top-4 right-4 p-2 bg-white bg-opacity-20 hover:bg-opacity-40 rounded-full text-white transition-colors"
                >
                    <X className="w-6 h-6" />
                </button>
                <img 
                    src={src} 
                    alt={alt} 
                    className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
                    onClick={(e) => e.stopPropagation()} 
                />
            </div>
        </div>
    );
};

export default ImageModal;

