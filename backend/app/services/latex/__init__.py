"""
LaTeX Generation Package
Provides template-specific LaTeX generators with common interface
"""

from .base_generator import BaseLatexGenerator
from .ieee_generator import IEEELatexGenerator
from .acm_generator import ACMLatexGenerator
from .springer_generator import SpringerLatexGenerator
from .generator_factory import LatexGeneratorFactory
from .utils import (
    clean_text_for_latex,
    extract_city_country_from_affiliation,
    format_latex_title,
    validate_email,
    normalize_author_name,
    detect_section_level,
    generate_latex_label,
    count_latex_environments
)

__all__ = [
    'BaseLatexGenerator',
    'IEEELatexGenerator',
    'ACMLatexGenerator',
    'SpringerLatexGenerator',
    'LatexGeneratorFactory',
    'clean_text_for_latex',
    'extract_city_country_from_affiliation',
    'format_latex_title',
    'validate_email',
    'normalize_author_name',
    'detect_section_level',
    'generate_latex_label',
    'count_latex_environments'
]