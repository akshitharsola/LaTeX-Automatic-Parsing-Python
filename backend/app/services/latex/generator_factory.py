"""
LaTeX Generator Factory
Creates template-specific generators using factory pattern
"""

from typing import Type
from app.models.document import LatexTemplate
from .base_generator import BaseLatexGenerator
from .ieee_generator import IEEELatexGenerator


class LatexGeneratorFactory:
    """Factory for creating template-specific LaTeX generators"""
    
    # Registry of available generators
    _generators = {
        LatexTemplate.IEEE: IEEELatexGenerator,
        # Note: ACM and Springer generators will be added later
        # LatexTemplate.ACM: ACMLatexGenerator,
        # LatexTemplate.SPRINGER: SpringerLatexGenerator,
    }
    
    @classmethod
    def create_generator(cls, template: LatexTemplate) -> BaseLatexGenerator:
        """
        Create a generator for the specified template
        
        Args:
            template: The LaTeX template type
            
        Returns:
            BaseLatexGenerator: Template-specific generator instance
            
        Raises:
            ValueError: If template is not supported
        """
        if template not in cls._generators:
            raise ValueError(f"Unsupported template: {template}. "
                           f"Available templates: {list(cls._generators.keys())}")
        
        generator_class = cls._generators[template]
        return generator_class()
    
    @classmethod
    def get_supported_templates(cls) -> list[LatexTemplate]:
        """
        Get list of supported templates
        
        Returns:
            List[LatexTemplate]: List of supported template types
        """
        return list(cls._generators.keys())
    
    @classmethod
    def is_template_supported(cls, template: LatexTemplate) -> bool:
        """
        Check if a template is supported
        
        Args:
            template: The template to check
            
        Returns:
            bool: True if template is supported, False otherwise
        """
        return template in cls._generators
    
    @classmethod
    def register_generator(cls, template: LatexTemplate, 
                          generator_class: Type[BaseLatexGenerator]) -> None:
        """
        Register a new generator for a template
        
        Args:
            template: The template type
            generator_class: The generator class to register
        """
        cls._generators[template] = generator_class