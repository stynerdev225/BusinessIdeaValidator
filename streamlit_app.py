"""
Streamlit app for the business idea validator.
"""
import streamlit as st
import os
import json
import logging
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

from business_validator import validate_business_idea
from business_validator.config import DATA_DIR
from business_validator.analyzers.trend_analyzer import analyze_health_trends, generate_tech_business_ideas

# Set page configuration
st.set_page_config(
    page_title="Business Idea Validator",
    page_icon="💡",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: 700;
        color: #000000;
        margin-bottom: 0;
    }
    
    .subheader {
        font-size: 1.2em;
        color: #555;
        margin-top: 0;
        margin-bottom: 2em;
    }
    
    .styled-form {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Make the Streamlit app header sticky */
    header[data-testid="stHeader"] {
        background-color: white;
        position: sticky;
        top: 0px;
        z-index: 999;
    }
    
    /* Style the text area input - "Enter your business idea" */
    textarea[aria-label="Enter your business idea"],
    textarea[aria-label="Health topic to analyze"] {
        background-color: white !important;
        border: 1px solid #e6e6e6 !important;
        border-radius: 8px !important;
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* Add focus effect to textareas */
    textarea[aria-label="Enter your business idea"]:focus,
    textarea[aria-label="Health topic to analyze"]:focus {
        border-color: #555555 !important;
        box-shadow: 0 0 0 2px rgba(49, 51, 63, 0.2) !important;
    }
    
    /* Style number inputs */
    [data-testid="stNumberInput"] > div {
        background-color: white !important;
    }
    
    /* Style select boxes */
    [data-testid="stSelectbox"] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
    }
    
    /* Style multiselect dropdowns */
    [data-testid="stMultiSelect"] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
    }
    
    /* Style text inputs */
    .stTextInput > div > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
    }
    
    /* Enhance main search/input fields */
    textarea[aria-label="Enter your business idea"] {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 16px !important;
        color: #333333 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    textarea[aria-label="Enter your business idea"]:focus {
        border-color: #ff6347 !important;
        box-shadow: 0 0 0 3px rgba(255,99,71,0.2) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Style expander content in Advanced Options */
    [data-testid="stExpander"] {
        background-color: white !important;
        border-radius: 8px !important;
        border: 2px solid #e0e0e0 !important;
        margin-bottom: 15px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
    
    [data-testid="stExpander"] > div {
        background-color: white !important;
    }
    
    /* Style input containers and labels in the Advanced Options */
    [data-testid="stExpander"] .stMarkdown p {
        background-color: white !important;
    }
    
    [data-testid="stExpander"] .stNumberInput > div > div {
        background-color: white !important;
    }
    
    [data-testid="stExpander"] .stSelectbox > div > div {
        background-color: white !important;
    }
    
    [data-testid="stExpander"] .stMultiSelect > div > div {
        background-color: white !important;
    }
    
    [data-testid="stExpander"] .stTextInput > div > div {
        background-color: white !important;
    }
    
    [data-testid="stExpander"] label {
        background-color: white !important;
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* Add styling to columns inside expander for better separation */
    [data-testid="stExpander"] [data-testid="column"] {
        background-color: white !important;
        border-radius: 6px !important;
        padding: 8px !important;
        margin: 0 4px !important;
    }
    
    /* Make sure all Streamlit elements have white backgrounds in the expander */
    .stExpander {
        background-color: white !important;
    }
    
    .stExpander > * {
        background-color: white !important;
    }
    
    .stExpander div[data-baseweb="input"] {
        background-color: white !important;
    }
    
    .stExpander div[data-baseweb="select"] {
        background-color: white !important;
    }
    
    .stExpander div[data-baseweb="popover"] {
        background-color: white !important;
    }
    
    .stExpander div[data-baseweb="menu"] {
        background-color: white !important;
    }
    
    /* Style for multiselect chips/tags */
    div[data-baseweb="tag"] {
        background-color: #f0f0f0 !important;
        border: 1px solid #d0d0d0 !important;
    }
    
    /* Dropdown menu items */
    div[role="option"] {
        background-color: white !important;
    }
    
    .stExpander p {
        background-color: white !important;
    }
    
    /* Ensure specific input elements have white backgrounds */
    input[type="number"],
    input[type="text"],
    select {
        background-color: white !important;
    }
    
    /* Dropdown menu options */
    div[role="listbox"] {
        background-color: white !important;
    }
    
    /* Number input spinners */
    [data-testid="stNumberInput"] input {
        background-color: white !important;
    }
    
    /* Text input fields */
    [data-testid="stTextInput"] input {
        background-color: white !important;
    }
    
    /* Select box inputs */
    [data-testid="stSelectbox"] input {
        background-color: white !important;
    }
    
    /* MultiSelect inputs */
    [data-testid="stMultiSelect"] input {
        background-color: white !important;
    }
    
    /* Number input container and all its children */
    [data-testid="stNumberInput"] * {
        background-color: white !important;
    }
    
    /* Add more visible borders to number inputs */
    [data-testid="stNumberInput"] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 2px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    
    /* Add more visible borders to selectboxes */
    [data-testid="stSelectbox"] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 2px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    
    /* Improve focus state for selectboxes */
    [data-testid="stSelectbox"] > div:focus-within {
        border-color: #555555 !important;
        box-shadow: 0 0 0 2px rgba(49, 51, 63, 0.2) !important;
    }
    
    /* Add more visible borders to multiselect boxes */
    [data-testid="stMultiSelect"] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 2px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    
    /* Improve focus state for multiselect */
    [data-testid="stMultiSelect"] > div:focus-within {
        border-color: #555555 !important;
        box-shadow: 0 0 0 2px rgba(49, 51, 63, 0.2) !important;
    }
    
    /* Add more visible borders to text inputs */
    [data-testid="stTextInput"] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 2px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    /* Make sure all form-related elements have white backgrounds */
    form,
    div[data-testid="stForm"],
    div[data-baseweb="form-control"],
    div[data-baseweb="form-control-container"],
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"],
    div[data-testid="textArea"],
    textarea,
    select,
    input {
        background-color: white !important;
    }
    
    /* Ensure inputs have visible borders */
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] select,
    div[data-testid="stForm"] textarea {
        border: 1px solid #d0d0d0 !important;
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* Improve the Form container styling */
    div[data-testid="stForm"] {
        background-color: white !important;
        border: 1px solid #e6e6e6 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
    }
    
    /* Add focus styles to form inputs */
    div[data-testid="stForm"] input:focus,
    div[data-testid="stForm"] select:focus,
    div[data-testid="stForm"] textarea:focus {
        border-color: #555555 !important;
        box-shadow: 0 0 0 2px rgba(49, 51, 63, 0.2) !important;
    }
    
    /* Ensure all dropdown menus have white backgrounds and proper borders */
    div[data-baseweb="select"] div[data-baseweb="menu"] {
        background-color: white !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
    }
    
    /* Style dropdown menu options */
    div[data-baseweb="select"] div[data-baseweb="menu"] ul,
    div[role="listbox"],
    div[role="listbox"] ul,
    [data-baseweb="menu"],
    [data-baseweb="popover"],
    [data-baseweb="popover"] div {
        background-color: white !important;
    }
    
    div[data-baseweb="select"] div[data-baseweb="menu"] ul li,
    div[role="listbox"] ul li,
    div[role="option"],
    [data-baseweb="menu"] li {
        background-color: white !important;
        color: #000000 !important;
    }
    
    /* Style global selectbox elements */
    div[data-baseweb="select"] {
        background-color: white !important;
    }
    
    /* Make dropdown text in select boxes visible */
    div[data-baseweb="select"] [data-baseweb="value"],
    div[data-baseweb="select"] [data-baseweb="value"] span,
    div[data-baseweb="select"] span[title],
    [data-testid="stSelectbox"] span,
    [data-testid="stMultiSelect"] span {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    div[data-baseweb="select"] * {
        background-color: white !important;
    }
    
    /* Style selected option pills/chips in multiselect */
    div[data-baseweb="tag"] {
        background-color: #333333 !important;
        border: 1px solid #555555 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 4px !important;
        padding: 2px 8px !important;
        margin: 2px !important;
    }
    
    /* Style the delete/close button in multiselect pills */
    div[data-baseweb="tag"] button {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    div[data-baseweb="tag"] button:hover {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Style dropdown options for all selectboxes on hover */
    div[role="option"]:hover,
    [data-baseweb="menu"] li:hover {
        background-color: #e0e0e0 !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Style the active/selected option */
    div[aria-selected="true"],
    [data-baseweb="menu"] li[aria-selected="true"],
    [data-baseweb="popover"] li[aria-selected="true"] {
        background-color: #333333 !important;
        color: white !important;
        font-weight: 600 !important;
        border-left: 3px solid tomato !important;
        padding-left: 10px !important;
    }
    
    /* Make dropdown text options fully visible */
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] div,
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] div {
        color: #000000 !important;
        background-color: white !important;
        padding: 6px 10px !important;
    }
    
    /* Style for dropdown hover states */
    [data-baseweb="menu"] li:hover,
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] div:hover,
    [data-baseweb="popover"] div:hover {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
    }
    
    /* Ensure text is visible when selected in dropdowns */
    div[data-baseweb="select"] div[role="option"]:hover,
    div[data-baseweb="select"] div[aria-selected="true"] {
        color: #000000 !important;
        background-color: #e6e6e6 !important;
    }
    
    /* Style the Health Trends Analysis inputs */
    #main-tab2 [data-testid="stTextInput"] > div,
    #main-tab2 [data-testid="stMultiSelect"] > div,
    #main-tab3 [data-testid="stMultiSelect"] > div,
    #main-tab3 [data-testid="stSelectbox"] > div {
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 2px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    
    /* Limit width of health topic input field */
    [data-testid="stTextInput"] input[aria-label="Health topic to analyze"] {
        max-width: 400px !important;
        width: 100% !important;
    }
    
    /* Limit width of demographics multiselect */
    [data-testid="stMultiSelect"][aria-label="Demographics to analyze"] > div {
        max-width: 400px !important;
        width: 100% !important;
    }
    
    /* Limit width of regions expander */
    #main-tab2 [data-testid="stExpander"] {
        max-width: 800px !important;
    }
    
    /* Style specific input fields */
    [aria-label="Health topic to analyze"],
    [aria-label="Demographics to analyze"] div,
    [aria-label="Technology focus areas"] div,
    [aria-label="Target market size"] div,
    [aria-label="Time horizon"] div {
        background-color: white !important;
    }
    
    /* Make inputs in Tech Business tab consistent width */
    #main-tab3 [data-testid="stMultiSelect"] > div,
    #main-tab3 [data-testid="stSelectbox"] > div {
        max-width: 400px !important;
        width: 100% !important;
        background-color: white !important;
        border: 2px solid #d0d0d0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    
    /* Add focus effect to Tech Business tab inputs */
    #main-tab3 [data-testid="stMultiSelect"] > div:focus-within,
    #main-tab3 [data-testid="stSelectbox"] > div:focus-within {
        border-color: #555555 !important;
        box-shadow: 0 0 0 2px rgba(49, 51, 63, 0.2) !important;
    }
    
    /* Improve contrast in multiselect dropdowns */
    #main-tab3 [data-testid="stMultiSelect"] div[data-baseweb="tag"] {
        background-color: #333333 !important;
        color: white !important;
        font-weight: 500 !important;
        border: 1px solid #555555 !important;
    }
    
    /* Improve selection visibility in Tech Business tab */
    #main-tab3 div[data-baseweb="select"] div[role="option"],
    #main-tab3 div[data-baseweb="menu"] li {
        padding: 8px 12px !important;
    }
    
    #main-tab3 div[data-baseweb="select"] div[role="option"]:hover,
    #main-tab3 div[data-baseweb="menu"] li:hover {
        background-color: #e0e0e0 !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    #main-tab3 div[aria-selected="true"],
    #main-tab3 div[data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #555555 !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Make sure select boxes and multiselect have proper text color and background */
    [data-testid="stSelectbox"] div[role="option"],
    [data-testid="stMultiSelect"] div[role="option"] {
        background-color: white !important;
        color: #000000 !important;
        font-weight: 500 !important;
        padding: 6px 10px !important;
    }
    
        /* Improve contrast on hover for all dropdowns */
    [data-testid="stSelectbox"] div[role="option"]:hover,
    [data-testid="stMultiSelect"] div[role="option"]:hover,
    div[role="listbox"] div[role="option"]:hover {
        background-color: #f0f0f0 !important; 
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Improve visibility of selected items */
    [data-testid="stSelectbox"] div[aria-selected="true"],
    [data-testid="stMultiSelect"] div[aria-selected="true"],
    div[role="listbox"] div[aria-selected="true"] {
        background-color: #333333 !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Style dropdown options for all selects and multiselects */
    div[role="listbox"],
    div[data-baseweb="popover"],
    div[data-baseweb="menu"] {
        background-color: white !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    }
    
    /* Style the dropdown arrow for better visibility */
    div[data-baseweb="select"] svg,
    [data-testid="stSelectbox"] svg,
    [data-testid="stMultiSelect"] svg {
        fill: #333333 !important;
        opacity: 0.8 !important;
    }
    
    /* Style the expanded dropdown container */
    div[data-baseweb="popover"] div[role="listbox"],
    div[data-baseweb="menu"] div[role="listbox"] {
        background-color: white !important;
        max-height: 300px !important;
        overflow-y: auto !important;
        padding: 4px !important;
    }
    
    /* Make placeholder text more visible but slightly muted */
    div[data-baseweb="select"] [data-baseweb="placeholder"],
    [data-testid="stSelectbox"] [data-baseweb="placeholder"],
    [data-testid="stMultiSelect"] [data-baseweb="placeholder"] {
        color: #666666 !important;
        font-weight: 400 !important;
    }
    
    /* Change all buttons to black background with transparent underline by default */
    button[kind="primary"], 
    button[data-baseweb="button"],
    .stButton > button,
    [data-testid="StyledFullScreenButton"] > button,
    [data-testid="baseButton-secondary"],
    div.stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        background-color: black !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        border-bottom: 2px solid transparent !important; /* Transparent border by default */
        transition: all 0.3s ease !important;
    }
    
    /* Button hover state */
    button[kind="primary"]:hover, 
    button[data-baseweb="button"]:hover,
    .stButton > button:hover,
    [data-testid="StyledFullScreenButton"] > button:hover,
    [data-testid="baseButton-secondary"]:hover,
    div.stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #333333 !important;
        border-bottom: 2px solid #ff6347 !important; /* Show tomato underline on hover */
        transform: translateY(-1px) !important;
    }
    
    /* Button active/pressed state */
    button[kind="primary"]:active, 
    button[data-baseweb="button"]:active,
    .stButton > button:active,
    [data-testid="StyledFullScreenButton"] > button:active,
    [data-testid="baseButton-secondary"]:active,
    div.stDownloadButton > button:active,
    [data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(1px) !important;
        border-bottom: 2px solid tomato !important; /* Show tomato underline when active */
    }
    
    /* Custom width for specific buttons */
    .stButton button[kind="secondary"] {
        width: auto !important;
        min-width: 120px !important;
        max-width: 180px !important;
    }
    
/* Specific styling for the market report button */
    button[key="market_report_button"],
    [data-testid="baseButton-secondary"][kind="secondary"] {
        width: auto !important;
        min-width: 180px !important;
        max-width: 200px !important;
        padding: 8px 16px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Style all tabs (both main navigation and result tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: black !important;
        border-radius: 4px 4px 0px 0px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        color: white !important;
        border-bottom: 2px solid transparent !important; /* Transparent border for inactive tabs */
    }
    
    .stTabs [aria-selected="true"] {
        background-color: black !important;
        color: white !important;
        border-bottom: 2px solid tomato !important; /* Tomato border only for active tab */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Style checkboxes and radio buttons */
    [data-testid="stCheckbox"] div[role="checkbox"],
    [data-testid="stRadio"] div[role="radio"] {
        background-color: white !important;
        border-color: #666666 !important;
    }
    
    /* Style checkbox and radio labels */
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label {
        color: #333333 !important;
        font-weight: 500 !important;
    }
    
    /* Style checkbox when checked */
    [data-testid="stCheckbox"] div[data-baseweb="checkbox"][aria-checked="true"] div {
        background-color: #333333 !important;
        border-color: #333333 !important;
    }
    
    /* Style the sidebar with white background and border */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 2px solid #d0d0d0 !important;
    }
    
    /* Style the sidebar scrollbar - Using a more specific selector for higher priority */
    [data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 14px !important; /* Make scrollbar wider for better visibility */
        height: 14px !important;
    }
    
    [data-testid="stSidebar"] ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 12px !important; /* More rounded track */
        margin: 4px 0 !important; /* Add some margin for a pill-like appearance */
        box-shadow: inset 0 0 5px rgba(0,0,0,0.1) !important; /* Inner shadow for depth */
    }
    
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background-color: #000000 !important; /* Black color for the main part */
        border-radius: 30px !important; /* Very rounded ends for a pill-like appearance */
        border: 2px solid #f1f1f1 !important; /* Light border for contrast */
        min-height: 50px !important; /* Increased minimum height for thumb */
        /* Add larger tomato-colored rounded ends */
        background-image: linear-gradient(#000000, #000000), 
                          linear-gradient(#ff6347, #ff6347), 
                          linear-gradient(#ff6347, #ff6347) !important;
        background-position: center center, top center, bottom center !important;
        background-size: 100% calc(100% - 24px), 100% 12px, 100% 12px !important; /* Bigger tomato ends */
        background-repeat: no-repeat !important;
        box-shadow: 0 0 3px rgba(0,0,0,0.2) !important; /* Subtle shadow for depth */
    }
    
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
        background-color: #000000 !important; /* Keep it black on hover */
        opacity: 0.9 !important; /* Slightly less opaque on hover */
        /* Keep bigger tomato ends on hover */
        background-image: linear-gradient(#000000, #000000), 
                          linear-gradient(#ff6347, #ff6347), 
                          linear-gradient(#ff6347, #ff6347) !important;
        background-position: center center, top center, bottom center !important;
        background-size: 100% calc(100% - 24px), 100% 12px, 100% 12px !important; /* Bigger tomato ends */
        background-repeat: no-repeat !important;
    }
    
    /* Add a global scrollbar style to override Streamlit defaults */
    ::-webkit-scrollbar-thumb {
        background-color: #000000 !important;
        /* Add tomato-colored rounded ends to all scrollbars */
        background-image: linear-gradient(#000000, #000000), 
                          linear-gradient(#ff6347, #ff6347), 
                          linear-gradient(#ff6347, #ff6347) !important;
        background-position: center center, top center, bottom center !important;
        background-size: 100% calc(100% - 24px), 100% 12px, 100% 12px !important; /* Bigger tomato ends */
        background-repeat: no-repeat !important;
        border-radius: 30px !important; /* More circular ends */
        min-height: 50px !important; /* Taller scrollbar */
        border: 2px solid #f1f1f1 !important; /* Border for better contrast */
    }
    
    /* Style all sidebar elements to have white background */
    [data-testid="stSidebar"] > div {
        background-color: white !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stTitle,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        background-color: white !important;
        color: #333333 !important;
    }
    
    /* Ensure sidebar sliders and selectboxes have white background */
    [data-testid="stSidebar"] [data-testid="stSlider"] > div, 
    [data-testid="stSidebar"] [data-testid="stSlider"] > div > div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        background-color: white !important;
    }
    
    /* Ensure sidebar buttons have consistent styling */
    [data-testid="stSidebar"] button {
        background-color: white !important;
        color: #333333 !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 4px !important;
        border-bottom: 2px solid transparent !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
        border-bottom: 2px solid #ff6347 !important;
    }
    
    /* Style for custom sidebar heading class */
    .sidebar-heading {
        text-align: center !important;
        color: #333333 !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-top: 10px !important;
        margin-bottom: 20px !important;
        padding: 5px 0 !important;
        position: relative !important;
        width: 100% !important;
        background-color: lightcoral !important; /* Temporary for testing */
    }
    
    /* Add decorative line under the heading */
    .sidebar-heading:after {
        content: "" !important;
        display: block !important;
        width: 40px !important;
        height: 3px !important;
        background-color: #ff6347 !important; /* Tomato color line */
        margin: 8px auto 0 auto !important;
        border-radius: 2px !important;
    }
    
    /* Add padding to the main scrollable container to ensure content doesn't touch scrollbar */
    [data-testid="stSidebar"] [data-testid="ScrollableContainer"] {
        padding-right: 10px !important;
    }
    
    /* Style for Previous Validations section heading */
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] .stMarkdown h3 {
        text-align: center !important;
        margin-top: 15px !important;
        margin-bottom: 15px !important;
        color: #333333 !important;
        font-weight: 600 !important;
    }
    
    /* Style for the "no validations" message */
    .no-validations {
        text-align: center !important;
        color: #888888 !important;
        font-style: italic !important;
        margin: 10px auto !important;
        font-size: 0.9rem !important;
        padding: 10px !important;
    }
    
    /* Add some spacing after the divider for better visual separation */
    [data-testid="stSidebar"] hr {
        margin-top: 20px !important;
        margin-bottom: 20px !important;
        border: none !important; /* Remove default border */
        height: 3px !important; /* Make it thicker for testing */
        background-color: blue !important; /* Bright blue for testing */
        width: 100% !important; /* Ensure it spans the width */
        display: block !important; /* Ensure it's a block element */
    }
    
    /* Style for the entire sidebar container */
    [data-testid="stSidebar"] > div:first-child {
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
    
    /* Center the vertical block containing previous validation buttons */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        padding: 0 5px !important;
    }
    
    /* Style specifically for Previous Validations buttons */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] button {
        background-color: white !important;
        color: #333333 !important;
        text-align: center !important; /* Changed from left to center */
        width: 90% !important; /* Make slightly narrower for visual centering */
        margin: 0 auto 8px auto !important; /* Center horizontally with auto margins */
        display: block !important; /* For proper centering */
        border-radius: 6px !important; /* Slightly more rounded corners */
        padding: 10px 12px !important; /* Add more padding for better appearance */
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important; /* Subtle shadow */
        transition: all 0.2s ease !important; /* Smooth transition for hover effects */
        border: 1px solid #e0e0e0 !important; /* Lighter border */
        white-space: pre-line !important; /* Preserve line breaks */
        line-height: 1.3 !important; /* Improve line spacing */
        min-height: 60px !important; /* Ensure consistent height */
    }
    
    /* Style for the Business Idea Validator title */
    .idea-validator-title {
        color: #000000 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
        padding-bottom: 8px !important;
        position: relative !important;
        display: inline-block !important;
    }
    
    .idea-validator-title:after {
        content: "" !important;
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 60px !important;
        height: 3px !important;
        background-color: #ff6347 !important;
        border-radius: 2px !important;
    }
    
    /* Style for the Business Idea Validator description */
    .idea-validator-description {
        background-color: #f8f9fa !important;
        border-left: 4px solid #ff6347 !important;
        padding: 15px 20px !important;
        margin: 15px 0 25px 0 !important;
        border-radius: 0 8px 8px 0 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }
    
    .idea-validator-description p {
        color: #333333 !important;
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
        margin: 0 !important;
    }

    /* Style for the Sidebar Main Title */
    .sidebar-main-title {
        color: #000000 !important;
        font-size: 1.8rem !important; /* Slightly smaller than main content title */
        font-weight: 700 !important;
        margin-bottom: 8px !important;
        padding-bottom: 6px !important;
        position: relative !important;
        display: block !important; /* Block to take full width */
        text-align: center !important; /* Center the title */
    }

    .sidebar-main-title:after {
        content: "" !important;
        position: absolute !important;
        bottom: 0 !important;
        left: 50% !important;
        transform: translateX(-50%) !important; /* Center the underline */
        width: 50px !important; /* Adjust width as needed */
        height: 3px !important;
        background-color: #ff6347 !important;
        border-radius: 2px !important;
    }

    /* Style for the Sidebar Main Description */
    .sidebar-main-description {
        background-color: #f8f9fa !important;
        border-left: 4px solid #ff6347 !important;
        padding: 12px 15px !important; /* Slightly less padding */
        margin: 10px 0 20px 0 !important; /* Adjust margins */
        border-radius: 0 8px 8px 0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    .sidebar-main-description p {
        color: #555555 !important; /* Softer gray for better readability */
        font-size: 0.95rem !important;
        line-height: 1.5 !important; /* Increased line height */
        margin: 0 !important;
        text-align: left !important; /* Align text to left for readability */
    }

    /* Style the sidebar collapse icon */
    [data-testid="collapseSidebarButton"] {
        background-color: black !important;
        color: white !important;
    }
    
    [data-testid="collapseSidebarButton"] svg {
        color: white !important;
        fill: white !important;
    }

    /* Custom Horizontal Rule for Sidebar */
    .custom-hr-sidebar {
        height: 3px !important; /* Thicker */
        background-color: blue !important; /* Bright blue for testing */
        margin-top: 20px !important;
        margin-bottom: 20px !important;
        width: 100% !important; /* Ensure it spans the width */
        display: block !important; /* Ensure it is displayed as a block */
    }
</style>
""", unsafe_allow_html=True)

# App title and description with improved styling
st.title("💡 Business Idea Validator")
st.markdown(
    """
    Validate business ideas, analyze health trends, and discover tech business opportunities.
    """
)

# Create tabs for different main functionalities
main_tab1, main_tab2, main_tab3 = st.tabs([
    "Business Idea Validation", 
    "Health Trends Analysis", 
    "Tech Business Ideas"
])

with main_tab1:
    st.markdown("<h2 class='idea-validator-title'>🚀 Business Idea Validator</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="idea-validator-description">
            <p>Validate your business ideas by analyzing discussions on HackerNews and Reddit. 
            Our AI-powered tool provides data-driven insights to help you refine your concept and 
            identify market opportunities.</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Business idea validation content will go here
    
with main_tab2:
    st.markdown("<h2 class='idea-validator-title'>🔍 Health Trends Analysis</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="idea-validator-description">
            <p>Analyze trending health issues with demographic and regional breakdowns.
            Useful for health-related business opportunities and research.</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Show related suggestions if business idea was validated
    if hasattr(st.session_state, "business_idea") and st.session_state.business_idea:
        st.info(f"💡 **Related to your business idea:** '{st.session_state.business_idea}' - Consider analyzing related health trends below!")
    
    # Health trend analysis form
    with st.form("health_trend_form"):
        # Use a column to constrain the width of the text input
        col_health_topic = st.columns([2, 1])
        with col_health_topic[0]:
            # Pre-populate health topic if business idea contains health-related keywords
            default_health_topic = "HIV"
            if hasattr(st.session_state, "business_idea") and st.session_state.business_idea:
                business_idea_lower = st.session_state.business_idea.lower()
                if any(keyword in business_idea_lower for keyword in ["health", "medical", "fitness", "wellness", "disease", "treatment", "patient", "clinical"]):
                    # Extract potential health topic from business idea
                    health_keywords = ["diabetes", "hiv", "cancer", "mental health", "fitness", "nutrition", "obesity", "heart disease", "stroke", "alzheimer"]
                    for keyword in health_keywords:
                        if keyword in business_idea_lower:
                            default_health_topic = keyword.title()
                            break
            
            health_topic = st.text_input(
                "Health topic to analyze",
                placeholder="Example: HIV, Diabetes, Mental Health",
                value=default_health_topic
            )
        
        # Use a column to constrain the width of the multiselect
        col_demographics = st.columns([2, 1])
        with col_demographics[0]:
            # Demographics selection
            demographics_options = [
                "All age groups", 
                "By gender", 
                "18-25 age group", 
                "26-40 age group", 
                "41-65 age group", 
                "65+ age group", 
                "By socioeconomic status",
                "By risk behavior"
            ]
            selected_demographics = st.multiselect(
                "Demographics to analyze",
                options=demographics_options,
                default=["All age groups", "By gender"]
            )
        
        # Regions selection
        regions_options = [
            "Global", 
            "North America", 
            "Europe", 
            "Asia", 
            "Africa", 
            "South America", 
            "Australia/Oceania",
            # Countries
            "United States",
            "Canada",
            "United Kingdom",
            "Germany",
            "France",
            "China",
            "India",
            "Brazil",
            "South Africa",
            "Nigeria",
            "Kenya",
            "Australia",
            "Japan",
            "Russia",
            # Regions within continents
            "Western Europe",
            "Eastern Europe",
            "Southeast Asia",
            "East Asia",
            "South Asia",
            "Middle East",
            "North Africa",
            "Sub-Saharan Africa",
            "Central America",
            "Caribbean",
            # Metropolitan areas
            "Major Global Cities"
        ]
        
        # Create a multiselect widget with regions grouped by continents, countries, and metropolitan areas
        # Use st.expander to make UI cleaner
        col_regions = st.columns([2, 1])
        with col_regions[0]:
            with st.expander("Select Regions to Analyze"):
                # Create columns for better UI organization
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Select continents/major regions
                    continents = st.multiselect(
                        "Continents/Major Regions",
                        options=["Global", "North America", "Europe", "Asia", "Africa", "South America", "Australia/Oceania"],
                        default=["Global", "North America", "Africa"]
                    )
                
                with col2:
                    # Select countries
                    countries = st.multiselect(
                        "Countries",
                        options=["United States", "Canada", "United Kingdom", "Germany", "France", "China", "India", 
                                "Brazil", "South Africa", "Nigeria", "Kenya", "Australia", "Japan", "Russia"],
                        default=[]
                    )
                
                with col3:
                    # Select specific regions
                    specific_regions = st.multiselect(
                        "Specific Regions",
                        options=["Western Europe", "Eastern Europe", "Southeast Asia", "East Asia", "South Asia", 
                                "Middle East", "North Africa", "Sub-Saharan Africa", "Central America", "Caribbean", "Major Global Cities"],
                        default=[]
                    )
        
        # Combine all selected regions
        selected_regions = continents + countries + specific_regions
        
        health_submit_button = st.form_submit_button("Analyze Health Trends")
    
    # Handle health trend form submission
    if health_submit_button and health_topic:
        with st.spinner(f"Analyzing trends for {health_topic}... This may take a few minutes."):
            try:
                # Run the health trend analysis
                health_results = analyze_health_trends(
                    topic=health_topic,
                    demographics=selected_demographics,
                    regions=selected_regions
                )
                
                if health_results:
                    st.success(f"Successfully analyzed health trends for {health_topic}!")
                    
                    # Store results in session state for persistence
                    st.session_state.health_results = health_results
                    
                    # Display comprehensive health analysis
                    st.markdown("---")
                    st.subheader(f"📊 Health Trends Analysis: {health_topic}")
                    
                    # Executive Overview
                    st.markdown("""
                    <div style="background-color:#ffffff; padding:20px; border-radius:10px; margin-bottom:20px; border: 1px solid #e6e6e6; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h3 style="margin-top:0; color:#333333;">📋 Executive Overview</h3>
                        <p style="margin-bottom:0;">{}</p>
                    </div>
                    """.format(health_results.get("overview", "No overview available.")), unsafe_allow_html=True)
                    
                    # Create tabs for organized display
                    health_tab1, health_tab2, health_tab3, health_tab4, health_tab5 = st.tabs([
                        "🌍 Statistics & Demographics", "🚀 Opportunities & Trends", "🔬 Research & Advancements", "🏛️ Policy & Business", "📁 Sources"
                    ])
                    
                    with health_tab1:
                        st.subheader("Global and Regional Statistics")
                        
                        # Global prevalence
                        if "statistics" in health_results and "global_prevalence" in health_results["statistics"]:
                            st.markdown(f"""
                            <div style="background-color:#e8f4fd; padding:15px; border-radius:8px; margin-bottom:15px;">
                                <h4 style="color:#0c5460; margin-top:0;">🌍 Global Prevalence</h4>
                                <p style="margin-bottom:0;">{health_results["statistics"]["global_prevalence"]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Demographics breakdown
                        if "statistics" in health_results and "demographic_breakdown" in health_results["statistics"]:
                            st.markdown("#### 👥 Demographics Breakdown")
                            demographics = health_results["statistics"]["demographic_breakdown"]
                            
                            if demographics:
                                for demo in demographics:
                                    # Handle both string and dictionary formats
                                    if isinstance(demo, dict):
                                        st.markdown(f"""
                                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                            <h5 style="color:#333; margin:0 0 8px 0;">👤 {demo.get('group', 'N/A')}</h5>
                                            <p style="margin:0 0 5px 0;"><strong>Prevalence:</strong> {demo.get('prevalence', 'N/A')}</p>
                                            <p style="margin:0 0 5px 0;"><strong>Trends:</strong> {demo.get('trends', 'N/A')}</p>
                                            <p style="margin:0;"><strong>Key Insights:</strong> {demo.get('key_insights', 'N/A')}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        # Handle string format
                                        st.markdown(f"""
                                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                            <h5 style="color:#333; margin:0 0 8px 0;">👤 Demographic Analysis</h5>
                                            <p style="margin:0;">{demo}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.info("No demographic breakdown available.")
                        
                        # Regional breakdown with visualization
                        if "statistics" in health_results and "regional_breakdown" in health_results["statistics"]:
                            st.markdown("#### 🗺️ Regional Analysis")
                            regional_data = health_results["statistics"]["regional_breakdown"]
                            
                            if regional_data:
                                # Display regional data
                                for region in regional_data:
                                    # Handle both string and dictionary formats
                                    if isinstance(region, dict):
                                        st.markdown(f"""
                                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                            <h5 style="color:#333; margin:0 0 8px 0;">🌎 {region.get('region', 'N/A')}</h5>
                                            <p style="margin:0 0 5px 0;"><strong>Prevalence:</strong> {region.get('prevalence', 'N/A')}</p>
                                            <p style="margin:0 0 5px 0;"><strong>Trends:</strong> {region.get('trends', 'N/A')}</p>
                                            <p style="margin:0;"><strong>Key Factors:</strong> {region.get('key_factors', 'N/A')}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        # Handle string format
                                        st.markdown(f"""
                                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                            <h5 style="color:#333; margin:0 0 8px 0;">🌎 Regional Analysis</h5>
                                            <p style="margin:0;">{region}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.info("No regional breakdown available.")
                    
                    with health_tab2:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                            <div style="background-color:#fff3cd; padding:10px; border-radius:5px; margin-bottom:10px;">
                                <h4 style="color:#856404; margin:0;">🚀 Market Opportunities</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if "business_opportunities" in health_results and health_results["business_opportunities"]:
                                for opp in health_results["business_opportunities"]:
                                    # Handle both string and dictionary formats
                                    if isinstance(opp, dict):
                                        difficulty_color = "#28a745" if opp.get("implementation_difficulty", "").lower() == "low" else "#ffc107" if opp.get("implementation_difficulty", "").lower() == "medium" else "#dc3545"
                                        st.markdown(f"""
                                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                            <h5 style="color:#333; margin:0 0 8px 0;">💼 {opp.get('opportunity', 'N/A')}</h5>
                                            <p style="margin:0 0 5px 0;"><strong>Market Size:</strong> {opp.get('market_size', 'N/A')}</p>
                                            <p style="margin:0 0 5px 0;"><strong>Target:</strong> {opp.get('target_demographic', 'N/A')}</p>
                                            <p style="margin:0;"><strong>Difficulty:</strong> <span style="color:{difficulty_color}; font-weight:bold;">{opp.get('implementation_difficulty', 'N/A')}</span></p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        # Handle string format
                                        st.markdown(f"""
                                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                            <h5 style="color:#333; margin:0 0 8px 0;">💼 {opp}</h5>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            if "unmet_needs" in health_results and health_results["unmet_needs"]:
                                st.markdown("##### 🎯 Unmet Medical Needs")
                                for need in health_results["unmet_needs"]:
                                    st.markdown(f"• {need}")
                        
                        with col2:
                            st.markdown("""
                            <div style="background-color:#d4edda; padding:10px; border-radius:5px; margin-bottom:10px;">
                                <h4 style="color:#155724; margin:0;">📈 Emerging Trends</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if "emerging_trends" in health_results and health_results["emerging_trends"]:
                                for trend in health_results["emerging_trends"]:
                                    st.markdown(f"""
                                    <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                        <p style="margin:0;">📊 {trend}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No emerging trends identified.")
                    
                    with health_tab3:
                        st.markdown("#### 🔬 Recent Advancements")
                        
                        if "advancements" in health_results and health_results["advancements"]:
                            for advancement in health_results["advancements"]:
                                # Handle both string and dictionary formats
                                if isinstance(advancement, dict):
                                    st.markdown(f"""
                                    <div style="background-color:white; padding:15px; border-radius:8px; margin-bottom:15px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                                        <h5 style="color:#495057; margin-top:0;">🧪 {advancement.get('area', 'N/A')}</h5>
                                        <p style="margin-bottom:8px;"><strong>Description:</strong> {advancement.get('description', 'N/A')}</p>
                                        <p style="margin-bottom:8px;"><strong>Impact:</strong> {advancement.get('impact', 'N/A')}</p>
                                        <p style="margin-bottom:0;"><strong>Timeline:</strong> {advancement.get('timeline', 'N/A')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    # Handle string format
                                    st.markdown(f"""
                                    <div style="background-color:white; padding:15px; border-radius:8px; margin-bottom:15px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                                        <h5 style="color:#495057; margin-top:0;">🧪 Recent Advancement</h5>
                                        <p style="margin-bottom:0;">{advancement}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.info("No recent advancements data available.")
                    
                    with health_tab4:
                        st.markdown("#### 🏛️ Policy Implications")
                        
                        if "policy_implications" in health_results and health_results["policy_implications"]:
                            for policy in health_results["policy_implications"]:
                                st.markdown(f"""
                                <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                                    <p style="margin:0;">🏛️ {policy}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No policy implications available.")
                    
                    with health_tab5:
                        st.markdown("#### 📚 Data Sources")
                        
                        if "data_sources" in health_results and health_results["data_sources"]:
                            for i, source in enumerate(health_results["data_sources"]):
                                source_icon = "🏥" if "WHO" in source else "🇺🇸" if "CDC" in source else "🌍" if "Our World" in source else "📖" if "PubMed" in source else "🔍"
                                st.markdown(f"{source_icon} {source}")
                        else:
                            st.info("No data sources available.")
                    
                    # Download health results
                    st.markdown("---")
                    st.download_button(
                        label=f"📥 Download Complete Health Analysis for {health_topic} (JSON)",
                        data=json.dumps(health_results, indent=2),
                        file_name=f"health_analysis_{health_topic.replace(' ', '_')}.json",
                        mime="application/json"
                    )
                else:
                    st.error(f"Failed to retrieve health trend analysis for {health_topic}.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                logging.error(f"Health trend analysis error: {e}", exc_info=True)
    
    # Auto-generate health trends based on business idea validation
    elif (hasattr(st.session_state, "auto_generate_related") and 
          st.session_state.auto_generate_related and 
          hasattr(st.session_state, "business_idea") and 
          not hasattr(st.session_state, "health_auto_generated")):
        
        business_idea_lower = st.session_state.business_idea.lower()
        if any(keyword in business_idea_lower for keyword in ["health", "medical", "fitness", "wellness", "disease", "treatment", "patient", "clinical"]):
            st.info("🤖 Auto-generating related health trends analysis based on your business idea...")
            
            # Extract health topic from business idea
            auto_health_topic = "Health Technology"
            health_keywords = ["diabetes", "hiv", "cancer", "mental health", "fitness", "nutrition", "obesity", "heart disease"]
            for keyword in health_keywords:
                if keyword in business_idea_lower:
                    auto_health_topic = keyword.title()
                    break
            
            with st.spinner(f"Auto-analyzing health trends for {auto_health_topic}..."):
                try:
                    auto_health_results = analyze_health_trends(
                        topic=auto_health_topic,
                        demographics=["All age groups", "By gender"],
                        regions=["Global", "North America", "Europe"]
                    )
                    
                    if auto_health_results:
                        st.success(f"✅ Auto-generated health trends analysis for {auto_health_topic}!")
                        st.session_state.health_results = auto_health_results
                        st.session_state.health_auto_generated = True
                        
                        # Show a preview of the results
                        st.markdown("### 📊 Auto-Generated Health Analysis Preview")
                        if "overview" in auto_health_results:
                            st.info(auto_health_results["overview"][:200] + "..." if len(auto_health_results["overview"]) > 200 else auto_health_results["overview"])
                        st.markdown("*Full results available above in the Health Trends Analysis section*")
                        
                except Exception as e:
                    st.warning(f"Could not auto-generate health analysis: {e}")
                    logging.error(f"Auto health trend analysis error: {e}", exc_info=True)
    
with main_tab3:
    st.markdown("<h2 class='idea-validator-title'>💡 Tech Business Ideas</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="idea-validator-description">
            <p>Generate innovative technology business ideas based on current market trends and opportunities.
            Select your preferences below to customize the recommendations.</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Show related suggestions if business idea was validated
    if hasattr(st.session_state, "business_idea") and st.session_state.business_idea:
        st.info(f"💡 **Related to your business idea:** '{st.session_state.business_idea}' - Explore similar tech opportunities below!")
    
    # Tech business ideas form
    with st.form("tech_ideas_form"):
        # Technology focus areas
        focus_areas_options = [
            "SaaS", 
            "AI/ML", 
            "HealthTech", 
            "FinTech", 
            "EdTech", 
            "CleanTech",
            "AR/VR",
            "Blockchain",
            "IoT", 
            "Cybersecurity",
            "E-commerce",
            "Robotics"
        ]
        
        # Auto-suggest focus areas based on business idea
        default_focus_areas = ["AI/ML", "SaaS", "HealthTech"]
        if hasattr(st.session_state, "business_idea") and st.session_state.business_idea:
            business_idea_lower = st.session_state.business_idea.lower()
            suggested_areas = []
            
            # Map business idea keywords to focus areas
            if any(keyword in business_idea_lower for keyword in ["health", "medical", "fitness", "wellness", "patient"]):
                suggested_areas.append("HealthTech")
            if any(keyword in business_idea_lower for keyword in ["finance", "payment", "money", "banking", "crypto"]):
                suggested_areas.append("FinTech")
            if any(keyword in business_idea_lower for keyword in ["education", "learning", "course", "student", "teach"]):
                suggested_areas.append("EdTech")
            if any(keyword in business_idea_lower for keyword in ["ai", "artificial intelligence", "machine learning", "ml", "smart"]):
                suggested_areas.append("AI/ML")
            if any(keyword in business_idea_lower for keyword in ["saas", "software", "app", "platform", "service"]):
                suggested_areas.append("SaaS")
            if any(keyword in business_idea_lower for keyword in ["environment", "green", "clean", "sustainable", "renewable"]):
                suggested_areas.append("CleanTech")
            if any(keyword in business_idea_lower for keyword in ["security", "secure", "protection", "privacy"]):
                suggested_areas.append("Cybersecurity")
            if any(keyword in business_idea_lower for keyword in ["ecommerce", "e-commerce", "shop", "retail", "marketplace"]):
                suggested_areas.append("E-commerce")
            if any(keyword in business_idea_lower for keyword in ["iot", "internet of things", "sensor", "device", "connected"]):
                suggested_areas.append("IoT")
            if any(keyword in business_idea_lower for keyword in ["vr", "ar", "virtual", "augmented", "reality"]):
                suggested_areas.append("AR/VR")
            if any(keyword in business_idea_lower for keyword in ["blockchain", "crypto", "decentralized", "web3"]):
                suggested_areas.append("Blockchain")
            if any(keyword in business_idea_lower for keyword in ["robot", "automation", "robotic"]):
                suggested_areas.append("Robotics")
            
            # Use suggested areas if any were found, otherwise use defaults
            if suggested_areas:
                default_focus_areas = list(set(suggested_areas))  # Remove duplicates
        
        # Use columns for better width control - make the first column narrower
        col_focus, col_empty1 = st.columns([1.2, 2])
        with col_focus:
            selected_focus_areas = st.multiselect(
                "Technology focus areas",
                options=focus_areas_options,
                default=default_focus_areas
            )
        
        # Create two columns for the selects - make them narrower
        col_market, col_time, col_empty2 = st.columns([1, 1, 1.2])
        
        # Market size selection
        with col_market:
            market_size = st.selectbox(
                "Target market size",
                options=["All sizes", "Small business", "Medium business", "Enterprise"],
                index=0
            )
        
        # Time horizon selection
        with col_time:
            timeframe = st.selectbox(
                "Time horizon",
                options=["Near-term (1-2 years)", "Mid-term (3-5 years)", "Long-term (5+ years)"],
                index=0
            )
        
        tech_submit_button = st.form_submit_button("Generate Tech Business Ideas")
    
    # Handle tech business ideas form submission
    if tech_submit_button:
        with st.spinner("Generating technology business ideas... This may take a few minutes."):
            try:
                # Extract timeframe value
                timeframe_value = timeframe.split("(")[0].strip().lower()
                
                # Run the tech ideas generation
                tech_results = generate_tech_business_ideas(
                    focus_areas=selected_focus_areas,
                    market_size=market_size.split()[0].lower(),
                    timeframe=timeframe_value
                )
                
                # Store the results in session state
                st.session_state.tech_results = tech_results
                
                # Success message
                st.success("Tech business ideas generated!")
                
            except Exception as e:
                st.error(f"Error generating tech business ideas: {str(e)}")
    
    # Auto-generate tech business ideas based on business idea validation
    elif (hasattr(st.session_state, "auto_generate_related") and 
          st.session_state.auto_generate_related and 
          hasattr(st.session_state, "business_idea") and 
          not hasattr(st.session_state, "tech_auto_generated")):
        
        st.info("🤖 Auto-generating related tech business ideas based on your business idea...")
        
        # Use the suggested focus areas we calculated earlier
        business_idea_lower = st.session_state.business_idea.lower()
        auto_focus_areas = []
        
        # Map business idea keywords to focus areas (same logic as in the form)
        if any(keyword in business_idea_lower for keyword in ["health", "medical", "fitness", "wellness", "patient"]):
            auto_focus_areas.append("HealthTech")
        if any(keyword in business_idea_lower for keyword in ["finance", "payment", "money", "banking", "crypto"]):
            auto_focus_areas.append("FinTech")
        if any(keyword in business_idea_lower for keyword in ["education", "learning", "course", "student", "teach"]):
            auto_focus_areas.append("EdTech")
        if any(keyword in business_idea_lower for keyword in ["ai", "artificial intelligence", "machine learning", "ml", "smart"]):
            auto_focus_areas.append("AI/ML")
        if any(keyword in business_idea_lower for keyword in ["saas", "software", "app", "platform", "service"]):
            auto_focus_areas.append("SaaS")
        
        # Use defaults if no specific areas found
        if not auto_focus_areas:
            auto_focus_areas = ["AI/ML", "SaaS", "HealthTech"]
        
        with st.spinner("Auto-generating technology business ideas..."):
            try:
                auto_tech_results = generate_tech_business_ideas(
                    focus_areas=auto_focus_areas,
                    market_size="all",
                    timeframe="near-term"
                )
                
                if auto_tech_results:
                    st.success("✅ Auto-generated tech business ideas!")
                    st.session_state.tech_results = auto_tech_results
                    st.session_state.tech_auto_generated = True
                    
                    # Show a preview of the results
                    st.markdown("### 💡 Auto-Generated Tech Ideas Preview")
                    if "market_overview" in auto_tech_results:
                        st.info(auto_tech_results["market_overview"][:200] + "..." if len(auto_tech_results["market_overview"]) > 200 else auto_tech_results["market_overview"])
                    if "ideas" in auto_tech_results and auto_tech_results["ideas"]:
                        idea_count = len(auto_tech_results["ideas"])
                        st.write(f"📊 Generated {idea_count} tech business ideas in areas: {', '.join(auto_focus_areas)}")
                    st.markdown("*Full results available above in the Tech Business Ideas section*")
                    
            except Exception as e:
                st.warning(f"Could not auto-generate tech business ideas: {e}")
                logging.error(f"Auto tech ideas generation error: {e}", exc_info=True)
    
    # Display tech business ideas results if available
    if hasattr(st.session_state, "tech_results") and st.session_state.tech_results:
        tech_data = st.session_state.tech_results
        
        # Market overview section
        st.subheader("Market Overview")
        st.write(tech_data["market_overview"])
        
        # Business ideas section
        st.subheader("Business Ideas")
        
        # Create a metric of difficulty vs potential
        ideas = tech_data["ideas"]
        if ideas:
            for idx, idea in enumerate(ideas):
                with st.expander(f"{idx+1}. {idea['name']}"):
                    # Create two columns for metrics and details
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Display metrics
                        st.metric("Implementation Difficulty", f"{idea['implementation_difficulty']}/5")
                        st.metric("Market Potential", f"{idea['market_potential']}/5")
                        st.caption(f"Category: {idea['category']}")
                    
                    with col2:
                        # Display details
                        st.markdown("#### Description")
                        st.write(idea["description"])
                        
                        st.markdown("#### Problem Solved")
                        st.write(idea["problem_solved"])
                        
                        st.markdown("#### Target Market")
                        st.write(idea["target_market"])
                        
                        st.markdown("#### Technology Stack")
                        for tech in idea["technology_stack"]:
                            st.markdown(f"- {tech}")
                        
                        st.markdown("#### Revenue Streams")
                        for stream in idea["revenue_streams"]:
                            st.markdown(f"- {stream}")
        
        # Implementation factors section
        st.subheader("Implementation Factors to Consider")
        for factor in tech_data["implementation_factors"]:
            st.markdown(f"- {factor}")
        
        # Market trends section
        st.subheader("Current Market Trends")
        for trend in tech_data["market_trends"]:
            st.markdown(f"- {trend}")
                
# Sidebar configuration
with st.sidebar:
    st.markdown("<h1 class='sidebar-main-title'>💡 Business Idea Validator</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sidebar-main-description">
            <p>Validate your business ideas by analyzing discussions on HackerNews and Reddit.</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    st.markdown("<div class='custom-hr-sidebar'></div>", unsafe_allow_html=True)
    st.markdown("<h3 class='sidebar-heading'>Configuration</h3>", unsafe_allow_html=True)
    
    # Note: These parameters are passed to the validator function
    hn_posts = st.slider(
        "HackerNews posts to analyze",
        min_value=5,
        max_value=30,
        value=10,
        step=5
    )
    
    reddit_posts = st.slider(
        "Reddit posts to analyze",
        min_value=5,
        max_value=30,
        value=10,
        step=5
    )
    
    keywords = st.slider(
        "Number of keywords to generate",
        min_value=1,
        max_value=5,
        value=3
    )
    
    # Note: The model selection is for display purposes only
    # The actual model is configured in keyword_generator.py
    
    model = st.selectbox(
        "LLM Model (for reference only)",
        options=["google/gemini-1.5-pro", "anthropic/claude-3-opus-20240229", "meta-llama/llama-3-8b-instruct"],
        index=2,
        help="Note: Currently using meta-llama/llama-3-8b-instruct in the backend"
    )
    
    st.markdown("<div class='custom-hr-sidebar'></div>", unsafe_allow_html=True)
    st.markdown("<h3 class='sidebar-heading'>Previous Validations</h3>", unsafe_allow_html=True)
    
    # List previous validations
    if os.path.exists(DATA_DIR):
        run_dirs = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
        run_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(DATA_DIR, d)), reverse=True)
        
        # Display a message if no validations are found
        if not run_dirs:
            st.markdown("<div class='no-validations'>No previous validations found</div>", unsafe_allow_html=True)
        else:
            # Create a container for the buttons with centering
            with st.container():
                for run_dir in run_dirs[:5]:  # Show the last 5 runs
                    info_path = os.path.join(DATA_DIR, run_dir, "info.json")
                    if os.path.exists(info_path):
                        with open(info_path, "r") as f:
                            info = json.load(f)
                        
                        # Extract business idea and timestamp
                        idea = info.get('business_idea', 'Unknown idea')
                        timestamp = info.get('timestamp', '')
                        
                        # Truncate idea if it's too long and format the button text
                        idea_display = idea if len(idea) < 30 else idea[:27] + "..."
                        button_label = f"{idea_display}\n{timestamp}"
                        
                        if st.button(button_label, key=f"prev_validation_{run_dir}", use_container_width=True):
                            st.session_state.selected_run = run_dir
                            st.rerun() # Changed from st.experimental_rerun()
    else:
        # Display a message if the data directory doesn't exist
        st.markdown("<div class='no-validations'>No previous validations found</div>", unsafe_allow_html=True)

# Input form and validation within the business idea validation tab
with main_tab1:
    # Capture sidebar values before the form
    keywords_value = keywords
    hn_posts_value = hn_posts
    reddit_posts_value = reddit_posts
    
    with st.form("validation_form"):
        business_idea = st.text_area(
            "Enter your business idea",
            placeholder="Example: A mobile app that helps pet owners find pet-friendly cafes and restaurants nearby",
            height=100
        )
        
        # Advanced Options section (now inside the form)
        with st.expander("Advanced Options", expanded=False):
            st.markdown("These options will be implemented in a future version.")
            
            # Create two columns for the first row
            col1, col2 = st.columns(2)
            
            with col1:
                adv_keywords = st.number_input(
                    "Number of keywords to generate:",
                    min_value=1,
                    max_value=10,
                    value=3
                )
            
            with col2:
                max_hn_pages = st.number_input(
                    "Max HackerNews pages per keyword:",
                    min_value=1,
                    max_value=10,
                    value=3
                )
            
            # Create two columns for the second row
            col3, col4 = st.columns(2)
            
            with col3:
                max_reddit_pages = st.number_input(
                    "Max Reddit pages per keyword:",
                    min_value=1, 
                    max_value=10,
                    value=3
                )
            
            with col4:
                max_reddit_posts = st.number_input(
                    "Max Reddit posts to analyze:",
                    min_value=5,
                    max_value=50,
                value=20
            )
        
        # Submit button inside the form
        submit_button = st.form_submit_button("Validate Business Idea")
    
    # Handle form submission (still inside main_tab1 but outside the form)
    if submit_button and business_idea:
        with st.spinner("Validating your business idea... This may take a few minutes."):
            try:
                # Run the validation with parameters
                # Since advanced options are currently marked as "future version",
                # we'll still use the sidebar settings for actual validation
                results = validate_business_idea(
                    business_idea=business_idea,
                    keywords_count=keywords_value,
                    max_pages_per_keyword=3,
                    max_hn_posts=hn_posts_value,
                    max_reddit_posts=reddit_posts_value
                )
                
                # In a future version, the code would use the advanced options like this:
                # results = validate_business_idea(
                #     business_idea=business_idea,
                #     keywords_count=adv_keywords,
                #     max_pages_per_keyword=max_hn_pages,
                #     max_hn_posts=hn_posts,
                #     max_reddit_posts=max_reddit_posts
                # )
                
                # Store the results in session state
                st.session_state.results = results
                
                # Store business idea and extract keywords for cross-tab functionality
                st.session_state.business_idea = business_idea
                
                # Clear previous auto-generation flags for fresh related content
                if hasattr(st.session_state, "health_auto_generated"):
                    del st.session_state.health_auto_generated
                if hasattr(st.session_state, "tech_auto_generated"):
                    del st.session_state.tech_auto_generated
                
                # Extract keywords from validation results for related searches
                # Try to get keywords from the validation data directory if available
                try:
                    # Find the most recent validation directory for this business idea
                    data_dirs = [d for d in os.listdir(DATA_DIR) if d.startswith("validation_")]
                    if data_dirs:
                        latest_dir = max(data_dirs, key=lambda x: os.path.getctime(os.path.join(DATA_DIR, x)))
                        keywords_file = os.path.join(DATA_DIR, latest_dir, "01_keywords.json")
                        if os.path.exists(keywords_file):
                            with open(keywords_file, 'r') as f:
                                keyword_data = json.load(f)
                                st.session_state.extracted_keywords = keyword_data.get('keywords', [])
                        else:
                            st.session_state.extracted_keywords = []
                    else:
                        st.session_state.extracted_keywords = []
                except Exception as e:
                    logging.warning(f"Could not extract keywords: {e}")
                    st.session_state.extracted_keywords = []
                
                # Automatically generate related content for other tabs
                st.session_state.auto_generate_related = True

            except Exception as e:
                st.error(f"An error occurred during validation: {str(e)}")
                logging.error(f"Error in validation_form: {e}", exc_info=True)
                st.session_state.results = None # Clear previous results on error
                

# Display results if available (inside main_tab1)
    if hasattr(st.session_state, "results") and st.session_state.results:
        results = st.session_state.results
        
        # Create a single column for the chart to take full width initially
        # st.subheader("Validation Overview")

        overall_score = results.get('overall_score', 0)
        summary_text = results.get('market_validation_summary', "Failed to generate analysis")

        # Data for the new bar chart
        labels = ["Key Pain Points", "Existing Solutions", "Market Opportunities", "Recommendations"]
        
        # Helper function to safely count valid items
        def get_valid_item_count(key_name):
            items_list = results.get(key_name, [])  # Default to empty list if key missing
            # Check if list is not empty and its first element is not "Analysis failed"
            if items_list and isinstance(items_list, list) and items_list[0] != "Analysis failed":
                return len(items_list)
            return 0

        values = [
            get_valid_item_count('key_pain_points'),
            get_valid_item_count('existing_solutions'),
            get_valid_item_count('market_opportunities'),
            get_valid_item_count('recommendations')
        ]

        # Calculate total items for percentage calculation
        total_items = sum(values)
        
        # Create text for bars including count and percentage
        bar_texts = []
        if total_items > 0:
            for v in values:
                percentage = (v / total_items) * 100
                bar_texts.append(f"{v} ({percentage:.0f}%)")
        else:
            # If total_items is 0, display count and 0%
            bar_texts = [f"{v} (0%)" for v in values]

        # Define colors for the bars
        colors = ['#FF6347', '#4682B4', '#32CD32', '#FFD700'] # Tomato, SteelBlue, LimeGreen, Gold

        fig_bar_chart = go.Figure(data=[go.Bar(
            x=labels, 
            y=values,
            marker_color=colors,
            text=bar_texts # Updated to show count and percentage
        )])
        
        fig_bar_chart.update_layout(
            title_text='Key Validation Metrics Overview',
            yaxis_title='Count of Items',
            height=400, # Adjust height as needed
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_bar_chart, use_container_width=True)

        # Explanations for the categories in the bar chart
        st.markdown("""
        <div style="background-color:#ffffff; padding:15px; border-radius:8px; margin-top:10px; margin-bottom:20px; color:#333333; border: 1px solid #e6e6e6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <h4 style="margin-top:0; margin-bottom:10px; color:#333333;">Understanding the Metrics:</h4>
            <ul>
                <li><b>Key Pain Points:</b> Identifies the specific problems, frustrations, or unmet needs of potential customers that your business idea aims to address. A higher number suggests more identified problems your idea could solve.</li>
                <li><b>Existing Solutions:</b> Lists current products, services, or workarounds that people use to deal with these pain points. This helps gauge the competitive landscape and differentiation opportunities. A higher number indicates more existing alternatives.</li>
                <li><b>Market Opportunities:</b> Highlights potential gaps, underserved niches, or emerging trends in the market that your business idea could leverage. More opportunities can indicate a favorable market entry.</li>
                <li><b>Recommendations:</b> Provides actionable advice and strategic suggestions based on the overall analysis to help refine your business idea and plan next steps.
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Business Idea Analysis")
        
        # Summary card at the top
        st.markdown("""
        <div style="background-color:#ffffff; padding:20px; border-radius:10px; margin-bottom:20px; border: 1px solid #e6e6e6; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0; color:#333333;">Executive Summary</h3>
            <p style="margin-bottom:15px;">{}</p>
            <div style="display:flex; align-items:center;">
                <span style="font-weight:600; margin-right:10px;">Validation Result:</span>
                <span style="padding:5px 12px; border-radius:15px; font-weight:600; {}">
                    {}
                </span>
            </div>
        </div>
        """.format(
            summary_text,
            "background-color:#d4edda; color:#155724;" if isinstance(overall_score, (int, float)) and overall_score >= 80 else 
            "background-color:#fff3cd; color:#856404;" if isinstance(overall_score, (int, float)) and overall_score >= 60 else 
            "background-color:#f8d7da; color:#721c24;",
            "Strong Validation" if isinstance(overall_score, (int, float)) and overall_score >= 80 else 
            "Moderate Validation" if isinstance(overall_score, (int, float)) and overall_score >= 60 else 
            "Needs Refinement"
        ), unsafe_allow_html=True)
        
        # Create a single set of well-organized tabs
        analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4, analysis_tab5 = st.tabs([
            "Overview", "Pain Points & Solutions", "Market Opportunities", "Platform Insights", "Recommendations"
        ])
        
        with analysis_tab1:
            st.subheader("Analysis Overview")
            
            # Create two columns for the score and key metrics
            overview_col1, overview_col2 = st.columns([1, 3])
            
            with overview_col1:
                st.metric(
                    "Overall Score",
                    f"{overall_score}/100" if isinstance(overall_score, (int, float)) else "N/A"
                )
                
                # Show validation level with color coding
                if isinstance(overall_score, (int, float)):
                    if overall_score >= 80:
                        st.success("Strong validation")
                    elif overall_score >= 60:
                        st.warning("Moderate validation")
                    else:
                        st.error("Needs refinement")
                else:
                    st.error("Score not available")
                    
            with overview_col2:
                st.write("This analysis evaluates your business idea across multiple dimensions, considering market needs, existing competition, and potential opportunities.")
                st.write(summary_text)
        
        with analysis_tab2:
            # Create two columns for pain points and solutions
            pain_col1, pain_col2 = st.columns(2)
            
            with pain_col1:
                st.markdown("""
                <div style="background-color:#f8d7da; padding:10px; border-radius:5px; margin-bottom:10px;">
                    <h3 style="color:#721c24; margin:0;">Key Pain Points</h3>
                </div>
                """, unsafe_allow_html=True)
                
                key_pain_points = results.get('key_pain_points', [])
                if key_pain_points and key_pain_points[0] != "Analysis failed":
                    for point in key_pain_points:
                        st.markdown(f"""
                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                            <p style="margin:0;">🔍 {point}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No key pain points identified.")
            
            with pain_col2:
                st.markdown("""
                <div style="background-color:#d1ecf1; padding:10px; border-radius:5px; margin-bottom:10px;">
                    <h3 style="color:#0c5460; margin:0;">Existing Solutions</h3>
                </div>
                """, unsafe_allow_html=True)
                
                existing_solutions = results.get('existing_solutions', [])
                if existing_solutions and existing_solutions[0] != "Analysis failed":
                    for solution in existing_solutions:
                        st.markdown(f"""
                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                            <p style="margin:0;">💡 {solution}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No existing solutions identified.")
        
        with analysis_tab3:
            st.markdown("""
            <div style="background-color:#d4edda; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3 style="color:#155724; margin:0;">Market Opportunities</h3>
            </div>
            """, unsafe_allow_html=True)
            
            market_opportunities = results.get('market_opportunities', [])
            if market_opportunities and market_opportunities[0] != "Analysis failed":
                for opportunity in market_opportunities:
                    st.markdown(f"""
                    <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                        <p style="margin:0;">🚀 {opportunity}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No clear market opportunities identified.")
        
        with analysis_tab4:
            st.markdown("""
            <div style="background-color:#fff3cd; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3 style="color:#856404; margin:0;">Platform Insights</h3>
            </div>
            """, unsafe_allow_html=True)
            
            platform_insights = results.get('platform_insights', [])
            if platform_insights:
                for platform in platform_insights:
                    platform_name = platform.get('platform', 'N/A')
                    platform_icon = "📰" if platform_name == "HackerNews" else "🔄" if platform_name == "Reddit" else "🌐" if platform_name == "Web Search" else "📊"
                    
                    st.markdown(f"""
                    <div style="background-color:white; padding:15px; border-radius:5px; margin-bottom:15px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                        <h4 style="color:#495057; margin-top:0;">{platform_icon} {platform_name} Insights</h4>
                        <p style="margin-bottom:0;">{platform.get('insights', 'No insights available.')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No platform insights found.")
        
        with analysis_tab5:
            st.markdown("""
            <div style="background-color:#e2e3e5; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3 style="color:#383d41; margin:0;">Recommendations</h3>
            </div>
            """, unsafe_allow_html=True)
            
            recommendations = results.get('recommendations', [])
            if recommendations and recommendations[0] != "Analysis failed":
                for i, rec in enumerate(recommendations):
                    st.markdown(f"""
                    <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                        <p style="margin:0;"><b>#{i+1}:</b> ✅ {rec}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recommendations available.")
    
    # Load previous validation if selected (inside main_tab1)
    if hasattr(st.session_state, "selected_run"):
        run_dir = st.session_state.selected_run
        analysis_path = os.path.join(DATA_DIR, run_dir, "final_analysis.json")
        info_path = os.path.join(DATA_DIR, run_dir, "info.json")
        
        results = None # Initialize results
        info = None # Initialize info

        if os.path.exists(analysis_path) and os.path.exists(info_path):
            with open(analysis_path, "r") as f:
                results = json.load(f)
            
            with open(info_path, "r") as f:
                info = json.load(f)
            
            st.subheader(f"Previous Validation: {info.get('business_idea', 'Unknown idea')}")
            st.write(f"Validated on: {info.get('timestamp', 'Unknown date')}")
        
        # Check if results and info were loaded successfully
        if results and info:
            # Create two columns for the score and summary
            col1, col2 = st.columns([1, 3])
            
            # Display the overall score
            with col1:
                st.metric(
                    "Overall Score",
                    f"{results.get('overall_score', 'N/A')}/100", # Use .get for safety
                    delta=None
                )
                
                # Add a verdict based on the score
                overall_score = results.get('overall_score')
                if isinstance(overall_score, (int, float)): # Check if score is a number
                    if overall_score >= 80:
                        st.success("Strong validation")
                    elif overall_score >= 60:
                        st.info("Good validation")
                    elif overall_score >= 40:
                        st.warning("Mixed validation")
                    else:
                        st.error("Poor validation")
                else:
                    st.error("Score not available.")

            # Display the summary
            with col2:
                st.subheader("Summary")
                st.write(results.get('market_validation_summary', 'Summary not available.')) # Use .get
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["Pain Points & Solutions", "Opportunities", "Platform Insights", "Recommendations"])
            
            with tab1:
                # Create two columns for pain points and solutions
                col1_tab1, col2_tab1 = st.columns(2) # Renamed to avoid conflict
                
                with col1_tab1:
                    st.subheader("Key Pain Points")
                    key_pain_points = results.get('key_pain_points', []) # Use .get
                    if key_pain_points:
                        for point in key_pain_points:
                            st.markdown(f"- {point}")
                    else:
                        st.info("No key pain points found.")
                
                with col2_tab1:
                    st.subheader("Existing Solutions")
                    existing_solutions = results.get('existing_solutions', []) # Use .get
                    if existing_solutions:
                        for solution in existing_solutions:
                            st.markdown(f"- {solution}")
                    else:
                        st.info("No existing solutions found.")
            
            with tab2:
                st.subheader("Market Opportunities")
                market_opportunities = results.get('market_opportunities', []) # Use .get
                if market_opportunities:
                    for opportunity in market_opportunities:
                        st.markdown(f"- {opportunity}")
                else:
                    st.info("No market opportunities found.")
            
            with tab3:
                # Display platform insights
                platform_insights = results.get('platform_insights', []) # Use .get
                if platform_insights:
                    for platform in platform_insights:
                        st.subheader(f"{platform.get('platform', 'N/A')} Insights") # Use .get
                        st.write(platform.get('insights', 'No insights available.')) # Use .get
                else:
                    st.info("No platform insights found.")
            
            with tab4:
                st.subheader("Recommendations")
                recommendations = results.get('recommendations', []) # Use .get
                if recommendations:
                    for rec in recommendations:
                        st.markdown(f"- {rec}")
                else:
                    st.info("No recommendations found.")
        else:
            st.error(f"Could not load the selected validation run data for '{run_dir}'. Check if 'final_analysis.json' and 'info.json' exist in the directory.")

    # Add a validation results review section (inside main_tab1)
    st.markdown("<hr style='margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#000000; margin-bottom: 20px;'>Validation Results: reviews</h2>", unsafe_allow_html=True)

    # If we have validation results, display user reviews/testimonials for similar ideas
    # This is a placeholder section that would be populated with real data in a future version
    if hasattr(st.session_state, "results") and st.session_state.results:
        # Create two columns for testimonials/reviews
        rev_col1, rev_col2 = st.columns(2)
        
        with rev_col1:
            st.markdown("""
            <div style="background-color:#ffffff; padding:15px; border-radius:10px; margin-bottom:15px; color:#333333; border: 1px solid #e6e6e6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <p><em>"This validation tool helped me identify critical gaps in my business plan that I hadn't considered. The market insights saved me months of research!"</em></p>
                <p style="text-align:right; font-weight:bold;">— Sarah K., Fintech Startup Founder</p>
            </div>
 """, unsafe_allow_html=True)
        
        with rev_col2:
            st.markdown("""

            <div style="background-color:#ffffff; padding:15px; border-radius:10px; margin-bottom:15px; color:#333333; border: 1px solid #e6e6e6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <p><em>"I was surprised by how accurately the tool identified our target market pain points. We pivoted our approach based on the insights and saw immediate traction."</em></p>
                <p style="text-align:right; font-weight:bold;">— Michael T., SaaS Entrepreneur</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Complete a validation to see how other entrepreneurs have benefited from these insights.")

# Add a new section that's always visible below everything else
st.markdown("<hr style='margin-top: 30px; margin-bottom: 30px;'>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#000000; margin-bottom: 20px;'>Next Steps for Your Business Idea</h2>", unsafe_allow_html=True)

# Create a two-column layout for the new section
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background-color:#ffffff; padding:15px; border-radius:10px; border: 1px solid #e6e6e6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h4 style="color:#000000;">Market Research Resources</h4>
        <ul>
            <li><b>Industry Reports:</b> Search for market size, trends, and growth projections</li>
            <li><b>Competitor Analysis:</b> Study similar businesses and their strategies</li>
            <li><b>Target Audience:</b> Define your ideal customer profile in detail</li>
            <li><b>Market Surveys:</b> Gather direct feedback from potential customers</li>
        </ul>
        <a href="https://www.sba.gov/business-guide/plan-your-business/market-research-competitive-analysis" target="_blank" style="color:#FF8C00;">
            Small Business Administration Guide →
        </a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color:#ffffff; padding:15px; border-radius:10px; border: 1px solid #e6e6e6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h4 style="color:#000000;">Business Plan Development</h4>
        <ul>
            <li><b>Executive Summary:</b> Clear overview of your business concept</li>
            <li><b>Financial Projections:</b> Revenue models and startup costs</li>
            <li><b>Marketing Strategy:</b> Customer acquisition and retention plans</li>
            <li><b>Operations Plan:</b> Day-to-day business operations</li>
        </ul>
        <a href="https://www.score.org/resource/business-plan-template-startup-business" target="_blank" style="color:#FF8C00;">
            SCORE Business Plan Template →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Add a call to action button
st.markdown("<div style='margin-top: 20px; text-align: center;'>", unsafe_allow_html=True)

# Create an HTML button with custom styling instead of using st.button
st.markdown("""
<div style="text-align: center; width: 100%;">
    <style>
    .custom-report-button {
        background-color: black !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        border-bottom: 2px solid transparent !important; /* Transparent border by default */
        transition: all 0.3s ease !important;
        width: auto !important;
        min-width: 180px !important;
        cursor: pointer;
        display: inline-block;
        text-align: center;
        margin: 0 auto !important;
    }
    .custom-report-button:hover {
        background-color: #333333 !important;
        border-bottom: 2px solid #ff6347 !important;
        transform: translateY(-1px) !important;
    }
    .custom-report-button:active {
        border-bottom: 2px solid tomato !important; /* Show tomato underline when active */
        transform: translateY(1px) !important;
    }
    </style>
    <button class="custom-report-button" id="report-btn" 
    onclick="
        this.innerText = 'Loading...';
        setTimeout(() => {
            document.getElementById('report-info').style.display = 'block';
            this.innerText = 'Get Market Report';
        }, 500);">
        Get Market Report
    </button>
    <div id="report-info" style="display: none; margin-top: 15px; padding: 10px; background-color: #e7f3fe; border-left: 6px solid #2196F3; border-radius: 4px;">
        This feature will be available in the next version! It will provide a comprehensive market analysis report for your business idea.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Display stored health results if available (outside the form submission)
if hasattr(st.session_state, "health_results") and st.session_state.health_results:
    health_results = st.session_state.health_results
    
    # Only display if we're not currently processing a new analysis
    if not health_submit_button:
        st.markdown("---")
        st.subheader("📊 Previous Health Trends Analysis")
        
        # Simplified display of stored results
        st.markdown("""
        <div style="background-color:#f8f9fa; padding:15px; border-radius:8px; margin-bottom:15px; border: 1px solid #dee2e6;">
            <h4 style="margin-top:0; color:#495057;">📋 Overview</h4>
            <p style="margin-bottom:0;">{}</p>
        </div>
        """.format(health_results.get("overview", "No overview available.")), unsafe_allow_html=True)
        
        # Key insights in columns
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            if "unmet_needs" in health_results and health_results["unmet_needs"]:
                st.markdown("##### 🎯 Key Unmet Needs")
                for need in health_results["unmet_needs"][:3]:  # Show top 3
                    st.markdown(f"• {need}")
                    
        with insight_col2:
            if "business_opportunities" in health_results and health_results["business_opportunities"]:
                st.markdown("##### 💼 Business Opportunities")
                for opp in health_results["business_opportunities"][:2]:  # Show top 2
                    # Handle both string and dictionary formats
                    if isinstance(opp, dict):
                        st.markdown(f"• {opp.get('opportunity', 'N/A')}")
                    else:
                        st.markdown(f"• {opp}")
        
        # Clear results button
        if st.button("🗑️ Clear Health Analysis Results"):
            del st.session_state.health_results
            st.rerun()
