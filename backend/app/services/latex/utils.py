"""
LaTeX Utilities
Shared utility functions for LaTeX generation
"""

import re
from typing import Dict, List, Tuple


def clean_text_for_latex(text: str) -> str:
    """Clean and prepare text for LaTeX processing"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove Word-specific artifacts
    text = re.sub(r'\ufeff', '', text)  # Remove BOM
    text = re.sub(r'\u00a0', ' ', text)  # Non-breaking space to regular space
    
    return text


def extract_city_country_from_affiliation(affiliation: str) -> Tuple[str, str, str]:
    """
    Extract institution, city, and country from affiliation string
    
    Args:
        affiliation: Full affiliation string
        
    Returns:
        Tuple of (institution, city, country)
    """
    if not affiliation:
        return "Institution", "City", "Country"
    
    parts = [part.strip() for part in affiliation.split(',')]
    
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        return parts[0], parts[1], "Country"
    else:
        return parts[0], "City", "Country"


def format_latex_title(title: str) -> str:
    """Format title for LaTeX with proper escaping and formatting"""
    if not title:
        return "Document Title"
    
    # Clean the title
    title = clean_text_for_latex(title)
    
    # Handle subtitle formatting (if separated by colon)
    if ':' in title:
        main_title, subtitle = title.split(':', 1)
        title = f"{main_title.strip()}: {subtitle.strip()}"
    
    return title


def validate_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def normalize_author_name(name: str) -> Tuple[str, str]:
    """
    Normalize author name and split into first and last names
    
    Args:
        name: Full author name
        
    Returns:
        Tuple of (first_name, last_name)
    """
    if not name:
        return "Author", "Name"
    
    name = clean_text_for_latex(name)
    parts = name.split()
    
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        # Multiple parts: first name is first part, last name is rest
        return parts[0], " ".join(parts[1:])


def detect_section_level(text: str) -> int:
    """
    Detect section level based on text formatting or numbering
    
    Args:
        text: Section title text
        
    Returns:
        int: Section level (1=section, 2=subsection, etc.)
    """
    text = text.strip()
    
    # Check for numbered sections
    if re.match(r'^\d+\.', text):
        return 1  # Section
    elif re.match(r'^\d+\.\d+\.', text):
        return 2  # Subsection
    elif re.match(r'^\d+\.\d+\.\d+\.', text):
        return 3  # Subsubsection
    
    # Check for common section keywords
    lower_text = text.lower()
    if any(keyword in lower_text for keyword in ['introduction', 'conclusion', 'related work', 'methodology']):
        return 1
    
    # Default to subsection if uncertain
    return 2


def generate_latex_label(text: str, prefix: str = "") -> str:
    """
    Generate a LaTeX label from text
    
    Args:
        text: Text to convert to label
        prefix: Optional prefix for the label
        
    Returns:
        str: LaTeX-safe label
    """
    if not text:
        return f"{prefix}:unnamed"
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    label = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
    label = re.sub(r'\s+', '-', label.strip())
    label = re.sub(r'-+', '-', label)  # Remove multiple consecutive hyphens
    label = label.strip('-')  # Remove leading/trailing hyphens
    
    if prefix:
        return f"{prefix}:{label}"
    return label


def count_latex_environments(latex_content: str) -> Dict[str, int]:
    """
    Count LaTeX environments in content
    
    Args:
        latex_content: LaTeX source code
        
    Returns:
        Dict with environment counts
    """
    environments = {}
    
    # Find all \begin{env} patterns
    begin_pattern = r'\\begin\{([^}]+)\}'
    matches = re.findall(begin_pattern, latex_content)
    
    for env in matches:
        environments[env] = environments.get(env, 0) + 1
    
    return environments