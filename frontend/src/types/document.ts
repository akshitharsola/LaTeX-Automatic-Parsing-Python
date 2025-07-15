/**
 * TypeScript interfaces for DOCX Analyzer
 * Matches Python Pydantic models for type safety
 */

export type DocumentType = 'docx';
export type ListType = 'ordered' | 'unordered' | 'multilevel';
export type SectionLevel = 0 | 1 | 2 | 3 | 4;
export type EquationType = 'omml' | 'latex_inline' | 'latex_display' | 'unicode_math' | 'fraction' | 'complex';
export type LatexTemplate = 'ieee' | 'acm' | 'springer';

export interface ListItem {
  content: string;
  level: number;
  item_type: ListType;
  index?: number;
  has_subitems: boolean;
  word_style?: string;
}

export interface DocumentList {
  id: number;
  list_type: ListType;
  items: ListItem[];
  confidence: number;
  word_list_id?: string;
  numbering_style?: string;
  is_nested: boolean;
  max_depth: number;
  start_paragraph?: number;
  end_paragraph?: number;
}

export interface Equation {
  id: number;
  content: string;
  equation_type: EquationType;
  latex_equivalent?: string;
  confidence: number;
  omml_xml?: string;
  paragraph_index?: number;
  context_before?: string;
  context_after?: string;
  is_display: boolean;
  variables: string[];
}

export interface TableCell {
  content: string;
  row_span: number;
  col_span: number;
  is_header: boolean;
  style?: string;
}

export interface DocumentTable {
  id: number;
  rows: number;
  columns: number;
  cells: TableCell[][];
  caption?: string;
  style?: string;
  confidence: number;
  has_headers: boolean;
  paragraph_index?: number;
}

export interface Section {
  id: number;
  number?: string;
  title: string;
  content: string;
  level: SectionLevel;
  confidence: number;
  word_count: number;
  paragraph_start?: number;
  paragraph_end?: number;
  has_subsections: boolean;
  word_style?: string;
  contains_equations: number[];
  contains_tables: number[];
  contains_lists: number[];
}

export interface DetectedElement {
  content: string;
  confidence: number;
  reasoning: string;
  word_style?: string;
  paragraph_index?: number;
}

export interface AuthorInfo {
  names: string[];
  affiliations: string[];
  emails: string[];
  corresponding_indices: number[];
  orcids: string[];
}

export interface DocumentAnalysis {
  // Basic document info
  filename: string;
  file_size: number;
  document_type: DocumentType;
  
  // Document elements
  title?: DetectedElement;
  authors?: AuthorInfo;
  abstract?: DetectedElement;
  keywords?: DetectedElement;
  
  // Structural elements
  sections: Section[];
  lists: DocumentList[];
  tables: DocumentTable[];
  equations: Equation[];
  
  // Processing metadata
  total_paragraphs: number;
  total_words: number;
  processing_time: number;
  confidence_score: number;
  
  // Word-specific metadata
  word_version?: string;
  has_styles: boolean;
  style_names: string[];
}

export interface ProcessingConfig {
  latex_template: LatexTemplate;
  detect_equations: boolean;
  detect_tables: boolean;
  detect_lists: boolean;
  extract_images: boolean;
  preserve_formatting: boolean;
  min_confidence: number;
  enable_compression: boolean;
}

export interface LatexOutput {
  content: string;
  template: LatexTemplate;
  sections_count: number;
  tables_count: number;
  equations_count: number;
  lists_count: number;
  validation_warnings: string[];
  generation_time: number;
}

export interface UploadProgress {
  stage: 'uploading' | 'processing' | 'analyzing' | 'complete';
  progress: number;
  message: string;
}