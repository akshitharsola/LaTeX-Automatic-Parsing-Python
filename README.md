# LaTeX Automatic Parsing (Python)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.1.0-blue.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue.svg)](https://typescriptlang.org)

Advanced document processing system that converts DOCX files to LaTeX format using native Python processing and modern web technologies.

## 🎯 Project Overview

This project aims to provide a robust solution for converting Microsoft Word documents (.docx) to LaTeX format, specifically targeting academic paper templates (IEEE, ACM, Springer). Unlike traditional approaches that rely on HTML conversion, this system processes DOCX files natively using Python libraries.

## 👥 Contributors

- **[Akshit Harsola](https://github.com/akshitharsola)** - Project Lead & Developer
- **Claude (Anthropic)** - Development Assistant & Code Implementation

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance async API
- **Document Processing**: docx2python for native DOCX structure access
- **Data Validation**: Pydantic models with type safety
- **Templates**: IEEE, ACM, and Springer LaTeX templates

### Frontend (React + TypeScript)
- **Framework**: React with TypeScript for type safety
- **Styling**: Modern CSS with responsive design
- **File Upload**: Drag-and-drop interface with progress tracking
- **Real-time Processing**: Live feedback during document analysis

## ✅ Current Features

### 🔧 Core Infrastructure
- FastAPI backend with async processing
- React TypeScript frontend
- File upload validation (DOCX only, 50MB limit)
- Real-time progress tracking
- Error handling and user feedback

### 👤 Advanced Author Processing
- **Semicolon-separated author format support**
- **Department abbreviation expansion** (cse → Computer Science)
- **Corresponding author marking**
- **Template-specific formatting**:
  - **IEEE**: `\IEEEauthorblockN` and `\IEEEauthorblockA` with ordinal numbering
  - **ACM**: `\affiliation{}`, `\institution{}`, `\city{}`, `\country{}` structure
  - **Springer**: `\fnm{}`, `\sur{}`, `\email{}` with corresponding author support

### 🎨 LaTeX Template System
- IEEE Conference template
- ACM Conference template
- Springer Nature template
- Template-specific document classes and packages
- Basic bibliography templates

## 🚧 Known Limitations

**⚠️ Important**: This project is currently **~30% complete**. The following major features are **NOT yet implemented**:

- Document content extraction and processing
- Abstract and keywords processing
- Section content analysis
- Table detection and conversion
- List processing with Word styles
- Equation extraction (OMML to LaTeX)
- Dynamic bibliography generation
- Image extraction and processing

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## 📊 Template Examples

### Input Format (Author Information)
```
Name: akshit harsola ; Athak Shrivastava ; ankita chourasia
Department: cse ; it ; cse
University: medicaps university, indore, madhya pradesh
Mail: harsolaakshit@gmail.com* ; athakshrivatva@gmail.com ; anitachourasia@gmail.com
```

### IEEE Output
```latex
\IEEEauthorblockN{1\textsuperscript{st} Akshit Harsola}
\IEEEauthorblockA{\textit{Department of Computer Science} \\
\textit{Medicaps University} \\
Indore, Madhya Pradesh \\
harsolaakshit@gmail.com}
\and
\IEEEauthorblockN{2\textsuperscript{nd} Ankita Chourasia}
\IEEEauthorblockA{\textit{Department of Computer Science} \\
\textit{Medicaps University} \\
Indore, Madhya Pradesh \\
ankitachourasia@gmail.com}
```

### ACM Output
```latex
\author{Akshit Harsola}
\email{harsolaakshit@gmail.com}
\affiliation{%
  \institution{Department of Computer Science and Engineering}
  \city{Medicaps University}
  \country{Indore}
}
```

## 🔧 API Endpoints

### Health Check
```bash
GET /api/health
```

### Available Templates
```bash
GET /api/latex/templates
```

### Generate LaTeX
```bash
POST /api/latex/generate
Content-Type: application/json

{
  "analysis": { /* DocumentAnalysis object */ },
  "template": "ieee" | "acm" | "springer"
}
```

## 📁 Project Structure

```
docx-analyzer-python/
├── backend/                 # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── models/         # Pydantic data models
│   │   │   └── document.py # Document structure models
│   │   ├── routers/        # API route handlers
│   │   │   ├── document.py # Document processing routes
│   │   │   └── latex.py    # LaTeX generation routes
│   │   └── services/       # Business logic
│   │       ├── document_processor.py
│   │       └── latex_generator.py
│   ├── requirements.txt    # Python dependencies
│   └── test_api.py        # API tests
├── frontend/               # React TypeScript Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── AnalysisViewer.tsx
│   │   │   ├── DocumentUploader.tsx
│   │   │   └── LatexViewer.tsx
│   │   ├── types/          # TypeScript interfaces
│   │   │   └── document.ts
│   │   ├── utils/          # API utilities
│   │   │   └── api.ts
│   │   ├── App.tsx         # Main application
│   │   └── index.tsx       # Entry point
│   ├── package.json        # Node.js dependencies
│   └── public/             # Static assets
├── PROJECT_STATUS_SUMMARY.md # Detailed project status
└── README.md              # This file
```

## 🛠️ Development

### Adding New Templates
1. Update `LatexTemplate` enum in `backend/app/models/document.py`
2. Add template configuration in `LatexGenerator.__init__()`
3. Implement template-specific logic in `_generate_authors()` method
4. Add template info to `/api/latex/templates` endpoint

### Testing
```bash
# Backend tests
cd backend
python test_api.py

# Frontend tests
cd frontend
npm test
```

## 🔍 Current Status

**Project Completion**: ~30%

**Working Features**:
- Basic LaTeX template generation
- Enhanced author formatting for all templates
- File upload and validation
- Template selection and configuration

**Missing Features**:
- Document content processing
- Element extraction (tables, lists, equations)
- Dynamic bibliography generation
- Comprehensive document analysis

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI team for the excellent async web framework
- React team for the modern UI library
- docx2python developers for native DOCX processing
- Academic community for LaTeX template standards

## 📞 Contact

**Akshit Harsola**
- Email: harsolaakshit@gmail.com
- GitHub: [@akshitharsola](https://github.com/akshitharsola)

---

**Note**: This project is under active development. The current version provides a foundation for DOCX-to-LaTeX conversion with significant room for feature completion and improvement.