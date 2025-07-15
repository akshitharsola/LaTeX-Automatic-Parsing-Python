import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, Loader } from 'lucide-react';
import { DocumentAnalysis, ProcessingConfig, UploadProgress } from '../types/document';
import { uploadDocument } from '../utils/api';
import './DocumentUploader.css';

interface DocumentUploaderProps {
  onAnalysisComplete: (analysis: DocumentAnalysis) => void;
}

const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onAnalysisComplete }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const [config, setConfig] = useState<ProcessingConfig>({
    latex_template: 'ieee',
    detect_equations: true,
    detect_tables: true,
    detect_lists: true,
    extract_images: false,
    preserve_formatting: true,
    min_confidence: 0.7,
    enable_compression: false
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.docx')) {
      setError('Please upload a .docx file');
      return;
    }

    // Validate file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB');
      return;
    }

    setIsUploading(true);
    setError(null);
    setProgress({ stage: 'uploading', progress: 0, message: 'Preparing upload...' });

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (!prev) return null;
          
          if (prev.stage === 'uploading' && prev.progress < 30) {
            return { ...prev, progress: prev.progress + 10, message: 'Uploading document...' };
          } else if (prev.stage === 'uploading') {
            return { stage: 'processing', progress: 40, message: 'Processing with docx2python...' };
          } else if (prev.stage === 'processing' && prev.progress < 70) {
            return { ...prev, progress: prev.progress + 10, message: 'Analyzing document structure...' };
          } else if (prev.stage === 'processing') {
            return { stage: 'analyzing', progress: 80, message: 'Extracting lists and equations...' };
          } else if (prev.stage === 'analyzing' && prev.progress < 95) {
            return { ...prev, progress: prev.progress + 5, message: 'Finalizing analysis...' };
          }
          
          return prev;
        });
      }, 500);

      const analysis = await uploadDocument(file, config);
      
      clearInterval(progressInterval);
      setProgress({ stage: 'complete', progress: 100, message: 'Analysis complete!' });
      
      setTimeout(() => {
        onAnalysisComplete(analysis);
        setIsUploading(false);
        setProgress(null);
      }, 1000);

    } catch (err: any) {
      setError(err.message || 'Failed to upload and analyze document');
      setIsUploading(false);
      setProgress(null);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="uploader-container">
      {/* Configuration Panel */}
      <div className="config-panel">
        <h3>Processing Configuration</h3>
        
        <div className="config-grid">
          <div className="config-group">
            <label>LaTeX Template:</label>
            <select 
              value={config.latex_template} 
              onChange={(e) => setConfig({...config, latex_template: e.target.value as any})}
            >
              <option value="ieee">IEEE Conference</option>
              <option value="acm">ACM Conference</option>
              <option value="springer">Springer Nature</option>
            </select>
          </div>

          <div className="config-group">
            <label>Min Confidence:</label>
            <input 
              type="range" 
              min="0.5" 
              max="1" 
              step="0.1" 
              value={config.min_confidence}
              onChange={(e) => setConfig({...config, min_confidence: parseFloat(e.target.value)})}
            />
            <span>{config.min_confidence}</span>
          </div>
        </div>

        <div className="config-checkboxes">
          <label>
            <input 
              type="checkbox" 
              checked={config.detect_equations}
              onChange={(e) => setConfig({...config, detect_equations: e.target.checked})}
            />
            Detect Equations (OMML + LaTeX)
          </label>
          
          <label>
            <input 
              type="checkbox" 
              checked={config.detect_tables}
              onChange={(e) => setConfig({...config, detect_tables: e.target.checked})}
            />
            Extract Tables
          </label>
          
          <label>
            <input 
              type="checkbox" 
              checked={config.detect_lists}
              onChange={(e) => setConfig({...config, detect_lists: e.target.checked})}
            />
            Detect Lists (Word Styles)
          </label>
          
          <label>
            <input 
              type="checkbox" 
              checked={config.preserve_formatting}
              onChange={(e) => setConfig({...config, preserve_formatting: e.target.checked})}
            />
            Preserve Word Formatting
          </label>
          
          {config.latex_template === 'ieee' && (
            <label>
              <input 
                type="checkbox" 
                checked={config.enable_compression}
                onChange={(e) => setConfig({...config, enable_compression: e.target.checked})}
              />
              Enable Content Compression
            </label>
          )}
        </div>
      </div>

      {/* Upload Area */}
      <div className="upload-section">
        <div 
          className={`upload-area ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={!isUploading ? openFileDialog : undefined}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".docx"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            disabled={isUploading}
          />

          {isUploading ? (
            <div className="upload-progress">
              <Loader className="spinner" size={48} />
              {progress && (
                <>
                  <h3>{progress.message}</h3>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${progress.progress}%` }}
                    />
                  </div>
                  <p>{progress.progress}% Complete</p>
                </>
              )}
            </div>
          ) : (
            <div className="upload-content">
              <FileText size={64} className="upload-icon" />
              <h3>Upload DOCX Document</h3>
              <p>Drag and drop your .docx file here, or click to browse</p>
              
              <div className="file-info">
                <p>✅ Supports Word 2016+ documents</p>
                <p>✅ Maximum file size: 50MB</p>
                <p>✅ Native DOCX processing with docx2python</p>
              </div>
              
              <button className="upload-button" disabled={isUploading}>
                <Upload size={20} />
                Choose File
              </button>
            </div>
          )}
        </div>

        {/* Features Showcase */}
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h4>Smart List Detection</h4>
            <p>Uses Word's native list styles for accurate detection of bulleted and numbered lists</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🧮</div>
            <h4>OMML Equation Support</h4>
            <p>Extracts Office Math Markup Language equations directly from Word documents</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h4>Advanced Table Processing</h4>
            <p>Preserves table structure, headers, and formatting for accurate LaTeX conversion</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h4>High Performance</h4>
            <p>Async processing with Python FastAPI for fast document analysis</p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUploader;