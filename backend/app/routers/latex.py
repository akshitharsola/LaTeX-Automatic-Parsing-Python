"""
LaTeX generation router
Handles conversion of document analysis to LaTeX format
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import PlainTextResponse

from app.models.document import DocumentAnalysis, LatexOutput, LatexTemplate
from app.services.latex_generator import LatexGenerator

router = APIRouter()

@router.post("/generate", response_model=LatexOutput)
async def generate_latex(
    analysis: DocumentAnalysis = Body(...),
    template: LatexTemplate = Body(default=LatexTemplate.IEEE)
):
    """
    Generate LaTeX code from document analysis
    
    Args:
        analysis: Document analysis result
        template: LaTeX template to use
    
    Returns:
        LatexOutput: Generated LaTeX with metadata
    """
    start_time = time.time()
    
    try:
        generator = LatexGenerator(template)
        latex_content = await generator.generate(analysis)
        
        # Validate LaTeX
        warnings = generator.validate_latex(latex_content)
        
        return LatexOutput(
            content=latex_content,
            template=template,
            sections_count=len(analysis.sections),
            tables_count=len(analysis.tables),
            equations_count=len(analysis.equations),
            lists_count=len(analysis.lists),
            validation_warnings=warnings,
            generation_time=time.time() - start_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating LaTeX: {str(e)}"
        )


@router.post("/generate/download")
async def download_latex(
    analysis: DocumentAnalysis = Body(...),
    template: LatexTemplate = Body(default=LatexTemplate.IEEE)
):
    """
    Generate and download LaTeX file
    
    Args:
        analysis: Document analysis result
        template: LaTeX template to use
    
    Returns:
        PlainTextResponse: LaTeX content as downloadable file
    """
    try:
        generator = LatexGenerator(template)
        latex_content = await generator.generate(analysis)
        
        filename = f"{analysis.filename.replace('.docx', '')}_{template.value}.tex"
        
        return PlainTextResponse(
            content=latex_content,
            media_type="application/x-tex",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating LaTeX file: {str(e)}"
        )


@router.get("/templates")
async def get_templates():
    """
    Get available LaTeX templates
    
    Returns:
        Dict: Available templates with descriptions
    """
    return {
        "templates": {
            "ieee": {
                "name": "IEEE Conference",
                "description": "IEEE conference paper format with proper table styling",
                "document_class": "IEEEtran",
                "features": ["Two-column layout", "IEEE-specific formatting", "Conference style"]
            },
            "acm": {
                "name": "ACM Conference",
                "description": "ACM conference paper format with modern styling",
                "document_class": "acmart",
                "features": ["ACM citation style", "Modern layout", "Author affiliations"]
            },
            "springer": {
                "name": "Springer Nature",
                "description": "Springer journal article format",
                "document_class": "sn-jnl",
                "features": ["Journal style", "Mathematical typesetting", "Algorithm support"]
            }
        }
    }


@router.post("/validate")
async def validate_latex(latex_content: str = Body(..., embed=True)):
    """
    Validate LaTeX content for common issues
    
    Args:
        latex_content: LaTeX code to validate
    
    Returns:
        Dict: Validation results with warnings and errors
    """
    try:
        generator = LatexGenerator(LatexTemplate.IEEE)  # Template doesn't matter for validation
        warnings = generator.validate_latex(latex_content)
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "suggestion": "Review warnings and fix any critical issues before compilation"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "warnings": [f"Validation error: {str(e)}"],
            "suggestion": "Check LaTeX syntax and structure"
        }