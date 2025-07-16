"""
LaTeX Generator Service
Converts document analysis to high-quality LaTeX output

This module now uses a factory pattern for template-specific generators
while maintaining backward compatibility with the original interface.
"""

import re
from typing import List, Dict, Any, Optional
from app.models.document import (
    DocumentAnalysis, LatexTemplate, Section, DocumentList, DocumentTable,
    Equation, ListType, SectionLevel
)
from .latex.generator_factory import LatexGeneratorFactory


class LatexGenerator:
    """
    Generate LaTeX code from document analysis
    
    This class now serves as a wrapper around the new template-specific
    generators, maintaining backward compatibility while providing the
    benefits of the separated architecture.
    """
    
    def __init__(self, template: LatexTemplate):
        self.template = template
        self._new_generator = None
        self._use_new_architecture = True  # Flag to control architecture usage
        
        # Try to use new architecture, fall back to legacy if needed
        try:
            if LatexGeneratorFactory.is_template_supported(template):
                self._new_generator = LatexGeneratorFactory.create_generator(template)
            else:
                self._use_new_architecture = False
        except Exception:
            self._use_new_architecture = False
        
        # Legacy configuration (fallback)
        if not self._use_new_architecture:
            # Template-specific configurations
            self.configs = {
                LatexTemplate.IEEE: {
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
                    "list_env": {"ordered": "enumerate", "unordered": "itemize"}
                },
                LatexTemplate.ACM: {
                    "document_class": "\\documentclass[acmtog]{acmart}",
                    "packages": [
                        "\\usepackage{booktabs}",
                        "\\usepackage{graphicx}",
                        "\\usepackage{amsmath}",
                        "\\usepackage{amssymb}"
                    ],
                    "table_style": "acm",
                    "list_env": {"ordered": "enumerate", "unordered": "itemize"}
                },
                LatexTemplate.SPRINGER: {
                    "document_class": "\\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}",
                    "packages": [
                        "\\usepackage{graphicx}",
                        "\\usepackage{multirow}",
                        "\\usepackage{amsmath,amssymb,amsfonts}",
                        "\\usepackage{amsthm}",
                        "\\usepackage{mathrsfs}",
                        "\\usepackage[title]{appendix}",
                        "\\usepackage{xcolor}",
                        "\\usepackage{textcomp}",
                        "\\usepackage{manyfoot}",
                        "\\usepackage{booktabs}"
                    ],
                    "table_style": "springer",
                    "list_env": {"ordered": "enumerate", "unordered": "itemize"}
                }
            }
    
    async def generate(self, analysis: DocumentAnalysis) -> str:
        """
        Generate complete LaTeX document
        
        Args:
            analysis: Document analysis result
            
        Returns:
            str: Complete LaTeX document
        """
        # Use new architecture if available
        if self._use_new_architecture and self._new_generator:
            return await self._new_generator.generate(analysis)
        
        # Legacy fallback implementation
        latex_parts = []
        
        # Document class and packages
        latex_parts.append(self._generate_preamble())
        
        # Document beginning
        latex_parts.append("\\begin{document}")
        latex_parts.append("")
        
        # Template-specific ordering
        if self.template == LatexTemplate.ACM:
            # ACM requires abstract before maketitle
            latex_parts.append(self._generate_title_metadata(analysis))
            if analysis.abstract:
                latex_parts.append(self._generate_abstract(analysis.abstract.content))
            if analysis.keywords:
                latex_parts.append(self._generate_keywords(analysis.keywords.content))
            latex_parts.append("\\maketitle")
            latex_parts.append("")
        else:
            # IEEE and Springer: title first, then abstract/keywords
            latex_parts.append(self._generate_title_section(analysis))
            if analysis.abstract:
                latex_parts.append(self._generate_abstract(analysis.abstract.content))
            if analysis.keywords:
                latex_parts.append(self._generate_keywords(analysis.keywords.content))
        
        # Document sections
        latex_parts.append(self._generate_sections(analysis))
        
        # Bibliography (template-specific)
        latex_parts.append(self._generate_bibliography())
        
        # Document end
        latex_parts.append("\\end{document}")
        
        return "\n".join(latex_parts)
    
    def is_using_new_architecture(self) -> bool:
        """Check if the generator is using the new separated architecture"""
        return self._use_new_architecture
    
    def get_supported_templates(self) -> List[LatexTemplate]:
        """Get list of templates supported by the new architecture"""
        return LatexGeneratorFactory.get_supported_templates()
    
    def validate_latex(self, latex_content: str) -> List[str]:
        """Validate LaTeX content and return warnings"""
        # Use new generator if available
        if self._use_new_architecture and self._new_generator:
            return self._new_generator.validate_latex(latex_content)
        
        # Legacy validation implementation
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
    
    # Legacy methods (for fallback compatibility)
    def _generate_preamble(self) -> str:
        """Generate document preamble with class and packages"""
        config = self.configs[self.template]
        preamble_parts = []
        
        # Document class
        preamble_parts.append(config["document_class"])
        preamble_parts.append("")
        
        # Packages
        preamble_parts.extend(config["packages"])
        preamble_parts.append("")
        
        # Template-specific additions
        if self.template == LatexTemplate.ACM:
            preamble_parts.extend([
                "\\setcopyright{acmlicensed}",
                "\\copyrightyear{2024}",
                "\\acmYear{2024}",
                "\\acmDOI{XXXXXXX.XXXXXXX}",
                "\\citestyle{acmauthoryear}",
                ""
            ])
        elif self.template == LatexTemplate.SPRINGER:
            preamble_parts.extend([
                "\\theoremstyle{thmstyleone}",
                "\\newtheorem{theorem}{Theorem}",
                "\\newtheorem{proposition}[theorem]{Proposition}",
                "",
                "\\theoremstyle{thmstyletwo}",
                "\\newtheorem{example}{Example}",
                "\\newtheorem{remark}{Remark}",
                "",
                "\\theoremstyle{thmstylethree}",
                "\\newtheorem{definition}{Definition}",
                "",
                "\\raggedbottom",
                ""
            ])
        
        return "\n".join(preamble_parts)
    
    def _generate_title_metadata(self, analysis: DocumentAnalysis) -> str:
        """Generate title and authors metadata only (for ACM template)"""
        parts = []
        
        # Title
        title = analysis.title.content if analysis.title else "Document Title"
        parts.append(f"\\title{{{title}}}")
        
        # Authors
        if analysis.authors:
            author_latex = self._generate_authors(analysis.authors)
            parts.append(author_latex)
        else:
            parts.append("\\author{Author Name}")
            parts.append("\\affiliation{\\institution{Institution Name}\\city{City}\\country{Country}}")
        
        parts.append("")
        return "\n".join(parts)
    
    def _generate_title_section(self, analysis: DocumentAnalysis) -> str:
        """Generate title, authors, and affiliations"""
        parts = []
        
        # Title
        title = analysis.title.content if analysis.title else "Document Title"
        
        if self.template == LatexTemplate.IEEE:
            parts.append(f"\\title{{{title}}}")
        elif self.template == LatexTemplate.ACM:
            parts.append(f"\\title{{{title}}}")
        elif self.template == LatexTemplate.SPRINGER:
            parts.append(f"\\title[{title}]{{{title}}}")
        
        # Authors
        if analysis.authors:
            author_latex = self._generate_authors(analysis.authors)
            parts.append(author_latex)
        else:
            if self.template == LatexTemplate.SPRINGER:
                parts.append("\\author[1]{\\fnm{Author} \\sur{Name}}\\email{author@domain.com}")
                parts.append("\\affil*[1]{\\orgdiv{Department}, \\orgname{Institution}, \\orgaddress{\\city{City}, \\country{Country}}}")
            else:
                parts.append("\\author{Author Name}")
        
        parts.append("\\maketitle")
        parts.append("")
        
        return "\n".join(parts)
    
    def _generate_authors(self, authors) -> str:
        """Generate author section based on template - legacy fallback"""
        if not authors.names:
            return "\\author{Author Name}"
        
        # Simplified legacy implementation
        if self.template == LatexTemplate.IEEE:
            author_blocks = []
            for i, name in enumerate(authors.names):
                formatted_name = self._format_author_name(name)
                email = authors.emails[i] if i < len(authors.emails) else "email@domain.com"
                
                block = f"\\IEEEauthorblockN{{{formatted_name}}}\\IEEEauthorblockA{{Email: {email}}}"
                author_blocks.append(block)
            
            return f"\\author{{\n{('\\n\\and\\n').join(author_blocks)}\n}}"
        else:
            return "\\author{" + ", ".join(authors.names) + "}"
    
    def _generate_abstract(self, abstract: str) -> str:
        """Generate abstract section"""
        cleaned_abstract = abstract.strip()
        if not cleaned_abstract:
            return ""
        
        formatted_abstract = self._escape_latex(cleaned_abstract)
        return f"\\begin{{abstract}}\n{formatted_abstract}\n\\end{{abstract}}\n"
    
    def _generate_keywords(self, keywords: str) -> str:
        """Generate keywords section"""
        if self.template == LatexTemplate.IEEE:
            return f"\\begin{{IEEEkeywords}}\n{self._escape_latex(keywords)}\n\\end{{IEEEkeywords}}\n"
        elif self.template == LatexTemplate.ACM:
            return f"\\keywords{{{self._escape_latex(keywords)}}}\n"
        else:
            return f"\\keywords{{{self._escape_latex(keywords)}}}\n"
    
    def _generate_sections(self, analysis: DocumentAnalysis) -> str:
        """Generate document sections with content"""
        parts = []
        
        for section in analysis.sections:
            if section.level == SectionLevel.SECTION:
                cmd = "\\section"
            elif section.level == SectionLevel.SUBSECTION:
                cmd = "\\subsection"
            elif section.level == SectionLevel.SUBSUBSECTION:
                cmd = "\\subsubsection"
            else:
                cmd = "\\paragraph"
            
            parts.append(f"{cmd}{{{section.title}}}")
            content = self._escape_latex(section.content)
            parts.append(content)
            parts.append("")
        
        return "\n".join(parts)
    
    def _generate_bibliography(self) -> str:
        """Generate bibliography section"""
        if self.template == LatexTemplate.IEEE:
            return """
\\begin{thebibliography}{1}
\\bibitem{ref1} Author, ``Title,'' \\emph{Journal}, vol. 1, no. 1, pp. 1--10, 2024.
\\end{thebibliography}"""
        elif self.template == LatexTemplate.ACM:
            return """
\\bibliographystyle{ACM-Reference-Format}
\\bibliography{references}"""
        else:  # Springer
            return """
\\begin{thebibliography}{1}
\\bibitem{ref1} Author, A.: Title of the paper. Journal Name \\textbf{1}, 1--10 (2024)
\\end{thebibliography}"""
    
    def _format_author_name(self, name: str) -> str:
        """Format author name with proper capitalization"""
        if not name:
            return ""
        return ' '.join(word.capitalize() for word in name.split())
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
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