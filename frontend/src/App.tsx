import React, { useState } from 'react';
import { FileText, Zap, Shield, Cpu } from 'lucide-react';
import DocumentUploader from './components/DocumentUploader';
import AnalysisViewer from './components/AnalysisViewer';
import LatexViewer from './components/LatexViewer';
import { DocumentAnalysis, LatexOutput } from './types/document';
import './App.css';

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'upload' | 'analysis' | 'latex'>('upload');
  const [analysis, setAnalysis] = useState<DocumentAnalysis | null>(null);
  const [latexOutput, setLatexOutput] = useState<LatexOutput | null>(null);

  const handleAnalysisComplete = (result: DocumentAnalysis) => {
    setAnalysis(result);
    setCurrentView('analysis');
  };

  const handleLatexGenerated = (latex: LatexOutput) => {
    setLatexOutput(latex);
    setCurrentView('latex');
  };

  const handleBackToUpload = () => {
    setCurrentView('upload');
    setAnalysis(null);
    setLatexOutput(null);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="container">
          <div className="header-content">
            <div className="header-title">
              <FileText className="header-icon" />
              <div>
                <h1>DOCX Analyzer</h1>
                <p className="header-subtitle">Python Edition - Advanced Document Processing</p>
              </div>
            </div>
            
            <div className="header-features">
              <div className="feature-badge">
                <Zap size={16} />
                <span>Native DOCX</span>
              </div>
              <div className="feature-badge">
                <Shield size={16} />
                <span>High Accuracy</span>
              </div>
              <div className="feature-badge">
                <Cpu size={16} />
                <span>Fast Processing</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="app-nav">
        <div className="container">
          <div className="nav-buttons">
            <button
              onClick={() => setCurrentView('upload')}
              className={`nav-button ${currentView === 'upload' ? 'active' : ''}`}
            >
              Upload
            </button>
            <button
              onClick={() => setCurrentView('analysis')}
              className={`nav-button ${currentView === 'analysis' ? 'active' : ''}`}
              disabled={!analysis}
            >
              Analysis
            </button>
            <button
              onClick={() => setCurrentView('latex')}
              className={`nav-button ${currentView === 'latex' ? 'active' : ''}`}
              disabled={!latexOutput}
            >
              LaTeX
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="app-main">
        <div className="container">
          {currentView === 'upload' && (
            <DocumentUploader onAnalysisComplete={handleAnalysisComplete} />
          )}
          
          {currentView === 'analysis' && analysis && (
            <AnalysisViewer 
              analysis={analysis} 
              onLatexGenerated={handleLatexGenerated}
              onBackToUpload={handleBackToUpload}
            />
          )}
          
          {currentView === 'latex' && latexOutput && (
            <LatexViewer 
              latexOutput={latexOutput}
              onBackToAnalysis={() => setCurrentView('analysis')}
              onBackToUpload={handleBackToUpload}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-info">
              <p>DOCX Analyzer v2.0 - Built with Python FastAPI + React TypeScript</p>
              <p className="footer-tech">
                Powered by docx2python • Advanced list detection • Native OMML support
              </p>
            </div>
            
            <div className="footer-improvements">
              <h4>Key Improvements:</h4>
              <ul>
                <li>Native DOCX processing (no HTML conversion)</li>
                <li>Superior list detection using Word styles</li>
                <li>Enhanced equation extraction with OMML support</li>
                <li>Context-aware section analysis</li>
                <li>High-performance async processing</li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;