#!/usr/bin/env python3
"""
AI Network Security Monitor - Startup Script
This script initializes the system and launches the Streamlit dashboard
"""

import os
import sys
import subprocess
from config.settings import Config

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import streamlit
        import pandas
        import numpy
        import sklearn
        import plotly
        import matplotlib
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def initialize_system():
    """Initialize the system directories and configuration"""
    print("🚀 Initializing AI Network Security Monitor...")
    
    # Create necessary directories
    Config.ensure_directories()
    print("✅ Directories created/verified")
    
    # Check if sample data exists
    sample_data_path = os.path.join(Config.DATA_DIR, "sample_network_data.csv")
    if os.path.exists(sample_data_path):
        print(f"✅ Sample data found at {sample_data_path}")
    else:
        print("⚠️ Sample data not found")
    
    print("✅ System initialization complete")

def main():
    """Main function to run the application"""
    print("=" * 60)
    print("🛡️  AI Network Security Monitor")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize system
    initialize_system()
    
    # Launch Streamlit app
    print("\n🌐 Launching Streamlit Dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the server")
    print("\n" + "=" * 60)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
