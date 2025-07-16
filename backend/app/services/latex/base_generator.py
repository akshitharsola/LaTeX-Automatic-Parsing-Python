"""
Base LaTeX Generator Abstract Class
Defines common interface for all template-specific generators
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.document import (
    DocumentAnalysis, LatexTemplate, Section, DocumentList, DocumentTable,
    Equation, ListType, SectionLevel
)


class BaseLatexGenerator(ABC):
    """Abstract base class for LaTeX generators"""
    
    def __init__(self, template: LatexTemplate):
        self.template = template
        self._config = self._get_template_config()
    
    @abstractmethod
    def _get_template_config(self) -> Dict[str, Any]:
        """Get template-specific configuration"""
        pass
    
    async def generate(self, analysis: DocumentAnalysis) -> str:
        """
        Generate complete LaTeX document
        
        Args:
            analysis: Document analysis result
            
        Returns:
            str: Complete LaTeX document
        """
        latex_parts = []
        
        # Document class and packages
        latex_parts.append(self._generate_preamble())
        
        # Document beginning
        latex_parts.append("\\begin{document}")
        latex_parts.append("")
        
        # Template-specific content ordering
        latex_parts.extend(self._generate_document_content(analysis))
        
        # Document end
        latex_parts.append("\\end{document}")
        
        return "\n".join(latex_parts)
    
    @abstractmethod
    def _generate_document_content(self, analysis: DocumentAnalysis) -> List[str]:
        """Generate the main document content with template-specific ordering"""
        pass
    
    @abstractmethod
    def _generate_preamble(self) -> str:
        """Generate document preamble with class and packages"""
        pass
    
    @abstractmethod
    def _generate_title_section(self, analysis: DocumentAnalysis) -> str:
        """Generate title, authors, and affiliations"""
        pass
    
    def _generate_abstract(self, abstract: str) -> str:
        """Generate abstract section - common implementation"""
        cleaned_abstract = abstract.strip()
        if not cleaned_abstract:
            return ""
        
        formatted_abstract = self._escape_latex(cleaned_abstract)
        return f"\\begin{{abstract}}\n{formatted_abstract}\n\\end{{abstract}}\n"
    
    @abstractmethod
    def _generate_keywords(self, keywords: str) -> str:
        """Generate keywords section - template-specific implementation"""
        pass
    
    def _generate_sections(self, analysis: DocumentAnalysis) -> str:
        """Generate document sections with content"""
        parts = []
        
        for section in analysis.sections:
            # Section command based on level
            if section.level == SectionLevel.SECTION:
                cmd = "\\section"
            elif section.level == SectionLevel.SUBSECTION:
                cmd = "\\subsection"
            elif section.level == SectionLevel.SUBSUBSECTION:
                cmd = "\\subsubsection"
            else:
                cmd = "\\paragraph"
            
            # Section title
            parts.append(f"{cmd}{{{section.title}}}")
            
            # Section content with embedded elements
            content = self._process_section_content(section, analysis)
            parts.append(content)
            parts.append("")
        
        return "\n".join(parts)
    
    def _process_section_content(self, section: Section, analysis: DocumentAnalysis) -> str:
        """Process section content and embed tables, lists, equations"""
        content = section.content
        
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
        
        return self._escape_latex(content)
    
    @abstractmethod
    def _generate_table(self, table: DocumentTable) -> str:
        """Generate LaTeX table - template-specific implementation"""
        pass
    
    def _generate_list(self, doc_list: DocumentList) -> str:
        """Generate LaTeX list - common implementation with template config"""
        if doc_list.list_type == ListType.ORDERED:
            env = "enumerate"
        else:
            env = "itemize"
        
        parts = []
        parts.append(f"\\begin{{{env}}}")
        
        for item in doc_list.items:
            # Handle nesting (simplified)
            indent = "  " * (item.level - 1)
            escaped_content = self._escape_latex(item.content)
            parts.append(f"{indent}\\item {escaped_content}")
        
        parts.append(f"\\end{{{env}}}")
        
        return "\n".join(parts)
    
    def _generate_equation(self, equation: Equation) -> str:
        """Generate LaTeX equation - common implementation"""
        if equation.latex_equivalent:
            if equation.is_display:
                return f"\\[{equation.latex_equivalent}\\]"
            else:
                return f"${equation.latex_equivalent}$"
        else:
            # Fallback to original content
            return f"${self._escape_latex(equation.content)}$"
    
    @abstractmethod
    def _generate_bibliography(self) -> str:
        """Generate bibliography section - template-specific implementation"""
        pass
    
    @abstractmethod
    def _generate_authors(self, authors) -> str:
        """Generate author section - template-specific implementation"""
        pass
    
    def _format_author_name(self, name: str) -> str:
        """Format author name with proper capitalization"""
        if not name:
            return ""
        
        return ' '.join(word.capitalize() for word in name.split())
    
    def _expand_department(self, dept: str, template: str) -> str:
        """Expand department abbreviations based on template"""
        if not dept:
            return "Computer Science"
        
        expansions = {
            "acm": {
                'cse': 'Computer Science and Engineering',
                'cs': 'Computer Science',
                'it': 'Information Technology',
                'ece': 'Electronics and Communication Engineering',
                'eee': 'Electrical and Electronics Engineering',
                'me': 'Mechanical Engineering',
                'ce': 'Civil Engineering',
            },
            "ieee": {
                'cse': 'Computer Science',
                'cs': 'Computer Science',
                'it': 'Information Technology',
                'ece': 'Electronics and Communication Engineering',
                'eee': 'Electrical and Electronics Engineering',
                'me': 'Mechanical Engineering',
                'ce': 'Civil Engineering',
            },
            "springer": {
                'cse': 'Computer Science and Engineering',
                'cs': 'Computer Science and Engineering',
                'it': 'Information Technology',
                'ece': 'Electronics and Communication Engineering',
                'eee': 'Electrical and Electronics Engineering',
                'me': 'Mechanical Engineering',
                'ce': 'Civil Engineering',
            }
        }
        
        template_expansions = expansions.get(template, expansions["ieee"])
        return template_expansions.get(dept.lower().strip(), dept)
    
    def _get_ordinal(self, num: int) -> str:
        """Get ordinal number with LaTeX superscript"""
        if num == 1:
            return "1\\textsuperscript{st}"
        elif num == 2:
            return "2\\textsuperscript{nd}"
        elif num == 3:
            return "3\\textsuperscript{rd}"
        else:
            return f"{num}\\textsuperscript{{th}}"
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # LaTeX special characters
        replacements = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        
        return result
    
    def validate_latex(self, latex_content: str) -> List[str]:
        """Validate LaTeX content and return warnings"""
        warnings = []
        
        # Check for unmatched braces
        open_braces = latex_content.count('{')
        close_braces = latex_content.count('}')
        if open_braces != close_braces:
            warnings.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
        
        # Check for unmatched dollar signs
        dollar_count = latex_content.count('$')
        if dollar_count % 2 != 0:
            warnings.append("Odd number of dollar signs - may cause math mode issues")
        
        # Check for required structure
        if '\\begin{document}' not in latex_content:
            warnings.append("Missing \\begin{document}")
        if '\\end{document}' not in latex_content:
            warnings.append("Missing \\end{document}")
        
        return warnings