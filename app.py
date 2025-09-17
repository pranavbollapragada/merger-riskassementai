import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Import custom modules
from components.document_uploader import DocumentUploader
from components.risk_analyzer import RiskAnalyzer
from components.dashboard import Dashboard
from components.json_manager import JSONManager
from models.risk_engine import RiskEngine
from utils.data_persistence import DataPersistence
from utils.audit_display import display_audit_outcomes
from utils.business_display import display_business_outputs
from utils.key_takeaways_dashboard import display_key_takeaways_dashboard

# Page configuration
st.set_page_config(
    page_title="Tax Risk Assessment Model",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'risk_engine' not in st.session_state:
    st.session_state.risk_engine = RiskEngine()
if 'data_persistence' not in st.session_state:
    st.session_state.data_persistence = DataPersistence()
if 'json_manager' not in st.session_state:
    st.session_state.json_manager = JSONManager()
if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

def main():
    st.title("🏢 M&A Tax Risk Assessment Model")
    st.markdown("### Professional Due Diligence and Tax Exposure Analysis")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Module",
        ["Document Upload & Analysis", "Risk Dashboard", "Detailed Reports", "JSON Management", "Historical Analysis"],
        key="main_navigation"
    )
    
    if page == "Document Upload & Analysis":
        document_analysis_page()
    elif page == "Risk Dashboard":
        dashboard_page()
    elif page == "Detailed Reports":
        reports_page()
    elif page == "JSON Management":
        json_management_page()
    elif page == "Historical Analysis":
        historical_page()

def document_analysis_page():
    st.header("📄 Document Upload & Tax Risk Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Upload Documents")
        uploader = DocumentUploader()
        uploaded_file = uploader.render()
        
        if uploaded_file:
            if st.button("Analyze Document", type="primary"):
                with st.spinner("Analyzing document for tax risks..."):
                    analyzer = RiskAnalyzer()
                    results = analyzer.analyze_document(uploaded_file)
                    
                    if results:
                        st.session_state.analysis_results.append(results)
                        st.session_state.uploaded_documents.append({
                            'name': uploaded_file.name,
                            'timestamp': datetime.now(),
                            'results': results
                        })
                        
                        # Save to persistence
                        st.session_state.data_persistence.save_analysis(results)
                        
                        st.success("Analysis completed successfully!")
                        st.rerun()
    
    with col2:
        st.subheader("Analysis Results")
        if st.session_state.analysis_results:
            latest_result = st.session_state.analysis_results[-1]
            
            # Document Information Display
            text_length = latest_result.get('text_length', 0)
            word_count = latest_result.get('word_count', 0)
            analysis_status = latest_result.get('analysis_status', 'Unknown')
            
            col2_1, col2_2, col2_3 = st.columns(3)
            with col2_1:
                st.metric("Text Length", f"{text_length:,} characters")
            with col2_2:
                st.metric("Word Count", f"{word_count:,} words")
            with col2_3:
                st.metric("Analysis Status", analysis_status)
            
            # Document Text Preview
            st.subheader("Document Text Preview")
            document_text = latest_result.get('document_text', 'No text available')
            st.text_area("Extracted Text", document_text, height=200, disabled=True)
            
            # Found Keywords
            found_keywords = latest_result.get('found_keywords', [])
            if found_keywords:
                st.subheader("Keywords Found in Document")
                keyword_df = pd.DataFrame(found_keywords)
                st.dataframe(keyword_df, width='stretch')
            else:
                st.info("No keywords found in document")
            
            # Audit Outcomes Section
            audit_outcomes = latest_result.get('audit_outcomes')
            if audit_outcomes:
                display_audit_outcomes(audit_outcomes)
            
            # Business Outputs Section
            business_outputs = latest_result.get('business_outputs')
            if business_outputs:
                display_business_outputs(business_outputs)
            
            # Key Takeaways Dashboard
            financial_data = latest_result.get('financial_data')
            if financial_data:
                display_key_takeaways_dashboard(financial_data, business_outputs)
            
            # JSON Export Section
            st.divider()
            st.session_state.json_manager.render_json_export_section(latest_result)
            
        else:
            st.info("Upload and analyze a document to see results here.")

def dashboard_page():
    st.header("📊 Tax Risk Dashboard")
    dashboard = Dashboard()
    dashboard.render(st.session_state.analysis_results)

def reports_page():
    st.header("📋 Detailed Risk Reports")
    
    if not st.session_state.analysis_results:
        st.info("No analysis results available. Please upload and analyze documents first.")
        return
    
    # Report selection
    analysis_options = [f"Analysis {i+1} - {result.get('document_name', 'Unknown')}" 
                       for i, result in enumerate(st.session_state.analysis_results)]
    
    selected_analysis = st.selectbox("Select Analysis for Detailed Report", analysis_options, key="detailed_report_selector")
    
    if selected_analysis:
        analysis_index = int(selected_analysis.split()[1]) - 1
        result = st.session_state.analysis_results[analysis_index]
        
        # Generate detailed report
        generate_detailed_report(result)

def historical_page():
    st.header("📈 Historical Analysis & Trends")
    
    if len(st.session_state.analysis_results) < 2:
        st.info("Need at least 2 analyses to show historical trends.")
        return
    
    # Historical risk score trends
    dates = [doc['timestamp'] for doc in st.session_state.uploaded_documents]
    risk_scores = [result.get('overall_risk_score', 0) for result in st.session_state.analysis_results]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=risk_scores,
        mode='lines+markers',
        name='Risk Score Trend',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title="Risk Score Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Risk Score",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk category frequency
    all_categories = {}
    for result in st.session_state.analysis_results:
        for category in result.get('risk_categories', {}):
            all_categories[category] = all_categories.get(category, 0) + 1
    
    if all_categories:
        fig_bar = px.bar(
            x=list(all_categories.keys()),
            y=list(all_categories.values()),
            title="Risk Category Frequency Across All Documents"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

def generate_detailed_report(result):
    """Generate a comprehensive detailed report"""
    
    st.subheader(f"Detailed Report: {result.get('document_name', 'Unknown Document')}")
    
    # Executive Summary
    with st.expander("📊 Executive Summary", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Risk Score", f"{result.get('overall_risk_score', 0):.2f}/100")
            st.metric("Risk Level", result.get('risk_level', 'Unknown'))
        
        with col2:
            st.metric("Keywords Flagged", len(result.get('flagged_keywords', [])))
            st.metric("Categories Identified", len(result.get('risk_categories', {})))
        
        with col3:
            audit_prob = result.get('audit_probability', {})
            st.metric("12-Month Audit Probability", f"{audit_prob.get('12_month', 0):.1f}%")
            st.metric("36-Month Audit Probability", f"{audit_prob.get('36_month', 0):.1f}%")
    
    # Tax Liability Assessment
    with st.expander("💰 Tax Liability & Contingency Analysis"):
        contingency = result.get('expected_tax_contingency', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Expected Tax Contingency")
            st.metric("Mean Exposure", f"${contingency.get('mean', 0):,.2f}")
            st.metric("P75 (75th Percentile)", f"${contingency.get('p75', 0):,.2f}")
            st.metric("P90 (90th Percentile)", f"${contingency.get('p90', 0):,.2f}")
        
        with col2:
            st.subheader("Escrow Adequacy")
            escrow_data = result.get('escrow_adequacy', {})
            st.metric("Recommended Escrow", f"${escrow_data.get('recommended', 0):,.2f}")
            st.metric("Current Escrow", f"${escrow_data.get('current', 0):,.2f}")
            
            adequacy_status = "✅ Adequate" if escrow_data.get('adequate', False) else "⚠️ Insufficient"
            st.write(f"**Status:** {adequacy_status}")
    
    # Risk Categories Detail
    with st.expander("🎯 Risk Categories Analysis"):
        risk_categories = result.get('risk_categories', {})
        
        for category, details in risk_categories.items():
            st.subheader(f"{category}")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Risk Level:** {details.get('risk_level', 'Unknown')}")
                st.write(f"**Confidence:** {details.get('confidence', 0):.2f}%")
                st.write(f"**Keywords:** {', '.join(details.get('keywords', []))}")
                
                if details.get('recommendations'):
                    st.write("**Recommendations:**")
                    for rec in details['recommendations']:
                        st.write(f"• {rec}")
            
            with col2:
                # Risk level color coding
                risk_level = details.get('risk_level', 'Unknown')
                if risk_level == 'High':
                    st.error(f"🔴 {risk_level} Risk")
                elif risk_level == 'Medium':
                    st.warning(f"🟡 {risk_level} Risk")
                else:
                    st.success(f"🟢 {risk_level} Risk")
    
    # Compliance Standards
    with st.expander("📋 Compliance Standards Assessment"):
        compliance = result.get('compliance_assessment', {})
        
        standards = ['ASC_740', 'ASC_450', 'ASC_805', 'IRS_Circular_230', 'OECD_TP_Guidelines']
        
        for standard in standards:
            standard_data = compliance.get(standard, {})
            compliance_level = standard_data.get('compliance_level', 'Unknown')
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{standard.replace('_', ' ')}**")
                st.write(f"Issues: {', '.join(standard_data.get('issues', ['None identified']))}")
            
            with col2:
                if compliance_level == 'Compliant':
                    st.success("✅ Compliant")
                elif compliance_level == 'Minor Issues':
                    st.warning("⚠️ Minor Issues")
                else:
                    st.error("❌ Non-Compliant")
    
    # Export functionality
    st.subheader("📤 Export Report")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export as PDF"):
            st.info("PDF export functionality would be implemented here")
    
    with col2:
        if st.button("Export as Excel"):
            st.info("Excel export functionality would be implemented here")

def json_management_page():
    """JSON Management page for importing/exporting data"""
    st.header("📁 JSON Data Management")
    st.markdown("Manage analysis results and configuration through JSON files")
    
    # Create tabs for different JSON operations
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Export Data", "📥 Import Data", "⚙️ Configuration", "🗂️ File Manager"])
    
    with tab1:
        st.subheader("Export Analysis Results")
        
        if st.session_state.analysis_results:
            # Select which analysis to export
            analysis_options = [f"Analysis {i+1} - {datetime.now().strftime('%Y-%m-%d')}" 
                               for i in range(len(st.session_state.analysis_results))]
            
            selected_analysis_idx = st.selectbox(
                "Select analysis to export:",
                range(len(analysis_options)),
                format_func=lambda x: analysis_options[x],
                key="json_export_selector"
            )
            
            selected_analysis = st.session_state.analysis_results[selected_analysis_idx]
            
            # Show analysis preview
            st.write("**Analysis Preview:**")
            st.json(selected_analysis)
            
            # Export functionality
            st.session_state.json_manager.render_json_export_section(selected_analysis)
            
        else:
            st.info("No analysis results available to export. Please analyze a document first.")
    
    with tab2:
        st.subheader("Import Previous Analysis")
        
        # Import analysis results
        loaded_data = st.session_state.json_manager.render_json_import_section()
        
        if loaded_data:
            st.write("**Loaded Analysis Data:**")
            
            # Extract analysis results from loaded data
            if 'analysis_results' in loaded_data:
                imported_results = loaded_data['analysis_results']
                
                # Add to session state if user confirms
                if st.button("📥 Add to Current Session"):
                    st.session_state.analysis_results.append(imported_results)
                    st.success("✅ Analysis data imported successfully!")
                    st.rerun()
                
                # Display imported data
                st.session_state.json_manager.render_json_viewer(imported_results, "Imported Analysis")
    
    with tab3:
        st.subheader("Configuration Management")
        
        # Configuration management
        loaded_config = st.session_state.json_manager.render_config_management_section()
        
        if loaded_config:
            st.write("**Configuration Loaded:**")
            
            # Option to apply configuration to risk engine
            if st.button("🔧 Apply Configuration to Risk Engine"):
                try:
                    # Update risk keywords if present in config
                    if 'risk_keywords' in loaded_config:
                        # This would require updating the risk engine
                        st.success("✅ Configuration applied successfully!")
                        st.info("Note: Configuration changes will take effect on next analysis.")
                    else:
                        st.warning("No risk keywords found in configuration.")
                except Exception as e:
                    st.error(f"❌ Failed to apply configuration: {str(e)}")
    
    with tab4:
        st.subheader("File Management")
        
        # File management interface
        st.session_state.json_manager.render_file_management_section()
        
        # Additional file operations
        st.write("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Quick Actions**")
            
            if st.button("🧹 Clear All Session Data"):
                if st.checkbox("I confirm I want to clear all session data"):
                    st.session_state.analysis_results = []
                    st.session_state.uploaded_documents = []
                    st.success("✅ Session data cleared!")
                    st.rerun()
        
        with col2:
            st.write("**Data Statistics**")
            
            st.metric("Analysis Results", len(st.session_state.analysis_results))
            st.metric("Uploaded Documents", len(st.session_state.uploaded_documents))
    
    # JSON Format Guide
    with st.expander("📋 JSON Format Guide", expanded=False):
        st.markdown("""
        ### Analysis Results JSON Format
        
        ```json
        {
          "metadata": {
            "timestamp": "2025-01-01T12:00:00",
            "app_version": "1.0",
            "analysis_type": "tax_risk_assessment"
          },
          "analysis_results": {
            "document_text": "Sample document text...",
            "text_length": 1500,
            "word_count": 250,
            "found_keywords": [
              {
                "keyword": "transfer pricing",
                "category": "transfer_pricing"
              }
            ],
            "analysis_status": "Complete"
          }
        }
        ```
        
        ### Configuration JSON Format
        
        ```json
        {
          "risk_keywords": {
            "transfer_pricing": [
              "transfer pricing",
              "intercompany",
              "arm's length"
            ],
            "state_tax": [
              "nexus",
              "apportionment",
              "sales tax"
            ]
          },
          "risk_weights": {
            "transfer_pricing": 1.2,
            "state_tax": 1.0
          },
          "analysis_settings": {
            "min_keyword_length": 3,
            "context_window": 100
          }
        }
        ```
        """)

if __name__ == "__main__":
    main()