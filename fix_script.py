#!/usr/bin/env python3
"""
Streamlit app fixer script that corrects indentation and structure issues.
"""
import re

def fix_streamlit_app():
    # Read the original file
    with open('/Users/stynerstiner/Downloads/BusinessIdeaValidator/streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Change the indentation of the tab2 section
    # Find the section after the "tab1" with "with col2:" ending
    content = re.sub(
        r'(with col2:.*?""", unsafe_allow_html=True\))\s+with tab2:',
        r'\1\n        with tab2:',
        content, 
        flags=re.DOTALL
    )
    
    # Fix 2: Fix the indentation for tab3 and tab4
    content = re.sub(
        r'with tab2:.*?""", unsafe_allow_html=True\))\s+with tab3:',
        r'with tab2:.*?""", unsafe_allow_html=True))\n        with tab3:',
        content, 
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'with tab3:.*?""", unsafe_allow_html=True\))\s+with tab4:',
        r'with tab3:.*?""", unsafe_allow_html=True))\n        with tab4:',
        content, 
        flags=re.DOTALL
    )
    
    # Fix 3: Make sure tab2, tab3, and tab4 are indented correctly
    # This pattern looks for "with tab2:" at the start of a line and adds proper indentation
    content = content.replace('\nwith tab2:', '\n        with tab2:')
    content = content.replace('\nwith tab3:', '\n        with tab3:')
    content = content.replace('\nwith tab4:', '\n        with tab4:')
    
    # Write the corrected file
    with open('/Users/stynerstiner/Downloads/BusinessIdeaValidator/streamlit_app.fixed.py', 'w') as f:
        f.write(content)
    
    print("Fixed file written to streamlit_app.fixed.py")

if __name__ == "__main__":
    fix_streamlit_app()
