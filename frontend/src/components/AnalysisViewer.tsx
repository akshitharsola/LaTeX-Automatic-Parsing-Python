import React, { useState } from 'react';
import { FileText, Users, Hash, List, Table, Calculator, Download, ArrowLeft } from 'lucide-react';
import { DocumentAnalysis, LatexTemplate, LatexOutput } from '../types/document';
import { generateLatex } from '../utils/api';
import './AnalysisViewer.css';

interface AnalysisViewerProps {
  analysis: DocumentAnalysis;
  onLatexGenerated: (latex: LatexOutput) => void;
  onBackToUpload: () => void;
}

const AnalysisViewer: React.FC<AnalysisViewerProps> = ({
  analysis,
  onLatexGenerated,
  onBackToUpload
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<LatexTemplate>('ieee');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateLatex = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const latexOutput = await generateLatex(analysis, selectedTemplate);
      onLatexGenerated(latexOutput);
    } catch (err: any) {
      setError(err.message || 'Failed to generate LaTeX');
    } finally {
      setIsGenerating(false);
    }
  };

  const renderConfidenceBar = (confidence: number) => {
    const percentage = Math.round(confidence * 100);
    const level = confidence >= 0.8 ? 'high' : confidence >= 0.6 ? 'medium' : 'low';
    
    return (
      <div className="confidence-bar">
        <div className="confidence-track">
          <div 
            className={`confidence-fill confidence-${level}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className="confidence-text">{percentage}%</span>
      </div>
    );
  };

  return (
    <div className="analysis-viewer">
      {/* Header */}
      <div className="analysis-header">
        <div className="header-main">
          <FileText className="header-icon" />
          <div>
            <h2>{analysis.filename}</h2>
            <p className="header-subtitle">
              Document Analysis Complete • {analysis.total_words} words • 
              {Math.round(analysis.processing_time * 1000)}ms processing time
            </p>
          </div>
        </div>
        
        <button onClick={onBackToUpload} className="back-button">
          <ArrowLeft size={16} />
          New Upload
        </button>
      </div>

      {/* Summary Stats */}
      <div className="summary-grid">
        <div className="summary-card">
          <div className="summary-icon">📄</div>
          <div className="summary-content">
            <h3>{analysis.sections.length}</h3>
            <p>Sections</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">📋</div>
          <div className="summary-content">
            <h3>{analysis.lists.length}</h3>
            <p>Lists</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">📊</div>
          <div className="summary-content">
            <h3>{analysis.tables.length}</h3>
            <p>Tables</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">🧮</div>
          <div className="summary-content">
            <h3>{analysis.equations.length}</h3>
            <p>Equations</p>
          </div>
        </div>
      </div>

      {/* Document Elements */}
      <div className="elements-grid">
        {/* Title */}
        {analysis.title && (
          <div className="element-card">
            <div className="element-header">
              <FileText size={20} />
              <span>Title</span>
              {renderConfidenceBar(analysis.title.confidence)}
            </div>
            <div className="element-content">
              <p className="element-text">{analysis.title.content}</p>
              <p className="element-reasoning">{analysis.title.reasoning}</p>
            </div>
          </div>
        )}

        {/* Authors */}
        {analysis.authors && (
          <div className="element-card">
            <div className="element-header">
              <Users size={20} />
              <span>Authors</span>
            </div>
            <div className="element-content">
              <div className="authors-list">
                {analysis.authors.names.map((name, index) => (
                  <div key={index} className="author-item">
                    <strong>{name}</strong>
                    {analysis.authors?.emails[index] && (
                      <span className="author-email">{analysis.authors.emails[index]}</span>
                    )}
                    {analysis.authors?.affiliations[index] && (
                      <span className="author-affiliation">{analysis.authors.affiliations[index]}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Abstract */}
        {analysis.abstract && (
          <div className="element-card">
            <div className="element-header">
              <Hash size={20} />
              <span>Abstract</span>
              {renderConfidenceBar(analysis.abstract.confidence)}
            </div>
            <div className="element-content">
              <p className="element-text">{analysis.abstract.content}</p>
              <p className="element-reasoning">{analysis.abstract.reasoning}</p>
            </div>
          </div>
        )}

        {/* Keywords */}
        {analysis.keywords && (
          <div className="element-card">
            <div className="element-header">
              <Hash size={20} />
              <span>Keywords</span>
              {renderConfidenceBar(analysis.keywords.confidence)}
            </div>
            <div className="element-content">
              <p className="element-text">{analysis.keywords.content}</p>
            </div>
          </div>
        )}
      </div>

      {/* Sections */}
      {analysis.sections.length > 0 && (
        <div className="sections-container">
          <h3>Document Sections ({analysis.sections.length})</h3>
          <div className="sections-list">
            {analysis.sections.slice(0, 5).map((section) => (
              <div key={section.id} className="section-item">
                <div className="section-header">
                  <div className="section-title">
                    {section.number && <span className="section-number">{section.number}</span>}
                    <span>{section.title}</span>
                  </div>
                  <div className="section-meta">
                    <span className="section-level">Level {section.level}</span>
                    <span className="section-words">{section.word_count} words</span>
                    {renderConfidenceBar(section.confidence)}
                  </div>
                </div>
                <p className="section-preview">
                  {section.content.substring(0, 200)}
                  {section.content.length > 200 && '...'}
                </p>
                
                {/* Related elements */}
                <div className="section-elements">
                  {section.contains_tables.length > 0 && (
                    <span className="element-badge">
                      <Table size={12} />
                      {section.contains_tables.length} table(s)
                    </span>
                  )}
                  {section.contains_lists.length > 0 && (
                    <span className="element-badge">
                      <List size={12} />
                      {section.contains_lists.length} list(s)
                    </span>
                  )}
                  {section.contains_equations.length > 0 && (
                    <span className="element-badge">
                      <Calculator size={12} />
                      {section.contains_equations.length} equation(s)
                    </span>
                  )}
                </div>
              </div>
            ))}
            
            {analysis.sections.length > 5 && (
              <div className="sections-more">
                ... and {analysis.sections.length - 5} more sections
              </div>
            )}
          </div>
        </div>
      )}

      {/* Lists */}
      {analysis.lists.length > 0 && (
        <div className="lists-container">
          <h3>Document Lists ({analysis.lists.length})</h3>
          <div className="lists-grid">
            {analysis.lists.slice(0, 4).map((list) => (
              <div key={list.id} className="list-card">
                <div className="list-header">
                  <List size={16} />
                  <span>
                    {list.list_type === 'ordered' ? 'Numbered' : 'Bulleted'} List
                  </span>
                  {renderConfidenceBar(list.confidence)}
                </div>
                <div className="list-meta">
                  <span>{list.items.length} items</span>
                  {list.is_nested && <span className="nested-badge">Nested</span>}
                  {list.max_depth > 1 && <span>Depth: {list.max_depth}</span>}
                </div>
                <div className="list-preview">
                  {list.items.slice(0, 3).map((item, index) => (
                    <div key={index} className="list-item-preview">
                      {list.list_type === 'ordered' ? `${item.index || index + 1}.` : '•'} 
                      {item.content.substring(0, 50)}
                      {item.content.length > 50 && '...'}
                    </div>
                  ))}
                  {list.items.length > 3 && (
                    <div className="list-more">... and {list.items.length - 3} more items</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Equations */}
      {analysis.equations.length > 0 && (
        <div className="equations-container">
          <h3>Mathematical Equations ({analysis.equations.length})</h3>
          <div className="equations-grid">
            {analysis.equations.slice(0, 6).map((equation) => (
              <div key={equation.id} className="equation-card">
                <div className="equation-header">
                  <Calculator size={16} />
                  <span>Equation {equation.id}</span>
                  <span className={`equation-type ${equation.equation_type}`}>
                    {equation.equation_type.replace('_', ' ')}
                  </span>
                  {renderConfidenceBar(equation.confidence)}
                </div>
                
                <div className="equation-content">
                  <div className="equation-original">
                    <strong>Detected:</strong> {equation.content}
                  </div>
                  {equation.latex_equivalent && (
                    <div className="equation-latex">
                      <strong>LaTeX:</strong> {equation.latex_equivalent}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* LaTeX Generation */}
      <div className="latex-generation">
        <h3>Generate LaTeX Output</h3>
        <div className="template-selection">
          <label>
            LaTeX Template:
            <select 
              value={selectedTemplate} 
              onChange={(e) => setSelectedTemplate(e.target.value as LatexTemplate)}
            >
              <option value="ieee">IEEE Conference</option>
              <option value="acm">ACM Conference</option>
              <option value="springer">Springer Nature</option>
            </select>
          </label>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
        
        <button 
          onClick={handleGenerateLatex} 
          disabled={isGenerating}
          className="generate-button"
        >
          {isGenerating ? (
            <>
              <div className="spinner" />
              Generating LaTeX...
            </>
          ) : (
            <>
              <Download size={16} />
              Generate {selectedTemplate.toUpperCase()} LaTeX
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default AnalysisViewer;