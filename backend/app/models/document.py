"""
Pydantic models for document structure and analysis
Enhanced for native DOCX processing with docx2python
"""

from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types"""
    DOCX = "docx"


class ListType(str, Enum):
    """List types supported by Word"""
    ORDERED = "ordered"
    UNORDERED = "unordered"
    MULTILEVEL = "multilevel"


class SectionLevel(int, Enum):
    """Section hierarchy levels"""
    TITLE = 0
    SECTION = 1
    SUBSECTION = 2
    SUBSUBSECTION = 3
    PARAGRAPH = 4


class EquationType(str, Enum):
    """Mathematical equation types"""
    OMML = "omml"  # Office Math Markup Language
    LATEX_INLINE = "latex_inline"
    LATEX_DISPLAY = "latex_display"
    UNICODE_MATH = "unicode_math"
    FRACTION = "fraction"
    COMPLEX = "complex"


class LatexTemplate(str, Enum):
    """Supported LaTeX templates"""
    IEEE = "ieee"
    ACM = "acm"
    SPRINGER = "springer"


class ListItem(BaseModel):
    """Individual list item with hierarchical information"""
    content: str = Field(..., description="Text content of the list item")
    level: int = Field(default=1, ge=1, le=9, description="Nesting level (1-9)")
    item_type: ListType = Field(..., description="Type of list item")
    index: Optional[int] = Field(None, description="Index for ordered lists")
    has_subitems: bool = Field(default=False, description="Whether item has sub-items")
    word_style: Optional[str] = Field(None, description="Original Word style name")


class DocumentList(BaseModel):
    """Enhanced list detection using Word's native list styles"""
    id: int = Field(..., description="Unique list identifier")
    list_type: ListType = Field(..., description="Type of list")
    items: List[ListItem] = Field(..., description="List items")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    word_list_id: Optional[str] = Field(None, description="Word's internal list ID")
    numbering_style: Optional[str] = Field(None, description="Numbering format")
    is_nested: bool = Field(default=False, description="Whether list has nested items")
    max_depth: int = Field(default=1, description="Maximum nesting depth")
    start_paragraph: Optional[int] = Field(None, description="Starting paragraph index")
    end_paragraph: Optional[int] = Field(None, description="Ending paragraph index")


class Equation(BaseModel):
    """Mathematical equation with enhanced OMML support"""
    id: int = Field(..., description="Unique equation identifier")
    content: str = Field(..., description="Raw equation content")
    equation_type: EquationType = Field(..., description="Type of equation")
    latex_equivalent: Optional[str] = Field(None, description="LaTeX representation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    omml_xml: Optional[str] = Field(None, description="Original OMML XML")
    paragraph_index: Optional[int] = Field(None, description="Paragraph location")
    context_before: Optional[str] = Field(None, description="Text before equation")
    context_after: Optional[str] = Field(None, description="Text after equation")
    is_display: bool = Field(default=False, description="Display vs inline equation")
    variables: List[str] = Field(default_factory=list, description="Detected variables")


class TableCell(BaseModel):
    """Enhanced table cell with Word formatting"""
    content: str = Field(..., description="Cell text content")
    row_span: int = Field(default=1, description="Number of rows spanned")
    col_span: int = Field(default=1, description="Number of columns spanned")
    is_header: bool = Field(default=False, description="Whether cell is a header")
    style: Optional[str] = Field(None, description="Word cell style")


class DocumentTable(BaseModel):
    """Enhanced table structure from Word"""
    id: int = Field(..., description="Unique table identifier")
    rows: int = Field(..., ge=1, description="Number of rows")
    columns: int = Field(..., ge=1, description="Number of columns")
    cells: List[List[TableCell]] = Field(..., description="Table cells")
    caption: Optional[str] = Field(None, description="Table caption")
    style: Optional[str] = Field(None, description="Word table style")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    has_headers: bool = Field(default=False, description="Whether table has headers")
    paragraph_index: Optional[int] = Field(None, description="Location in document")


class Section(BaseModel):
    """Document section with enhanced context analysis"""
    id: int = Field(..., description="Unique section identifier")
    number: Optional[str] = Field(None, description="Section number (e.g., '1.2.3')")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    level: SectionLevel = Field(..., description="Hierarchical level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    word_count: int = Field(..., ge=0, description="Number of words in section")
    paragraph_start: Optional[int] = Field(None, description="Starting paragraph index")
    paragraph_end: Optional[int] = Field(None, description="Ending paragraph index")
    has_subsections: bool = Field(default=False, description="Whether section has subsections")
    word_style: Optional[str] = Field(None, description="Word heading style")
    contains_equations: List[int] = Field(default_factory=list, description="Equation IDs in section")
    contains_tables: List[int] = Field(default_factory=list, description="Table IDs in section")
    contains_lists: List[int] = Field(default_factory=list, description="List IDs in section")


class DetectedElement(BaseModel):
    """Generic detected document element"""
    content: str = Field(..., description="Element content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    reasoning: str = Field(..., description="Detection reasoning")
    word_style: Optional[str] = Field(None, description="Word style used")
    paragraph_index: Optional[int] = Field(None, description="Location in document")


class AuthorInfo(BaseModel):
    """Structured author information"""
    names: List[str] = Field(default_factory=list, description="Author names")
    affiliations: List[str] = Field(default_factory=list, description="Author affiliations")
    departments: List[str] = Field(default_factory=list, description="Author departments")
    emails: List[str] = Field(default_factory=list, description="Author emails")
    corresponding_indices: List[int] = Field(default_factory=list, description="Corresponding author indices")
    orcids: List[str] = Field(default_factory=list, description="ORCID identifiers")


class DocumentAnalysis(BaseModel):
    """Complete document analysis result"""
    # Basic document info
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    document_type: DocumentType = Field(..., description="Document type")
    
    # Document elements
    title: Optional[DetectedElement] = Field(None, description="Document title")
    authors: Optional[AuthorInfo] = Field(None, description="Author information")
    abstract: Optional[DetectedElement] = Field(None, description="Document abstract")
    keywords: Optional[DetectedElement] = Field(None, description="Document keywords")
    
    # Structural elements
    sections: List[Section] = Field(default_factory=list, description="Document sections")
    lists: List[DocumentList] = Field(default_factory=list, description="Document lists")
    tables: List[DocumentTable] = Field(default_factory=list, description="Document tables")
    equations: List[Equation] = Field(default_factory=list, description="Mathematical equations")
    
    # Processing metadata
    total_paragraphs: int = Field(..., description="Total number of paragraphs")
    total_words: int = Field(..., description="Total word count")
    processing_time: float = Field(..., description="Processing time in seconds")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall analysis confidence")
    
    # Word-specific metadata
    word_version: Optional[str] = Field(None, description="Word version that created document")
    has_styles: bool = Field(default=False, description="Whether document uses Word styles")
    style_names: List[str] = Field(default_factory=list, description="Available style names")


class ProcessingConfig(BaseModel):
    """Configuration for document processing"""
    latex_template: LatexTemplate = Field(default=LatexTemplate.IEEE, description="LaTeX template to use")
    detect_sections: bool = Field(default=True, description="Enable section detection")
    detect_equations: bool = Field(default=True, description="Enable equation detection")
    detect_tables: bool = Field(default=True, description="Enable table detection")
    detect_lists: bool = Field(default=True, description="Enable list detection")
    extract_images: bool = Field(default=False, description="Extract embedded images")
    preserve_formatting: bool = Field(default=True, description="Preserve Word formatting")
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence threshold")
    enable_compression: bool = Field(default=False, description="Enable content compression for IEEE")


class LatexOutput(BaseModel):
    """Generated LaTeX output"""
    content: str = Field(..., description="Generated LaTeX content")
    template: LatexTemplate = Field(..., description="Template used")
    sections_count: int = Field(..., description="Number of sections")
    tables_count: int = Field(..., description="Number of tables")
    equations_count: int = Field(..., description="Number of equations")
    lists_count: int = Field(..., description="Number of lists")
    validation_warnings: List[str] = Field(default_factory=list, description="LaTeX validation warnings")
    generation_time: float = Field(..., description="Generation time in seconds")