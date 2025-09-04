import streamlit as st
from clausewise.analyzer import extract_text, analyze_document
import json
import transformers
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ClauseWise - AI Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_logo():
    """Create a text-based logo for ClauseWise using standard Streamlit elements."""
    st.title("ClauseWise")
    st.subheader("AI-Powered Legal Document Analysis")
    st.write("---")

def show_navigation():
    """Show navigation buttons."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "home"
    
    with col2:
        if st.button("Analysis", key="nav_analysis", use_container_width=True):
            st.session_state.current_page = "analysis"
    
    with col3:
        if st.button("Results", key="nav_results", use_container_width=True):
            st.session_state.current_page = "results"
    
    with col4:
        if st.button("About", key="nav_about", use_container_width=True):
            st.session_state.current_page = "about"
    
    st.write("---")

def show_home_page():
    """Display the home page with project overview."""
    st.header("Welcome to ClauseWise")
    
    st.write(
        "Transform complex legal documents into clear, understandable insights with our AI-powered analysis engine. "
        "Upload your legal documents and let ClauseWise extract, simplify, and classify every important detail."
    )
    
    st.subheader("Key Features")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("Clause Simplification")
            st.write("Automatically rewrites complex legal clauses into simplified, layman-friendly language.")
    
        with st.container(border=True):
            st.subheader("Named Entity Recognition")
            st.write("Identifies and extracts key legal entities such as parties, dates, obligations, and monetary values.")
    
        with st.container(border=True):
            st.subheader("Clause Extraction")
            st.write("Detects and segments individual clauses from lengthy legal documents for focused analysis.")
    
    with col2:
        with st.container(border=True):
            st.subheader("Document Classification")
            st.write("Accurately classifies legal documents into categories like NDA, lease, employment contract.")
    
        with st.container(border=True):
            st.subheader("Multi-Format Support")
            st.write("Processes PDF, DOCX, and TXT formats seamlessly.")
    
        with st.container(border=True):
            st.subheader("AI-Powered Analysis")
            st.write("Leverages advanced NLP for intelligent legal text processing.")
    
    st.subheader("Getting Started")
    st.info(
        "1. Upload your legal document (PDF, DOCX, or TXT)\n"
        "2. Analyze with our AI-powered ClauseWise engine\n"
        "3. Review simplified clauses, extracted entities, and classification\n"
        "4. Export results for further analysis"
    )
    
    st.button("Start Analysis Now", on_click=lambda: setattr(st.session_state, 'current_page', 'analysis'), type="primary")

def show_analysis_page():
    """Display the document analysis page."""
    st.header("Document Analysis")
    
    st.write("Upload a legal document to get started.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt"],
        help="Upload a legal document to analyze"
    )
    
    if uploaded_file:
        # Show file info
        st.subheader("File Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"File: {uploaded_file.name}")
        with col2:
            st.info(f"Size: {uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.info(f"Type: {uploaded_file.name.split('.')[-1].upper()}")
        
        # Analysis button
        if st.button("Analyze Document", use_container_width=True):
            with st.spinner("Analyzing document... This may take a moment."):
                try:
                    filetype = uploaded_file.name.split(".")[-1].lower()
                    text = extract_text(uploaded_file, filetype)
                    
                    if not text or text.startswith("PDF processing requires"):
                        st.error("Could not extract text from the document. Please ensure the file is not corrupted.")
                    else:
                        # Store text in session state
                        st.session_state.document_text = text
                        st.session_state.uploaded_file = uploaded_file
                        
                        # Run analysis
                        result = analyze_document(text)
                        st.session_state.analysis_result = result
                        
                        # Show success message
                        st.success("Document analysis completed successfully!")
                        
                        # Auto-navigate to results
                        st.session_state.current_page = "results"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")

def show_results_page():
    """Display the analysis results page."""
    if 'analysis_result' not in st.session_state:
        st.warning("No analysis results available. Please analyze a document first.")
        st.button("Go to Analysis", on_click=lambda: setattr(st.session_state, 'current_page', 'analysis'))
        return
    
    result = st.session_state.analysis_result
    
    st.header("Analysis Results")
    
    # Document summary
    st.subheader("Document Summary")
    st.info(result.get('summary', 'Analysis completed successfully.'))
    
    # Document classification
    st.subheader("Document Classification")
    st.write(f"**Type:** {result['classification']}")
    
    # Named entities
    st.subheader("Named Entities")
    
    for entity_type, entities in result['entities'].items():
        if entities:
            st.write(f"**{entity_type}:**")
            st.write("- " + "\n- ".join(entities))
    
    # Simplified clauses
    st.subheader("Simplified Clauses")
    
    for i, (orig, simp) in enumerate(zip(result['clauses'], result['simplified_clauses'])):
        with st.expander(f"Clause {i+1}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Original:**")
                st.write(orig)
            with col2:
                st.write("**Simplified:**")
                st.write(simp)
    
    # Export options
    show_export_options(result)

def show_export_options(results):
    """Show export options for the results."""
    st.subheader("Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON export
        json_str = json.dumps(results, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="clausewise_analysis.json",
            mime="application/json"
        )
    
    with col2:
        # CSV export for entities
        if results['entities']:
            entity_data = []
            for entity_type, entities in results['entities'].items():
                for entity in entities:
                    entity_data.append({'Type': entity_type, 'Entity': entity})
            
            if entity_data:
                df = pd.DataFrame(entity_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="clausewise_entities.csv",
                    mime="text/csv"
                )

def show_about_page():
    """Display the about page."""
    st.header("About ClauseWise")
    
    st.subheader("Project Overview")
    st.write(
        "ClauseWise is an AI-powered legal document analyzer designed to simplify, decode, and classify complex legal texts for lawyers, businesses, and laypersons alike. "
        "Navigating legal contracts typically requires intensive manual reading and interpretation, often demanding legal expertise to identify obligations, understand clauses, and determine the document type. ClauseWise addresses this challenge by automating the clause analysis workflow using cutting-edge natural language processing."
    )
    
    st.subheader("Key Features")
    st.markdown("""
    - Clause Simplification: Automatically rewrites complex legal clauses into simplified, layman-friendly language
    - Named Entity Recognition (NER): Identifies and extracts key legal entities such as parties, dates, obligations, monetary values, and legal terms
    - Clause Extraction and Breakdown: Detects and segments individual clauses from lengthy legal documents for focused analysis
    - Document Type Classification: Accurately classifies uploaded legal documents into categories like NDA, lease, employment contract, or service agreement
    - Multi-Format Document Support: Enables users to upload and process legal documents in PDF, DOCX, or TXT formats seamlessly
    - User-Friendly Interface: Provides an interactive frontend built with Streamlit
    """)
    
    st.subheader("Technology Stack")
    st.markdown("""
    - Python: Core programming language
    - spaCy: Natural language processing and named entity recognition
    - scikit-learn: Machine learning for document classification
    - NLTK: Natural language toolkit for text processing
    - Streamlit: Modern web application framework
    - PyPDF2 & python-docx: Document format support
    """)
    
    st.subheader("Supported Document Types")
    st.markdown("""
    - Non-Disclosure Agreements (NDA)
    - Employment Contracts
    - Lease Agreements
    - Service Agreements
    - Purchase Agreements
    - Partnership Agreements
    - License Agreements
    - Other legal documents
    """)
    
    st.subheader("Privacy and Security")
    st.write(
        "All document processing is done locally using advanced NLP techniques. No documents are stored permanently on our servers, and analysis results are only available during your session."
    )

def main():
    """Main application function."""
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    # Create logo and header
    create_logo()
    
    # Show navigation
    show_navigation()
    
    # Page routing
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "analysis":
        show_analysis_page()
    elif st.session_state.current_page == "results":
        show_results_page()
    elif st.session_state.current_page == "about":
        show_about_page()

if __name__ == "__main__":
    main()
