import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchFiles, uploadFile } from '../api/client';
import { FileItemData } from '../types';

export const useFiles = () => {
    return useQuery<FileItemData[], Error>({
        queryKey: ['files'],
        queryFn: fetchFiles,
    });
};

export const useUploadFile = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: uploadFile,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['files'] });
        },
    });
};

