import React, { useState } from 'react';
import { Copy, Download, ArrowLeft, Eye, CheckCircle, ExternalLink } from 'lucide-react';
import { LatexOutput } from '../types/document';
import './LatexViewer.css';

interface LatexViewerProps {
  latexOutput: LatexOutput;
  onBackToAnalysis: () => void;
  onBackToUpload: () => void;
}

const LatexViewer: React.FC<LatexViewerProps> = ({
  latexOutput,
  onBackToAnalysis,
  onBackToUpload
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(latexOutput.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([latexOutput.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `document_${latexOutput.template}.tex`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const openOverleaf = () => {
    window.open('https://www.overleaf.com', '_blank');
  };

  return (
    <div className="latex-viewer">
      {/* Header */}
      <div className="latex-header">
        <div className="header-main">
          <div className="header-info">
            <h2>Generated LaTeX Code</h2>
            <p className="header-subtitle">
              {latexOutput.template.toUpperCase()} Template • 
              {latexOutput.sections_count} sections • 
              {latexOutput.tables_count} tables • 
              {latexOutput.equations_count} equations • 
              {latexOutput.lists_count} lists • 
              Generated in {Math.round(latexOutput.generation_time * 1000)}ms
            </p>
          </div>
          
          <div className="header-actions">
            <button onClick={onBackToAnalysis} className="nav-button">
              <ArrowLeft size={16} />
              Back to Analysis
            </button>
            <button onClick={onBackToUpload} className="nav-button secondary">
              New Upload
            </button>
          </div>
        </div>
      </div>

      {/* Template Info */}
      <div className="template-info">
        <div className="template-card">
          <h3>{getTemplateName(latexOutput.template)}</h3>
          <p>{getTemplateDescription(latexOutput.template)}</p>
          <div className="template-features">
            {getTemplateFeatures(latexOutput.template).map((feature, index) => (
              <span key={index} className="feature-tag">{feature}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="latex-stats">
        <div className="stat-item">
          <span className="stat-number">{latexOutput.content.split('\n').length}</span>
          <span className="stat-label">Lines</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{Math.round(latexOutput.content.length / 1024)}KB</span>
          <span className="stat-label">Size</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{latexOutput.validation_warnings.length}</span>
          <span className="stat-label">Warnings</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{Math.round(latexOutput.generation_time * 1000)}ms</span>
          <span className="stat-label">Generation Time</span>
        </div>
      </div>

      {/* Validation Warnings */}
      {latexOutput.validation_warnings.length > 0 && (
        <div className="warnings-section">
          <h3>⚠️ Validation Warnings</h3>
          <div className="warnings-list">
            {latexOutput.validation_warnings.map((warning, index) => (
              <div key={index} className="warning-item">
                {warning}
              </div>
            ))}
          </div>
          <p className="warnings-note">
            These warnings may affect LaTeX compilation. Review and fix them before submitting.
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="latex-actions">
        <button onClick={handleCopy} className="action-button primary">
          {copied ? <CheckCircle size={16} /> : <Copy size={16} />}
          {copied ? 'Copied!' : 'Copy to Clipboard'}
        </button>
        
        <button onClick={handleDownload} className="action-button secondary">
          <Download size={16} />
          Download .tex File
        </button>
        
        <button onClick={openOverleaf} className="action-button overleaf">
          <ExternalLink size={16} />
          Open Overleaf
        </button>
      </div>

      {/* LaTeX Code Display */}
      <div className="latex-container">
        <div className="latex-toolbar">
          <div className="toolbar-info">
            <Eye size={16} />
            <span>LaTeX Source Code</span>
          </div>
          
          <div className="toolbar-actions">
            <button onClick={handleCopy} className="toolbar-button">
              {copied ? <CheckCircle size={14} /> : <Copy size={14} />}
            </button>
            <button onClick={handleDownload} className="toolbar-button">
              <Download size={14} />
            </button>
          </div>
        </div>
        
        <div className="latex-code-wrapper">
          <pre className="latex-code">
            <code>{latexOutput.content}</code>
          </pre>
        </div>
      </div>

      {/* Usage Instructions */}
      <div className="usage-instructions">
        <h3>How to Use This LaTeX Code</h3>
        <div className="instructions-grid">
          <div className="instruction-card">
            <div className="instruction-number">1</div>
            <div className="instruction-content">
              <h4>Copy the Code</h4>
              <p>Click "Copy to Clipboard" to copy the entire LaTeX document to your clipboard.</p>
            </div>
          </div>
          
          <div className="instruction-card">
            <div className="instruction-number">2</div>
            <div className="instruction-content">
              <h4>Open Overleaf</h4>
              <p>Create a new project in Overleaf or your preferred LaTeX editor.</p>
            </div>
          </div>
          
          <div className="instruction-card">
            <div className="instruction-number">3</div>
            <div className="instruction-content">
              <h4>Paste and Compile</h4>
              <p>Paste the code and compile to generate your PDF document.</p>
            </div>
          </div>
          
          <div className="instruction-card">
            <div className="instruction-number">4</div>
            <div className="instruction-content">
              <h4>Review and Edit</h4>
              <p>Review the output and make any necessary adjustments to formatting or content.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions
const getTemplateName = (template: string): string => {
  const names = {
    'ieee': 'IEEE Conference Paper',
    'acm': 'ACM Conference Paper',
    'springer': 'Springer Nature Journal'
  };
  return names[template as keyof typeof names] || template.toUpperCase();
};

const getTemplateDescription = (template: string): string => {
  const descriptions = {
    'ieee': 'Standard IEEE conference paper format with two-column layout and proper citation style.',
    'acm': 'ACM conference paper format with modern styling and author affiliations.',
    'springer': 'Springer Nature journal article format with comprehensive mathematical typesetting support.'
  };
  return descriptions[template as keyof typeof descriptions] || 'LaTeX document template';
};

const getTemplateFeatures = (template: string): string[] => {
  const features = {
    'ieee': ['Two-column layout', 'IEEE citation style', 'Conference format'],
    'acm': ['Modern styling', 'Author affiliations', 'ACM citation style'],
    'springer': ['Journal format', 'Mathematical typesetting', 'Algorithm support']
  };
  return features[template as keyof typeof features] || ['Custom template'];
};

export default LatexViewer;