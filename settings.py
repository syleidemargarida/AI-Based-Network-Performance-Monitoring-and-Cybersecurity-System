import os
from datetime import datetime

class Config:
    # Data settings
    DATA_DIR = "data"
    MODEL_DIR = "model"
    LOGS_DIR = "logs"
    STATIC_DIR = "static"
    
    # ML Model settings
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    ANOMALY_THRESHOLD = 0.1
    
    # Feature columns for network traffic analysis (CICIDS2017 dataset)
    NUMERIC_FEATURES = [
        'Flow Duration', 'Total Fwd Packet', 'Total Bwd packets',
        'Total Length of Fwd Packet', 'Total Length of Bwd Packet',
        'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean',
        'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean',
        'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std',
        'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Mean', 'Fwd IAT Std',
        'Fwd IAT Max', 'Fwd IAT Min', 'Bwd IAT Mean', 'Bwd IAT Std',
        'Bwd IAT Max', 'Bwd IAT Min', 'Active Mean', 'Active Std',
        'Active Max', 'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
    ]
    
    # Attack types (CICIDS2017 dataset)
    ATTACK_TYPES = {
        'BENIGN': 'Normal Traffic',
        'DDoS': 'Distributed Denial of Service',
        'Portscan': 'Port Scanning Attack',
        'Bot': 'Botnet Attack',
        'Infiltration': 'Infiltration Attack',
        'Web Attack': 'Web-based Attack',
        'Brute Force': 'Brute Force Attack',
        'DoS': 'Denial of Service',
        'FTP-BruteForce': 'FTP Brute Force',
        'SSH-BruteForce': 'SSH Brute Force',
        'Heartbleed': 'Heartbleed Attack',
        'SQL Injection': 'SQL Injection Attack'
    }
    
    # Alert severity levels
    ALERT_LEVELS = {
        'LOW': '#28a745',
        'MEDIUM': '#ffc107', 
        'HIGH': '#fd7e14',
        'CRITICAL': '#dc3545'
    }
    
    # Dashboard settings
    REFRESH_INTERVAL = 5000  # milliseconds
    MAX_DISPLAY_ROWS = 100
    
    # Security settings
    SESSION_TIMEOUT = 3600  # seconds
    
    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def ensure_directories():
        """Create necessary directories if they don't exist"""
        dirs = [Config.DATA_DIR, Config.MODEL_DIR, Config.LOGS_DIR, Config.STATIC_DIR]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
