#!/usr/bin/env python3
"""
Quick fix for Streamlit display issues.
This script restarts the Streamlit app to clear any cache issues.
"""
import subprocess
import sys
import time
import signal
import os

def restart_streamlit():
    """Restart the Streamlit application."""
    print("🔄 Restarting Streamlit app to apply fixes...")
    
    try:
        # Find Streamlit processes
        result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n')
        
        # Kill existing Streamlit processes
        for pid in pids:
            if pid:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Terminated Streamlit process {pid}")
                except ProcessLookupError:
                    pass
        
        time.sleep(2)
        
        # Start new Streamlit process
        print("🚀 Starting Streamlit app with fixes...")
        os.chdir('/Users/stynerstiner/Downloads/BusinessIdeaValidator')
        
        # Start streamlit in background
        subprocess.Popen(['streamlit', 'run', 'streamlit_app.py', '--server.port=8501'])
        
        print("✅ Streamlit app restarted successfully!")
        print("🌐 App available at: http://localhost:8501")
        
    except Exception as e:
        print(f"❌ Error restarting Streamlit: {e}")
        print("Please manually restart with: streamlit run streamlit_app.py")

if __name__ == "__main__":
    restart_streamlit()
