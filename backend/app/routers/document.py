"""
Document processing router
Handles file upload and document analysis using docx2python
"""

import time
import tempfile
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

from app.models.document import DocumentAnalysis, ProcessingConfig
from app.services.document_processor import DocumentProcessor

router = APIRouter()

@router.post("/upload", response_model=DocumentAnalysis)
async def upload_document(
    file: UploadFile = File(...),
    config: Optional[str] = Form(None)
):
    """
    Upload and analyze a DOCX document
    
    Args:
        file: DOCX file to process
        config: JSON string of ProcessingConfig (optional)
    
    Returns:
        DocumentAnalysis: Complete analysis of the document
    """
    start_time = time.time()
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.docx'):
        raise HTTPException(
            status_code=400,
            detail="Only DOCX files are supported"
        )
    
    # Parse configuration
    processing_config = ProcessingConfig()
    if config:
        try:
            import json
            config_dict = json.loads(config)
            processing_config = ProcessingConfig(**config_dict)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid configuration: {str(e)}"
            )
    
    # Create temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process document
        processor = DocumentProcessor(processing_config)
        analysis = await processor.analyze_document(
            file_path=tmp_file_path,
            filename=file.filename,
            file_size=len(content)
        )
        
        # Add processing time
        analysis.processing_time = time.time() - start_time
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@router.get("/analyze/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Retrieve a previous analysis by ID
    
    Args:
        analysis_id: Unique identifier for the analysis
    
    Returns:
        DocumentAnalysis: The requested analysis
    """
    # TODO: Implement analysis storage and retrieval
    raise HTTPException(
        status_code=501,
        detail="Analysis storage not yet implemented"
    )


@router.get("/health")
async def health_check():
    """Document processing service health check"""
    return {
        "status": "healthy",
        "service": "document-processor",
        "capabilities": [
            "DOCX file processing",
            "Native list detection",
            "OMML equation extraction",
            "Smart section analysis",
            "Table structure detection"
        ]
    }