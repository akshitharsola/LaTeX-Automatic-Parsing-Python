"""
IEEE LaTeX Generator
Generates LaTeX code specifically for IEEE Conference template
"""

import re
from typing import List, Dict, Any
from .base_generator import BaseLatexGenerator
from app.models.document import (
    DocumentAnalysis, LatexTemplate, DocumentTable, SectionLevel
)


class IEEELatexGenerator(BaseLatexGenerator):
    """IEEE-specific LaTeX generator"""
    
    def __init__(self):
        super().__init__(LatexTemplate.IEEE)
    
    def _get_template_config(self) -> Dict[str, Any]:
        """Get IEEE-specific configuration"""
        return {
            "document_class": "\\documentclass[conference]{IEEEtran}",
            "packages": [
                "\\usepackage{array}",
                "\\usepackage{booktabs}",
                "\\usepackage{graphicx}",
                "\\usepackage{amsmath}",
                "\\usepackage{amssymb}",
                "\\usepackage{cite}"
            ],
            "table_style": "ieee",
            "list_env": {"ordered": "enumerate", "unordered": "itemize"},
            "author_format": "ieee_blocks",
            "abstract_format": "standard",
            "keywords_format": "IEEEkeywords"
        }
    
    def _generate_document_content(self, analysis: DocumentAnalysis) -> List[str]:
        """Generate IEEE document content with proper ordering"""
        parts = []
        
        # IEEE ordering: title first, then abstract/keywords
        parts.append(self._generate_title_section(analysis))
        
        if analysis.abstract:
            parts.append(self._generate_abstract(analysis.abstract.content))
        
        if analysis.keywords:
            parts.append(self._generate_keywords(analysis.keywords.content))
        
        # Document sections
        parts.append(self._generate_sections(analysis))
        
        # Bibliography
        parts.append(self._generate_bibliography())
        
        return parts
    
    def _generate_preamble(self) -> str:
        """Generate IEEE document preamble"""
        preamble_parts = []
        
        # Document class
        preamble_parts.append(self._config["document_class"])
        preamble_parts.append("")
        
        # Packages
        preamble_parts.extend(self._config["packages"])
        preamble_parts.append("")
        
        # IEEE-specific additions
        preamble_parts.extend([
            "\\IEEEoverridecommandlockouts",
            "\\def\\BibTeX{{\\rm B\\kern-.05em{\\sc i\\kern-.025em b}\\kern-.08em",
            "    T\\kern-.1667em\\lower.7ex\\hbox{E}\\kern-.125emX}}",
            ""
        ])
        
        return "\n".join(preamble_parts)
    
    def _generate_title_section(self, analysis: DocumentAnalysis) -> str:
        """Generate IEEE title, authors, and affiliations"""
        parts = []
        
        # Title
        title = analysis.title.content if analysis.title else "Document Title"
        parts.append(f"\\title{{{title}}}")
        
        # Authors
        if analysis.authors:
            author_latex = self._generate_authors(analysis.authors)
            parts.append(author_latex)
        else:
            parts.append("\\author{\\IEEEauthorblockN{Author Name}\\IEEEauthorblockA{\\textit{Department}\\\\\\textit{Institution}\\\\City, Country\\\\email@domain.com}}")
        
        parts.append("\\maketitle")
        parts.append("")
        
        return "\n".join(parts)
    
    def _generate_keywords(self, keywords: str) -> str:
        """Generate IEEE keywords section"""
        return f"\\begin{{IEEEkeywords}}\n{self._escape_latex(keywords)}\n\\end{{IEEEkeywords}}\n"
    
    def _generate_authors(self, authors) -> str:
        """Generate IEEE author section with IEEEauthorblock format"""
        if not authors.names:
            return "\\author{Author Name}"
        
        author_blocks = []
        for i, name in enumerate(authors.names):
            # Format author name
            formatted_name = self._format_author_name(name)
            email = authors.emails[i] if i < len(authors.emails) else "email@domain.com"
            affiliation = authors.affiliations[i] if i < len(authors.affiliations) else "Institution"
            
            # Handle department expansion for IEEE
            if hasattr(authors, 'departments') and i < len(authors.departments):
                dept = self._expand_department(authors.departments[i], "ieee")
                dept_text = f"Department of {dept}"
            else:
                dept_text = "Department"
            
            # Generate ordinal number
            ordinal = self._get_ordinal(i + 1)
            
            # Extract city and country from affiliation
            affiliation_parts = affiliation.split(',')
            institution = affiliation_parts[0].strip()
            city = affiliation_parts[1].strip() if len(affiliation_parts) > 1 else "City"
            country = affiliation_parts[2].strip() if len(affiliation_parts) > 2 else "Country"
            
            block = f"""\\IEEEauthorblockN{{{ordinal} {formatted_name}}}
\\IEEEauthorblockA{{\\textit{{{dept_text}}} \\\\
\\textit{{{institution}}} \\\\
{city}, {country} \\\\
{email}}}"""
            author_blocks.append(block)
        
        return f"\\author{{\n{('\\n\\and\\n').join(author_blocks)}\n}}"
    
    def _generate_table(self, table: DocumentTable) -> str:
        """Generate IEEE LaTeX table with proper formatting"""
        if not table.cells or not table.cells[0]:
            return ""
        
        cols = len(table.cells[0])
        
        # IEEE table formatting with column alignment
        col_spec = self._generate_ieee_column_spec(table, cols)
        
        parts = []
        parts.append("\\begin{table}[!t]")  # IEEE prefers [!t] positioning
        parts.append("\\renewcommand{\\arraystretch}{1.3}")  # Better row spacing
        parts.append("\\caption{" + self._format_ieee_table_caption(table) + "}")
        parts.append(f"\\label{{tab:{self._generate_table_label(table)}}}")
        parts.append("\\centering")
        parts.append(f"\\begin{{tabular}}{{{col_spec}}}")
        parts.append("\\hline\\hline")  # IEEE double line at top
        
        # Table rows with IEEE formatting
        for i, row in enumerate(table.cells):
            row_content = self._format_ieee_table_row(row, i == 0 and table.has_headers)
            parts.append(row_content)
            
            # IEEE header separator
            if i == 0 and table.has_headers:
                parts.append("\\hline")
        
        parts.append("\\hline\\hline")  # IEEE double line at bottom
        parts.append("\\end{tabular}")
        parts.append("\\end{table}")
        
        return "\n".join(parts)
    
    def _generate_ieee_column_spec(self, table: DocumentTable, cols: int) -> str:
        """Generate IEEE-appropriate column specification"""
        # Analyze column content to determine best alignment
        col_alignments = []
        
        for col_idx in range(cols):
            # Check first few rows to determine content type
            has_numbers = False
            has_text = False
            
            for row_idx, row in enumerate(table.cells[:min(3, len(table.cells))]):
                if col_idx < len(row):
                    content = row[col_idx].content.strip()
                    if content:
                        # Check if content is primarily numeric
                        if re.match(r'^[\d.,\-+%]+$', content):
                            has_numbers = True
                        else:
                            has_text = True
            
            # Determine alignment
            if has_numbers and not has_text:
                col_alignments.append('r')  # Right-align numbers
            elif col_idx == 0:
                col_alignments.append('l')  # Left-align first column
            else:
                col_alignments.append('c')  # Center-align others
        
        return '|' + '|'.join(col_alignments) + '|'
    
    def _format_ieee_table_caption(self, table: DocumentTable) -> str:
        """Format table caption in IEEE style"""
        if table.caption:
            caption = self._escape_latex(table.caption.strip())
            # IEEE caption format: "TABLE I: Caption Text"
            if not caption.upper().startswith('TABLE'):
                caption = f"TABLE {self._roman_numeral(table.id)}: {caption}"
        else:
            caption = f"TABLE {self._roman_numeral(table.id)}: Sample Table"
        
        return caption
    
    def _generate_table_label(self, table: DocumentTable) -> str:
        """Generate appropriate table label"""
        if table.caption:
            # Generate label from caption
            label_text = re.sub(r'[^a-zA-Z0-9\s]', '', table.caption.lower())
            label_text = re.sub(r'\s+', '_', label_text.strip())
            return f"table_{table.id}_{label_text}"
        else:
            return f"table_{table.id}"
    
    def _format_ieee_table_row(self, row, is_header: bool = False) -> str:
        """Format a table row with IEEE styling"""
        formatted_cells = []
        
        for cell in row:
            content = cell.content.strip()
            
            if is_header:
                # IEEE headers are typically bold and centered
                if content:
                    formatted_cells.append(f"\\textbf{{{self._escape_latex(content)}}}")
                else:
                    formatted_cells.append("")
            else:
                # Regular cell content
                if content:
                    # Check for special formatting needs
                    if re.match(r'^[\d.,\-+]+$', content):
                        # Numeric content - no special formatting needed
                        formatted_cells.append(self._escape_latex(content))
                    elif '%' in content:
                        # Percentage - ensure proper LaTeX formatting
                        formatted_cells.append(self._escape_latex(content))
                    else:
                        # Text content
                        formatted_cells.append(self._escape_latex(content))
                else:
                    formatted_cells.append("")
        
        row_content = " & ".join(formatted_cells)
        return row_content + " \\\\"
    
    def _roman_numeral(self, num: int) -> str:
        """Convert number to Roman numeral (IEEE table numbering)"""
        values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        numerals = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        
        result = ''
        for i, value in enumerate(values):
            count = num // value
            if count:
                result += numerals[i] * count
                num -= value * count
        return result
    
    def _generate_list(self, doc_list) -> str:
        """Generate IEEE LaTeX list with proper formatting"""
        from app.models.document import ListType
        
        if not doc_list.items:
            return ""
        
        # IEEE list formatting
        if doc_list.list_type == ListType.ORDERED:
            return self._generate_ieee_ordered_list(doc_list)
        else:
            return self._generate_ieee_unordered_list(doc_list)
    
    def _generate_ieee_ordered_list(self, doc_list) -> str:
        """Generate IEEE-style ordered (numbered) list"""
        parts = []
        
        # IEEE prefers specific enumerate formatting
        if doc_list.is_nested:
            parts.append("\\begin{enumerate}")
        else:
            parts.append("\\begin{enumerate}")
        
        # Group items by level for proper nesting
        nested_items = self._group_list_items_by_level(doc_list.items)
        self._add_nested_items_to_list(parts, nested_items, is_ordered=True)
        
        parts.append("\\end{enumerate}")
        return "\n".join(parts)
    
    def _generate_ieee_unordered_list(self, doc_list) -> str:
        """Generate IEEE-style unordered (bullet) list"""
        parts = []
        
        # IEEE itemize formatting
        parts.append("\\begin{itemize}")
        
        # Group items by level for proper nesting
        nested_items = self._group_list_items_by_level(doc_list.items)
        self._add_nested_items_to_list(parts, nested_items, is_ordered=False)
        
        parts.append("\\end{itemize}")
        return "\n".join(parts)
    
    def _group_list_items_by_level(self, items) -> Dict[int, List]:
        """Group list items by their nesting level"""
        grouped = {}
        for item in items:
            level = item.level
            if level not in grouped:
                grouped[level] = []
            grouped[level].append(item)
        return grouped
    
    def _add_nested_items_to_list(self, parts: List[str], grouped_items: Dict[int, List], 
                                 is_ordered: bool, current_level: int = 1) -> None:
        """Add items to list with proper nesting"""
        if current_level not in grouped_items:
            return
        
        for item in grouped_items[current_level]:
            # Add current item
            escaped_content = self._escape_latex(item.content)
            parts.append(f"  \\item {escaped_content}")
            
            # Check if there are nested items
            next_level = current_level + 1
            if next_level in grouped_items:
                # Add nested list
                list_env = "enumerate" if is_ordered else "itemize"
                parts.append(f"    \\begin{{{list_env}}}")
                
                # Recursively add nested items
                nested_grouped = {next_level: grouped_items[next_level]}
                self._add_nested_items_to_list(parts, nested_grouped, is_ordered, next_level)
                
                parts.append(f"    \\end{{{list_env}}}")
    
    def _generate_equation(self, equation) -> str:
        """Generate IEEE-style equation"""
        from app.models.document import EquationType
        
        if equation.latex_equivalent:
            if equation.is_display:
                # IEEE prefers numbered equations for display math
                return f"\\begin{{equation}}\n{equation.latex_equivalent}\n\\label{{eq:eq{equation.id}}}\n\\end{{equation}}"
            else:
                # Inline math
                return f"${equation.latex_equivalent}$"
        else:
            # Process OMML or fallback content
            if equation.equation_type == EquationType.OMML and hasattr(equation, 'omml_xml'):
                # Try to convert OMML to LaTeX
                latex_content = self._convert_omml_to_latex(equation.omml_xml)
                if latex_content:
                    if equation.is_display:
                        return f"\\begin{{equation}}\n{latex_content}\n\\label{{eq:eq{equation.id}}}\n\\end{{equation}}"
                    else:
                        return f"${latex_content}$"
            
            # Fallback to escaped content
            escaped_content = self._escape_latex(equation.content)
            if equation.is_display:
                return f"\\[{escaped_content}\\]"
            else:
                return f"${escaped_content}$"
    
    def _convert_omml_to_latex(self, omml_xml: str) -> str:
        """Convert OMML XML to LaTeX (enhanced implementation)"""
        if not omml_xml:
            return ""
        
        try:
            import xml.etree.ElementTree as ET
            
            # Parse OMML XML
            root = ET.fromstring(omml_xml)
            
            # Basic OMML to LaTeX conversion
            latex_parts = []
            self._process_omml_element(root, latex_parts)
            
            return ''.join(latex_parts).strip()
        except:
            # Fallback: extract text content
            import re
            text_content = re.sub(r'<[^>]+>', '', omml_xml)
            return self._basic_math_text_to_latex(text_content)
    
    def _process_omml_element(self, element, latex_parts: List[str]) -> None:
        """Process OMML element and convert to LaTeX"""
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        # Handle common OMML elements
        if tag == 'f':  # Fraction
            self._process_omml_fraction(element, latex_parts)
        elif tag == 'sup':  # Superscript
            self._process_omml_superscript(element, latex_parts)
        elif tag == 'sub':  # Subscript
            self._process_omml_subscript(element, latex_parts)
        elif tag == 'rad':  # Radical (square root)
            self._process_omml_radical(element, latex_parts)
        elif tag == 'r':  # Run (text)
            self._process_omml_run(element, latex_parts)
        else:
            # Default: process children
            for child in element:
                self._process_omml_element(child, latex_parts)
    
    def _process_omml_fraction(self, element, latex_parts: List[str]) -> None:
        """Process OMML fraction element"""
        latex_parts.append('\\frac{')
        
        # Find numerator and denominator
        num_found = False
        for child in element:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'num':
                for subchild in child:
                    self._process_omml_element(subchild, latex_parts)
                num_found = True
                break
        
        latex_parts.append('}{')
        
        for child in element:
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'den':
                for subchild in child:
                    self._process_omml_element(subchild, latex_parts)
                break
        
        latex_parts.append('}')
    
    def _process_omml_superscript(self, element, latex_parts: List[str]) -> None:
        """Process OMML superscript element"""
        latex_parts.append('^{')
        for child in element:
            self._process_omml_element(child, latex_parts)
        latex_parts.append('}')
    
    def _process_omml_subscript(self, element, latex_parts: List[str]) -> None:
        """Process OMML subscript element"""
        latex_parts.append('_{')
        for child in element:
            self._process_omml_element(child, latex_parts)
        latex_parts.append('}')
    
    def _process_omml_radical(self, element, latex_parts: List[str]) -> None:
        """Process OMML radical (square root) element"""
        latex_parts.append('\\sqrt{')
        for child in element:
            self._process_omml_element(child, latex_parts)
        latex_parts.append('}')
    
    def _process_omml_run(self, element, latex_parts: List[str]) -> None:
        """Process OMML text run element"""
        text = ''.join(element.itertext()).strip()
        if text:
            # Convert common mathematical symbols
            latex_text = self._basic_math_text_to_latex(text)
            latex_parts.append(latex_text)
    
    def _basic_math_text_to_latex(self, text: str) -> str:
        """Convert basic mathematical text to LaTeX"""
        # Common symbol replacements
        replacements = {
            '∑': '\\sum',
            '∫': '\\int',
            '∏': '\\prod',
            '√': '\\sqrt',
            '∞': '\\infty',
            'α': '\\alpha',
            'β': '\\beta',
            'γ': '\\gamma',
            'δ': '\\delta',
            'ε': '\\epsilon',
            'θ': '\\theta',
            'λ': '\\lambda',
            'μ': '\\mu',
            'π': '\\pi',
            'σ': '\\sigma',
            'τ': '\\tau',
            'φ': '\\phi',
            'ω': '\\omega',
            '≤': '\\leq',
            '≥': '\\geq',
            '≠': '\\neq',
            '±': '\\pm',
            '×': '\\times',
            '÷': '\\div',
        }
        
        result = text
        for symbol, latex in replacements.items():
            result = result.replace(symbol, latex)
        
        return result
    
    def _generate_figure(self, figure_id: int, caption: str = "", file_path: str = "") -> str:
        """Generate IEEE-style figure"""
        parts = []
        parts.append("\\begin{figure}[!t]")  # IEEE prefers top positioning
        parts.append("\\centering")
        
        if file_path:
            # Include the figure file
            parts.append(f"\\includegraphics[width=\\columnwidth]{{{file_path}}}")
        else:
            # Placeholder for missing figure
            parts.append("% TODO: Add figure file path")
            parts.append("\\rule{\\columnwidth}{2in}")  # Placeholder rectangle
        
        # IEEE figure caption format
        if caption:
            clean_caption = self._escape_latex(caption.strip())
            if not clean_caption.lower().startswith('fig'):
                clean_caption = f"Fig. {figure_id}. {clean_caption}"
        else:
            clean_caption = f"Fig. {figure_id}. Sample figure caption."
        
        parts.append(f"\\caption{{{clean_caption}}}")
        parts.append(f"\\label{{fig:fig{figure_id}}}")
        parts.append("\\end{figure}")
        
        return "\n".join(parts)
    
    def _process_figure_placeholders(self, content: str, section, analysis: DocumentAnalysis) -> str:
        """Replace figure placeholders with IEEE-formatted figures"""
        # Look for figure references in content
        figure_pattern = r'\[FIGURE_(\d+)\]'
        
        def replace_figure(match):
            figure_id = int(match.group(1))
            # In a real implementation, you'd extract figure info from the document
            return self._generate_figure(figure_id, caption=f"Figure {figure_id}", file_path="")
        
        return re.sub(figure_pattern, replace_figure, content)
    
    def _generate_bibliography(self) -> str:
        """Generate IEEE bibliography section"""
        # In the future, this could extract actual references from the document
        # For now, provide IEEE-style template references
        
        return """
\\begin{thebibliography}{99}
\\bibitem{ref1}
A. Author, ``Sample paper title,'' \\emph{IEEE Transactions on Sample}, vol. 1, no. 1, pp. 1--10, Jan. 2024.

\\bibitem{ref2}
B. Author and C. Coauthor, ``Another sample title,'' in \\emph{Proc. IEEE Conference}, 2024, pp. 123--130.

\\bibitem{ref3}
D. Researcher, \\emph{Book Title}, 2nd ed. Publisher, 2024.

\\bibitem{ref4}
E. Writer, ``Online article title,'' Website Name, 2024. [Online]. Available: https://example.com

\\end{thebibliography}"""
    
    def _extract_citations_from_content(self, content: str) -> List[str]:
        """Extract citation references from document content"""
        # Find all citation patterns like [1], [2], [3-5], etc.
        citation_pattern = r'\[(\d+(?:[,\s\-]\d+)*)\]'
        citations = set()
        
        for match in re.finditer(citation_pattern, content):
            citation_text = match.group(1)
            # Parse individual citation numbers
            for part in re.split(r'[,\s]+', citation_text):
                if '-' in part:
                    # Range like "3-5"
                    start, end = part.split('-')
                    for i in range(int(start), int(end) + 1):
                        citations.add(str(i))
                else:
                    citations.add(part)
        
        return sorted(citations, key=int)
    
    def _generate_dynamic_bibliography(self, analysis: DocumentAnalysis) -> str:
        """Generate bibliography based on citations found in document"""
        # Collect all citations from sections
        all_citations = set()
        
        for section in analysis.sections:
            if section.content:
                section_citations = self._extract_citations_from_content(section.content)
                all_citations.update(section_citations)
        
        if not all_citations:
            return self._generate_bibliography()  # Use default template
        
        # Generate bibliography entries for found citations
        max_citations = max(int(c) for c in all_citations) if all_citations else 10
        
        parts = []
        parts.append(f"\\begin{{thebibliography}}{{{max_citations}}}")
        
        for i in range(1, max_citations + 1):
            if str(i) in all_citations:
                parts.append(f"\\bibitem{{ref{i}}}")
                parts.append(f"Author {i}, ``Reference {i} title,'' \\emph{{Journal Name}}, vol. 1, no. 1, pp. 1--10, 2024.")
                parts.append("")
        
        parts.append("\\end{thebibliography}")
        
        return "\n".join(parts)
    
    def _generate_sections(self, analysis: DocumentAnalysis) -> str:
        """Generate IEEE document sections with enhanced content processing"""
        if not analysis.sections:
            return self._generate_default_sections()
        
        parts = []
        
        for section in analysis.sections:
            # Skip certain sections that are handled separately
            if self._should_skip_section(section.title):
                continue
            
            # Section command based on level
            cmd = self._get_section_command(section.level)
            
            # Clean and format section title
            clean_title = self._clean_section_title(section.title)
            
            # Generate section with IEEE formatting
            parts.append(f"{cmd}{{{clean_title}}}")
            parts.append(f"\\label{{sec:{self._generate_section_label(clean_title)}}}")
            
            # Process and format section content
            content = self._process_ieee_section_content(section, analysis)
            if content.strip():
                parts.append(content)
            else:
                # Add placeholder content for empty sections
                parts.append("% TODO: Add content for this section")
            
            parts.append("")
        
        return "\n".join(parts)
    
    def _should_skip_section(self, title: str) -> bool:
        """Check if section should be skipped (handled elsewhere)"""
        title_lower = title.lower().strip()
        skip_sections = [
            'abstract', 'keywords', 'references', 'bibliography', 
            'acknowledgments', 'acknowledgements'
        ]
        return any(skip in title_lower for skip in skip_sections)
    
    def _get_section_command(self, level) -> str:
        """Get appropriate LaTeX section command"""
        if level == SectionLevel.SECTION:
            return "\\section"
        elif level == SectionLevel.SUBSECTION:
            return "\\subsection"
        elif level == SectionLevel.SUBSUBSECTION:
            return "\\subsubsection"
        else:
            return "\\paragraph"
    
    def _clean_section_title(self, title: str) -> str:
        """Clean and format section title for IEEE"""
        # Remove section numbers if present
        title = re.sub(r'^\d+(?:\.\d+)*\s*\.?\s*', '', title)
        
        # Clean extra whitespace
        title = ' '.join(title.split())
        
        # IEEE prefers title case for major sections
        if not any(word.islower() for word in title.split()):
            # If title is all caps, convert to title case
            title = title.title()
        
        return title
    
    def _generate_section_label(self, title: str) -> str:
        """Generate LaTeX label from section title"""
        # Convert to lowercase and replace spaces/special chars
        label = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
        label = re.sub(r'\s+', '_', label.strip())
        return label
    
    def _process_ieee_section_content(self, section, analysis: DocumentAnalysis) -> str:
        """Process section content with IEEE-specific formatting"""
        if not section.content:
            return "% Section content not detected from document"
        
        # Start with the base content
        content = section.content.strip()
        
        if not content:
            return "% Empty section content"
        
        # Split into paragraphs for better processing
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        if not paragraphs:
            return "% No paragraphs found in section"
        
        processed_paragraphs = []
        for para in paragraphs:
            # Skip very short paragraphs that might be artifacts
            if len(para) < 3:
                continue
                
            # Process each paragraph
            processed_para = self._process_paragraph_content(para, section, analysis)
            if processed_para:
                processed_paragraphs.append(processed_para)
        
        if not processed_paragraphs:
            return f"% Content was filtered out (original: {len(content)} chars)"
        
        # Join paragraphs with proper spacing
        result = '\n\n'.join(processed_paragraphs)
        
        # Replace element placeholders with IEEE-formatted content
        result = self._replace_element_placeholders(result, section, analysis)
        
        return result
    
    def _process_paragraph_content(self, paragraph: str, section, analysis: DocumentAnalysis) -> str:
        """Process individual paragraph with IEEE formatting"""
        # Basic text cleaning
        para = paragraph.strip()
        
        if not para:
            return ""
        
        # Handle citations (basic implementation)
        para = self._format_ieee_citations(para)
        
        # Handle emphasis and formatting
        para = self._format_ieee_text_styling(para)
        
        # Escape LaTeX special characters - but preserve placeholders
        para = self._escape_latex_preserve_placeholders(para)
        
        return para
    
    def _escape_latex_preserve_placeholders(self, text: str) -> str:
        """Escape LaTeX characters but preserve element placeholders"""
        if not text:
            return ""
        
        # First, temporarily protect placeholders
        import re
        placeholders = []
        placeholder_pattern = r'\[(TABLE|LIST|EQUATION|FIGURE)_\d+\]'
        
        def protect_placeholder(match):
            placeholders.append(match.group(0))
            return f"PLACEHOLDER_{len(placeholders)-1}_PLACEHOLDER"
        
        # Protect placeholders
        text = re.sub(placeholder_pattern, protect_placeholder, text)
        
        # Escape LaTeX characters
        text = self._escape_latex(text)
        
        # Restore placeholders
        for i, placeholder in enumerate(placeholders):
            text = text.replace(f"PLACEHOLDER_{i}_PLACEHOLDER", placeholder)
        
        return text
    
    def _format_ieee_citations(self, text: str) -> str:
        """Format citations for IEEE style"""
        # Look for citation patterns like [1], [2-4], [1, 3, 5]
        citation_pattern = r'\[(\d+(?:[,\s\-]\d+)*)\]'
        
        def replace_citation(match):
            citation = match.group(1)
            # IEEE uses \cite{} command
            # For now, keep the bracket format but could be enhanced
            clean_citation = citation.replace(' ', '').replace('-', ',')
            return f"\\cite{{{clean_citation}}}"
        
        return re.sub(citation_pattern, replace_citation, text)
    
    def _format_ieee_text_styling(self, text: str) -> str:
        """Apply IEEE text styling"""
        # Convert bold text (basic patterns)
        text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
        text = re.sub(r'__(.*?)__', r'\\textbf{\1}', text)
        
        # Convert italic text
        text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
        text = re.sub(r'_(.*?)_', r'\\textit{\1}', text)
        
        # Convert typewriter/code text
        text = re.sub(r'`(.*?)`', r'\\texttt{\1}', text)
        
        return text
    
    def _replace_element_placeholders(self, content: str, section, analysis: DocumentAnalysis) -> str:
        """Replace placeholders with IEEE-formatted elements"""
        # Replace table placeholders
        for table_id in section.contains_tables:
            table = next((t for t in analysis.tables if t.id == table_id), None)
            if table:
                table_latex = self._generate_table(table)
                content = content.replace(f"[TABLE_{table_id}]", f"\n\n{table_latex}\n")
        
        # Replace list placeholders
        for list_id in section.contains_lists:
            doc_list = next((l for l in analysis.lists if l.id == list_id), None)
            if doc_list:
                list_latex = self._generate_list(doc_list)
                content = content.replace(f"[LIST_{list_id}]", f"\n\n{list_latex}\n")
        
        # Replace equation placeholders
        for eq_id in section.contains_equations:
            equation = next((e for e in analysis.equations if e.id == eq_id), None)
            if equation:
                eq_latex = self._generate_equation(equation)
                content = content.replace(f"[EQUATION_{eq_id}]", eq_latex)
        
        return content
    
    def _generate_default_sections(self) -> str:
        """Generate default IEEE sections if none are detected"""
        return """\\section{Introduction}
\\label{sec:introduction}
This section should contain the introduction content. The document processing system was unable to detect section content from the uploaded document. This may indicate that the document structure is not clearly defined or the content extraction needs improvement.

\\section{Related Work}
\\label{sec:related_work}
This section should contain related work content.

\\section{Methodology}
\\label{sec:methodology}
This section should contain methodology content.

\\section{Results}
\\label{sec:results}
This section should contain results content.

\\section{Conclusion}
\\label{sec:conclusion}
This section should contain conclusion content."""