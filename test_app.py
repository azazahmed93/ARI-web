import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import nltk
import time
import os
import random

# Set page config
st.set_page_config(
    page_title="ARI Analyzer Diagnostics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("ARI Analyzer Diagnostic Tool")
st.write("This tool helps diagnose issues with the main application.")

# Download necessary NLTK data if not already downloaded
@st.cache_resource
def download_nltk_data():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('vader_lexicon')
    nltk.download('wordnet')
    return "NLTK data downloaded successfully"

status = download_nltk_data()
st.write(f"NLTK Status: {status}")

# Check for API key
openai_key = os.environ.get("OPENAI_API_KEY")
if openai_key:
    st.write("✓ OpenAI API Key is set")
else:
    st.write("❌ OpenAI API Key is not set")

# Test module imports
st.write("### Module Import Test")

modules_status = {}

# Test asset modules
try:
    from assets.content import METRICS
    modules_status["assets.content"] = "✓ Imported successfully"
except Exception as e:
    modules_status["assets.content"] = f"❌ Import failed: {str(e)}"

try:
    from assets.styles import apply_styles
    modules_status["assets.styles"] = "✓ Imported successfully"
except Exception as e:
    modules_status["assets.styles"] = f"❌ Import failed: {str(e)}"

# Test utility modules
try:
    from utils import strip_html
    modules_status["utils"] = "✓ Imported successfully"
except Exception as e:
    modules_status["utils"] = f"❌ Import failed: {str(e)}"

try:
    from database import benchmark_db
    modules_status["database"] = "✓ Imported successfully"
except Exception as e:
    modules_status["database"] = f"❌ Import failed: {str(e)}"

try:
    from analysis import analyze_campaign_brief
    modules_status["analysis"] = "✓ Imported successfully"
except Exception as e:
    modules_status["analysis"] = f"❌ Import failed: {str(e)}"

try:
    from ai_insights import generate_deep_insights
    modules_status["ai_insights"] = "✓ Imported successfully"
except Exception as e:
    modules_status["ai_insights"] = f"❌ Import failed: {str(e)}"

# Display module status
for module, status in modules_status.items():
    st.write(f"**{module}**: {status}")

# Display a sample METRICS value
st.write("### Sample METRICS data")
if "assets.content" in modules_status and "✓" in modules_status["assets.content"]:
    st.write(METRICS["Representation"])

# Run a sample benchmark query
st.write("### Sample Database Query")
if "database" in modules_status and "✓" in modules_status["database"]:
    try:
        benchmark_result = benchmark_db.get_vertical_benchmarks("Technology", "Software")
        st.write(benchmark_result)
    except Exception as e:
        st.write(f"Error querying benchmark database: {str(e)}")

# Provide troubleshooting steps
st.write("### Troubleshooting Recommendations")
st.write("""
1. Check for any missing modules or packages
2. Ensure all required NLTK data is downloaded
3. Verify the OpenAI API key is set
4. Look for any error messages in the console logs
5. Check for syntax errors in recently modified files
""")

# Add a test button to simulate a brief analysis
if st.button("Test Brief Analysis"):
    with st.spinner("Analyzing sample brief..."):
        try:
            # Simple sample brief
            sample_brief = """
            This is a sample marketing brief for a technology company launching a new software product.
            The target audience is young professionals aged 25-35 who are tech-savvy and interested in productivity tools.
            """
            
            # Test analysis module with a simple input
            from analysis import extract_brand_info
            brand_info = extract_brand_info(sample_brief)
            st.write("Brand info extraction successful:", brand_info)
            
            time.sleep(2)  # Simulate processing time
            
            # Display success message
            st.success("Sample analysis completed successfully")
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")