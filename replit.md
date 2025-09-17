# Tax Risk Assessment Model

## Overview

This is a comprehensive M&A Tax Risk Assessment Model built with Streamlit that analyzes uploaded documents (purchase agreements, memorandums, tax returns) for tax exposure risks. The system uses natural language processing to identify risk keywords, calculate risk scores, assess audit probabilities, and provide quantitative analysis of potential tax contingencies. It's designed for professional due diligence workflows in mergers and acquisitions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Application**: Multi-page interface with modular components for document upload, risk analysis, dashboard visualization, and reporting
- **Component-Based Design**: Separate modules for DocumentUploader, RiskAnalyzer, and Dashboard to maintain clean separation of concerns
- **Interactive Visualizations**: Plotly integration for risk charts, heatmaps, and statistical distributions

### Backend Architecture
- **Risk Engine Core**: Central RiskEngine class that processes text and calculates comprehensive risk scores using weighted keyword analysis
- **Text Processing Pipeline**: NLTK-based TextProcessor for document preprocessing, tokenization, and feature extraction
- **PDF Processing**: PyPDF2-based extraction system for handling uploaded documents with metadata preservation
- **Modular Risk Assessment**: Keyword-based analysis using predefined risk categories (Transfer Pricing, State Tax, International Tax, etc.)

### Data Storage Solutions
- **SQLite Database**: Local persistence for documents, analysis results, and audit trails
- **Session State Management**: Streamlit session state for temporary data and user interactions
- **File System Storage**: Document content and extracted text storage with metadata tracking

### Risk Assessment Framework
- **Multi-Category Analysis**: Evaluates Transfer Pricing, State Tax, International Tax, and other risk categories with weighted scoring
- **Compliance Standards Integration**: Built-in assessment against ASC 740, ASC 450, and other tax accounting standards
- **Quantitative Modeling**: Statistical analysis including audit probability calculations and expected tax contingency distributions
- **Escalation Logic**: Automated flagging system for high-risk findings requiring partner review

### Authentication and Authorization
- **No Authentication**: Currently designed as a single-user application without user management or access controls

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis
- **NumPy/SciPy**: Statistical calculations and risk modeling
- **Plotly**: Interactive data visualization and charting
- **NLTK**: Natural language processing for text analysis
- **PyPDF2**: PDF document parsing and text extraction

### Database
- **SQLite**: Embedded database for local data persistence (no external database server required)

### Third-Party Services
- **None Currently**: The application operates as a standalone system without external API integrations

### Development Dependencies
- Standard Python scientific stack (pandas, numpy, scipy)
- Text processing libraries (nltk, re)
- File handling utilities for document processing

The system is designed to be self-contained with minimal external dependencies, making it suitable for deployment in secure environments where external API access may be restricted.