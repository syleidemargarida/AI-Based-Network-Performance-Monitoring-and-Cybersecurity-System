#!/usr/bin/env python3
"""
Test script to verify the AI Network Security Monitor works with CICIDS2017 dataset
"""

import os
import sys

def test_basic_imports():
    """Test if basic modules can be imported"""
    print("Testing basic imports...")
    try:
        import pandas as pd
        import numpy as np
        print("  pandas and numpy: OK")
    except ImportError as e:
        print(f"  pandas/numpy import failed: {e}")
        return False
    
    try:
        import sklearn
        print("  scikit-learn: OK")
    except ImportError as e:
        print(f"  scikit-learn import failed: {e}")
        return False
    
    try:
        import plotly
        print("  plotly: OK")
    except ImportError as e:
        print(f"  plotly import failed: {e}")
        return False
    
    return True

def test_dataset_access():
    """Test if dataset files are accessible"""
    print("\nTesting dataset access...")
    
    data_files = [
        'data/monday.csv',
        'data/friday.csv', 
        'data/tuesday.csv',
        'data/wednesday.csv',
        'data/thursday.csv'
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024*1024)
            print(f"  {file_path}: OK ({size_mb:.1f} MB)")
        else:
            print(f"  {file_path}: NOT FOUND")
            return False
    
    return True

def test_config_loading():
    """Test if configuration loads correctly"""
    print("\nTesting configuration...")
    try:
        from config.settings import Config
        print(f"  NUMERIC_FEATURES: {len(Config.NUMERIC_FEATURES)} features")
        print(f"  ATTACK_TYPES: {len(Config.ATTACK_TYPES)} types")
        print("  Configuration: OK")
        return True
    except ImportError as e:
        print(f"  Configuration import failed: {e}")
        return False

def test_data_loading():
    """Test loading a small sample of the dataset"""
    print("\nTesting data loading...")
    try:
        import pandas as pd
        
        # Load first 100 rows of monday.csv
        df = pd.read_csv('data/monday.csv', nrows=100)
        print(f"  Loaded {len(df)} rows")
        print(f"  Columns: {len(df.columns)}")
        
        # Check for required columns
        required_cols = ['Flow Duration', 'Label']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"  Missing columns: {missing_cols}")
            return False
        
        # Check labels
        unique_labels = df['Label'].unique()
        print(f"  Labels found: {unique_labels}")
        
        print("  Data loading: OK")
        return True
        
    except Exception as e:
        print(f"  Data loading failed: {e}")
        return False

def test_custom_modules():
    """Test custom module imports"""
    print("\nTesting custom modules...")
    try:
        from utils import DataProcessor, AlertManager
        print("  utils module: OK")
        
        from main import NetworkSecurityModel
        print("  main module: OK")
        
        return True
    except ImportError as e:
        print(f"  Custom module import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Network Security Monitor - System Test")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_dataset_access,
        test_config_loading,
        test_data_loading,
        test_custom_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("  TEST FAILED")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Install missing dependencies if any")
        print("2. Run: streamlit run app.py")
        print("3. Open browser to: http://localhost:8501")
    else:
        print("Some tests failed. Please check the errors above.")
        print("Run: pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
