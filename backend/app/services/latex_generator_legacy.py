"""
LaTeX Generator Service
Converts document analysis to high-quality LaTeX output
"""

import re
from typing import List, Dict, Any, Optional
from app.models.document import (
    DocumentAnalysis, LatexTemplate, Section, DocumentList, DocumentTable,
    Equation, ListType, SectionLevel
)


class LatexGenerator:
    """Generate LaTeX code from document analysis"""
    
    def __init__(self, template: LatexTemplate):
        self.template = template
        
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
        """Generate author section based on template"""
        if not authors.names:
            return "\\author{Author Name}"
        
        if self.template == LatexTemplate.IEEE:
            # IEEE format with IEEEauthorblock
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
        
        elif self.template == LatexTemplate.ACM:
            # ACM format with individual author blocks and proper affiliations
            author_parts = []
            
            # Process each author individually
            for i, name in enumerate(authors.names):
                # Format author name
                formatted_name = self._format_author_name(name)
                author_parts.append(f"\\author{{{formatted_name}}}")
                
                # Add email if available
                if i < len(authors.emails):
                    author_parts.append(f"\\email{{{authors.emails[i]}}}")
                
                # Add affiliation with proper structure
                affiliation = authors.affiliations[i] if i < len(authors.affiliations) else "Institution"
                
                # Handle department expansion for ACM
                if hasattr(authors, 'departments') and i < len(authors.departments):
                    dept = self._expand_department(authors.departments[i], "acm")
                    full_affiliation = f"Department of {dept}, {affiliation}"
                else:
                    full_affiliation = affiliation
                
                # Extract city and country from affiliation if available
                affiliation_parts = full_affiliation.split(',')
                institution = affiliation_parts[0].strip()
                city = affiliation_parts[1].strip() if len(affiliation_parts) > 1 else "City"
                country = affiliation_parts[2].strip() if len(affiliation_parts) > 2 else "Country"
                
                author_parts.append(f"""\\affiliation{{%
  \\institution{{{institution}}}
  \\city{{{city}}}
  \\country{{{country}}}
}}""")
            
            return "\n".join(author_parts)
        
        elif self.template == LatexTemplate.SPRINGER:
            # Springer format with \\fnm and \\sur based on official template
            author_parts = []
            
            # Generate authors
            for i, name in enumerate(authors.names):
                name_parts = name.split()
                first_name = name_parts[0] if name_parts else name
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                # Check if this is a corresponding author
                if hasattr(authors, 'corresponding_indices') and i in authors.corresponding_indices:
                    author_parts.append(f"\\author*[{i+1}]{{\\fnm{{{first_name}}} \\sur{{{last_name}}}}}")
                else:
                    author_parts.append(f"\\author[{i+1}]{{\\fnm{{{first_name}}} \\sur{{{last_name}}}}}")
                
                if i < len(authors.emails):
                    author_parts.append(f"\\email{{{authors.emails[i]}}}")
            
            # Add affiliations using \\affil format
            if authors.affiliations:
                for i, affiliation in enumerate(authors.affiliations):
                    # Handle department expansion for Springer
                    if hasattr(authors, 'departments') and i < len(authors.departments):
                        dept = self._expand_department(authors.departments[i], "springer")
                        dept_text = f"Department of {dept}"
                    else:
                        dept_text = "Department"
                    
                    # Use proper Springer affiliation format
                    if i == 0:  # First affiliation gets the * for corresponding author
                        author_parts.append(f"\\affil*[{i+1}]{{\\orgdiv{{{dept_text}}}, \\orgname{{{affiliation}}}, \\orgaddress{{\\city{{City}}, \\country{{Country}}}}}}")
                    else:
                        author_parts.append(f"\\affil[{i+1}]{{\\orgdiv{{{dept_text}}}, \\orgname{{{affiliation}}}, \\orgaddress{{\\city{{City}}, \\country{{Country}}}}}}")
            else:
                # Fallback affiliation
                author_parts.append(f"\\affil*[1]{{\\orgdiv{{Department}}, \\orgname{{Institution}}, \\orgaddress{{\\city{{City}}, \\country{{Country}}}}}}")
            
            return "\n".join(author_parts)
        
        return "\\author{" + ", ".join(authors.names) + "}"
    
    def _generate_abstract(self, abstract: str) -> str:
        """Generate abstract section"""
        # Clean and format abstract text to prevent missing first character
        cleaned_abstract = abstract.strip()
        if not cleaned_abstract:
            return ""
        
        # Ensure proper spacing and formatting
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
    
    def _generate_table(self, table: DocumentTable) -> str:
        """Generate LaTeX table"""
        if not table.cells or not table.cells[0]:
            return ""
        
        cols = len(table.cells[0])
        
        # Table configuration based on template
        if self.template == LatexTemplate.IEEE:
            col_spec = "|" + "|".join(["c"] * cols) + "|"
            table_env = "table"
            tab_env = "tabular"
            row_sep = " \\\\ \\hline"
        elif self.template == LatexTemplate.ACM:
            col_spec = "l" * cols
            table_env = "table"
            tab_env = "tabular"
            row_sep = " \\\\"
        else:  # Springer
            col_spec = "l" * cols
            table_env = "table"
            tab_env = "tabular"
            row_sep = " \\\\"
        
        parts = []
        parts.append(f"\\begin{{{table_env}}}[!htbp]")
        parts.append("\\centering")
        
        if table.caption:
            parts.append(f"\\caption{{{self._escape_latex(table.caption)}}}")
        
        parts.append(f"\\label{{tab:table{table.id}}}")
        parts.append(f"\\begin{{{tab_env}}}{{{col_spec}}}")
        
        # Add top rule for ACM/Springer
        if self.template in [LatexTemplate.ACM, LatexTemplate.SPRINGER]:
            parts.append("\\toprule")
        elif self.template == LatexTemplate.IEEE:
            parts.append("\\hline")
        
        # Table rows
        for i, row in enumerate(table.cells):
            row_content = " & ".join(self._escape_latex(cell.content) for cell in row)
            parts.append(row_content + row_sep)
            
            # Add midrule after header
            if i == 0 and table.has_headers:
                if self.template in [LatexTemplate.ACM, LatexTemplate.SPRINGER]:
                    parts.append("\\midrule")
        
        # Add bottom rule
        if self.template in [LatexTemplate.ACM, LatexTemplate.SPRINGER]:
            parts.append("\\bottomrule")
        
        parts.append(f"\\end{{{tab_env}}}")
        parts.append(f"\\end{{{table_env}}}")
        
        return "\n".join(parts)
    
    def _generate_list(self, doc_list: DocumentList) -> str:
        """Generate LaTeX list"""
        config = self.configs[self.template]
        
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
        """Generate LaTeX equation"""
        if equation.latex_equivalent:
            if equation.is_display:
                return f"\\[{equation.latex_equivalent}\\]"
            else:
                return f"${equation.latex_equivalent}$"
        else:
            # Fallback to original content
            return f"${self._escape_latex(equation.content)}$"
    
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
        
        # Check for common errors
        if '\\\\' in latex_content and '\\\\\\\\' not in latex_content:
            # This is actually OK, but let's check for excessive line breaks
            excessive_breaks = re.findall(r'\\\\\\\\+', latex_content)
            if excessive_breaks:
                warnings.append("Found excessive line breaks (\\\\\\\\)")
        
        return warnings