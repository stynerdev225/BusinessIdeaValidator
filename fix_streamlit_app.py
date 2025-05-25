#!/usr/bin/env python3
"""
Script that directly fixes problematic sections in the Streamlit app.
"""

def main():
    # Create a new fixed file
    with open('/Users/stynerstiner/Downloads/BusinessIdeaValidator/streamlit_app.py', 'r') as src_file:
        content = src_file.read()
    
    # Fix indentation for tab2, tab3, and tab4 sections, setting them properly within the results check
    fixed_content = """# Display results if available (inside main_tab1)
    if hasattr(st.session_state, "results") and st.session_state.results:
        results = st.session_state.results
        
        # Create two columns for the score and summary
        col1, col2 = st.columns([1, 3])
        
        # Display the overall score
        with col1:
            st.metric(
                "Overall Score",
                f"{results['overall_score']}/100",
                delta=None
            )
        
        # Add a verdict based on the score
        if results['overall_score'] >= 80:
            st.success("Strong validation")
        elif results['overall_score'] >= 60:
            st.info("Good validation")
        elif results['overall_score'] >= 40:
            st.warning("Mixed validation")
        else:
            st.error("Poor validation")
    
        # Display the summary
        with col2:
            st.subheader("Summary")
            st.write(results['market_validation_summary'])
        
        # Add space between sections
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create tabs for different sections with custom styling
        st.markdown(\"\"\"
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f0f2f6;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1E88E5 !important;
            color: white !important;
        }
        </style>
        \"\"\", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Pain Points & Solutions", "Opportunities", "Platform Insights", "Recommendations"])
        
        with tab1:
            # Create two columns for pain points and solutions
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(\"\"\"
                <div style="background-color:#f8d7da; padding:10px; border-radius:5px; margin-bottom:10px;">
                    <h3 style="color:#721c24; margin:0;">Key Pain Points</h3>
                </div>
                \"\"\", unsafe_allow_html=True)
                
                if results['key_pain_points'][0] != "Analysis failed":
                    for point in results['key_pain_points']:
                        st.markdown(f\"\"\"
                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                            <p style="margin:0;">🔍 {point}</p>
                        </div>
                        \"\"\", unsafe_allow_html=True)
                else:
                    st.markdown(\"\"\"
                    <div style="background-color:white; padding:15px; border-radius:5px; margin-bottom:10px; text-align:center;">
                        <p style="color:#6c757d; font-style:italic;">No clear pain points identified</p>
                    </div>
                    \"\"\", unsafe_allow_html=True)
            
            with col2:
                st.markdown(\"\"\"
                <div style="background-color:#d1ecf1; padding:10px; border-radius:5px; margin-bottom:10px;">
                    <h3 style="color:#0c5460; margin:0;">Existing Solutions</h3>
                </div>
                \"\"\", unsafe_allow_html=True)
                
                if results['existing_solutions'][0] != "Analysis failed":
                    for solution in results['existing_solutions']:
                        st.markdown(f\"\"\"
                        <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                            <p style="margin:0;">💡 {solution}</p>
                        </div>
                        \"\"\", unsafe_allow_html=True)
                else:
                    st.markdown(\"\"\"
                    <div style="background-color:white; padding:15px; border-radius:5px; margin-bottom:10px; text-align:center;">
                        <p style="color:#6c757d; font-style:italic;">No existing solutions identified</p>
                    </div>
                    \"\"\", unsafe_allow_html=True)
        
        with tab2:
            st.markdown(\"\"\"
            <div style="background-color:#d4edda; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3 style="color:#155724; margin:0;">Market Opportunities</h3>
            </div>
            \"\"\", unsafe_allow_html=True)
            
            if results['market_opportunities'][0] != "Analysis failed":
                for opportunity in results['market_opportunities']:
                    st.markdown(f\"\"\"
                    <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                        <p style="margin:0;">🚀 {opportunity}</p>
                    </div>
                    \"\"\", unsafe_allow_html=True)
            else:
                st.markdown(\"\"\"
                <div style="background-color:white; padding:15px; border-radius:5px; margin-bottom:10px; text-align:center;">
                    <p style="color:#6c757d; font-style:italic;">No clear market opportunities identified</p>
                </div>
                \"\"\", unsafe_allow_html=True)
        
        with tab3:
            st.markdown(\"\"\"
            <div style="background-color:#fff3cd; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3 style="color:#856404; margin:0;">Platform Insights</h3>
            </div>
            \"\"\", unsafe_allow_html=True)
            
            for platform in results['platform_insights']:
                platform_name = platform['platform']
                platform_icon = "📰" if platform_name == "HackerNews" else "🔄" if platform_name == "Reddit" else "📊"
                
                st.markdown(f\"\"\"
                <div style="background-color:white; padding:15px; border-radius:5px; margin-bottom:15px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                    <h4 style="color:#495057; margin-top:0;">{platform_icon} {platform_name} Insights</h4>
                    <p style="margin-bottom:0;">{platform['insights']}</p>
                </div>
                \"\"\", unsafe_allow_html=True)
        
        with tab4:
            st.markdown(\"\"\"
            <div style="background-color:#e2e3e5; padding:10px; border-radius:5px; margin-bottom:10px;">
                <h3 style="color:#383d41; margin:0;">Recommendations</h3>
            </div>
            \"\"\", unsafe_allow_html=True)
            
            if results['recommendations'][0] != "Analysis failed":
                for i, rec in enumerate(results['recommendations']):
                    st.markdown(f\"\"\"
                    <div style="background-color:white; padding:12px; border-radius:5px; margin-bottom:8px; box-shadow:0 1px 2px rgba(0,0,0,0.1);">
                        <p style="margin:0;"><b>#{i+1}:</b> ✅ {rec}</p>
                    </div>
                    \"\"\", unsafe_allow_html=True)
            else:
                st.markdown(\"\"\"
                <div style="background-color:white; padding:15px; border-radius:5px; margin-bottom:10px; text-align:center;">
                    <p style="color:#6c757d; font-style:italic;">No recommendations available</p>
                </div>
                \"\"\", unsafe_allow_html=True)"""

    # First we look for the problematic section
    start_marker = "# Display results if available (inside main_tab1)"
    end_marker = "# Load previous validation if selected (inside main_tab1)"
    
    # Find the start and end positions of the section to replace
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos != -1 and end_pos != -1:
        # Replace the problematic section
        new_content = content[:start_pos] + fixed_content + "\n\n    " + content[end_pos:]
        
        # Write the fixed content back to the file
        with open('/Users/stynerstiner/Downloads/BusinessIdeaValidator/streamlit_app.py', 'w') as dest_file:
            dest_file.write(new_content)
        
        print("Successfully fixed tab structure in streamlit_app.py")
    else:
        print("Could not find the section to replace")

if __name__ == "__main__":
    main()
