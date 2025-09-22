import streamlit as st
import pandas as pd

st.set_page_config(page_title="LLM PDF Summaries Viewer", layout="wide")

st.title("LLM PDF Summaries Viewer")

# Load CSV
def load_data():
    return pd.read_csv("file_inventory_with_llm_summaries.csv")

df = load_data()

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    filenames = df["filename"].unique()
    selected_file = st.selectbox("Select a file", ["All"] + list(filenames))
    business_types = df["business_type"].fillna("other").unique()
    selected_type = st.selectbox("Business type", ["All"] + list(business_types))
    min_page = int(df["page_number"].min())
    max_page = int(df["page_number"].max())
    if min_page == max_page:
        page_range = (min_page, max_page)
        st.write(f"Only page {min_page} available.")
    else:
        page_range = st.slider("Page number", min_page, max_page, (min_page, max_page))

# Filter data
filtered = df.copy()
if selected_file != "All":
    filtered = filtered[filtered["filename"] == selected_file]
if selected_type != "All":
    filtered = filtered[filtered["business_type"] == selected_type]
filtered = filtered[(filtered["page_number"] >= page_range[0]) & (filtered["page_number"] <= page_range[1])]

# Show table
st.dataframe(filtered, use_container_width=True)

# Show details for selected row
st.markdown("---")
st.header("Page Details")
row = st.selectbox("Select a row to view details", filtered.index, format_func=lambda i: f"{filtered.loc[i, 'filename']} - Page {filtered.loc[i, 'page_number']}")
if row is not None:
    details = filtered.loc[row]
    st.subheader(f"{details['filename']} - Page {details['page_number']}")
    st.markdown(f"**Business Type:** {details['business_type']}")
    st.markdown(f"**Exceptions:** {details['exceptions']}")
    st.markdown("**LLM Summary:**")
    st.write(details['llm_summary'])
    st.markdown("**Extracted Text:**")
    st.code(details['page_text'], language='text')
    st.markdown("**Markdown (if available):**")
    st.code(details['page_text_md'], language='markdown')
    st.markdown("---")
    st.header("Rendered Markdown Preview")
    st.markdown(details['page_text_md'] or "_No Markdown available for this page._", unsafe_allow_html=True)
