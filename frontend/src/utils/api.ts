/**
 * API utilities for communicating with FastAPI backend
 */

import axios from 'axios';
import { DocumentAnalysis, ProcessingConfig, LatexOutput, LatexTemplate } from '../types/document';

// Configure axios defaults
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 300000, // 5 minutes for large documents
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || error.message || 'API request failed');
  }
);

/**
 * Upload and analyze a DOCX document
 */
export const uploadDocument = async (
  file: File, 
  config: ProcessingConfig
): Promise<DocumentAnalysis> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('config', JSON.stringify(config));

  const response = await api.post('/document/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      const percentCompleted = Math.round(
        (progressEvent.loaded * 100) / (progressEvent.total || 1)
      );
      console.log(`Upload progress: ${percentCompleted}%`);
    },
  });

  return response.data;
};

/**
 * Generate LaTeX from document analysis
 */
export const generateLatex = async (
  analysis: DocumentAnalysis,
  template: LatexTemplate = 'ieee'
): Promise<LatexOutput> => {
  const response = await api.post('/latex/generate', {
    analysis,
    template,
  });

  return response.data;
};

/**
 * Download LaTeX file
 */
export const downloadLatex = async (
  analysis: DocumentAnalysis,
  template: LatexTemplate = 'ieee'
): Promise<Blob> => {
  const response = await api.post('/latex/generate/download', {
    analysis,
    template,
  }, {
    responseType: 'blob',
  });

  return response.data;
};

/**
 * Get available LaTeX templates
 */
export const getLatexTemplates = async () => {
  const response = await api.get('/latex/templates');
  return response.data;
};

/**
 * Validate LaTeX content
 */
export const validateLatex = async (latexContent: string) => {
  const response = await api.post('/latex/validate', {
    latex_content: latexContent,
  });
  return response.data;
};

/**
 * Health check for the API
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

/**
 * Health check for document processing service
 */
export const documentHealthCheck = async () => {
  const response = await api.get('/document/health');
  return response.data;
};