import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from datetime import datetime
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(Config.LOGS_DIR, 'system.log')),
        logging.StreamHandler()
    ]
)

class DataProcessor:
    """Utility class for data processing and analysis"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = Config.NUMERIC_FEATURES
        
    def load_data(self, file_path):
        """Load and preprocess network traffic data"""
        try:
            logging.info(f"Loading data from {file_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                    elif file_path.endswith('.parquet'):
                        df = pd.read_parquet(file_path)
                    else:
                        raise ValueError("Unsupported file format. Please use CSV or Parquet.")
                    
                    logging.info(f"Data loaded successfully with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not read file with any supported encoding")
            
            # Clean column names
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.replace('/', '_')
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            # Convert numeric columns
            df = self._convert_numeric_columns(df)
            
            logging.info(f"Data shape: {df.shape}")
            return df
            
        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            raise
    
    def _handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        # Replace infinite values with NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Fill missing values for numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        # Fill missing values for categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
        
        return df
    
    def _convert_numeric_columns(self, df):
        """Convert columns to numeric where possible"""
        for col in df.columns:
            if col in self.feature_columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    logging.warning(f"Could not convert column {col} to numeric")
        
        return df
    
    def prepare_features(self, df, target_column='Label'):
        """Prepare features for ML model training"""
        # Filter to only available columns
        available_features = [col for col in self.feature_columns if col in df.columns]
        
        if not available_features:
            raise ValueError("No valid feature columns found in the dataset")
        
        X = df[available_features].copy()
        
        # Handle any remaining missing values
        X = X.fillna(X.median())
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=available_features)
        
        # Prepare target variable
        y = None
        if target_column in df.columns:
            y = df[target_column].copy()
            # Convert to binary classification (Benign vs Attack)
            y = y.apply(lambda x: 'Benign' if str(x).lower() in ['benign', 'normal', 'legitimate'] else 'Attack')
        
        return X_scaled, y, available_features
    
    def create_visualizations(self, df):
        """Create various visualizations for network analysis"""
        figures = {}
        
        # 1. Traffic Distribution
        if 'Label' in df.columns:
            label_counts = df['Label'].value_counts()
            fig1 = px.pie(
                values=label_counts.values,
                names=label_counts.index,
                title="Traffic Distribution (Normal vs Attack)",
                color_discrete_sequence=['#2E8B57', '#DC143C']
            )
            figures['traffic_dist'] = fig1
        
        # 2. Network Performance Metrics
        numeric_cols = ['Flow_Duration', 'Flow_Bytes_s', 'Flow_Packets_s']
        available_metrics = [col for col in numeric_cols if col in df.columns]
        
        if available_metrics:
            fig2 = make_subplots(
                rows=1, cols=len(available_metrics),
                subplot_titles=available_metrics,
                specs=[[{"type": "histogram"}] * len(available_metrics)]
            )
            
            for i, col in enumerate(available_metrics, 1):
                fig2.add_histogram(
                    x=df[col],
                    nbinsx=30,
                    name=col.replace('_', ' ').title(),
                    row=1, col=i
                )
            
            fig2.update_layout(
                title="Network Performance Metrics Distribution",
                showlegend=False,
                height=400
            )
            figures['performance_metrics'] = fig2
        
        # 3. Timeline Analysis (if timestamp data available)
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            timeline_data = df.groupby(df['Timestamp'].dt.hour)['Label'].value_counts().unstack(fill_value=0)
            
            fig3 = go.Figure()
            for col in timeline_data.columns:
                fig3.add_trace(go.Scatter(
                    x=timeline_data.index,
                    y=timeline_data[col],
                    mode='lines+markers',
                    name=col
                ))
            
            fig3.update_layout(
                title="Traffic Timeline Analysis",
                xaxis_title="Hour of Day",
                yaxis_title="Number of Connections"
            )
            figures['timeline'] = fig3
        
        return figures
    
    def calculate_network_stats(self, df):
        """Calculate network performance statistics"""
        stats = {}
        
        # Basic statistics
        stats['total_connections'] = len(df)
        stats['unique_sources'] = df['Source_IP'].nunique() if 'Source_IP' in df.columns else 'N/A'
        stats['unique_destinations'] = df['Destination_IP'].nunique() if 'Destination_IP' in df.columns else 'N/A'
        
        # Performance metrics
        if 'Flow_Duration' in df.columns:
            stats['avg_duration'] = df['Flow_Duration'].mean()
            stats['max_duration'] = df['Flow_Duration'].max()
        
        if 'Flow_Bytes_s' in df.columns:
            stats['avg_throughput'] = df['Flow_Bytes_s'].mean()
            stats['max_throughput'] = df['Flow_Bytes_s'].max()
        
        if 'Flow_Packets_s' in df.columns:
            stats['avg_packet_rate'] = df['Flow_Packets_s'].mean()
        
        # Attack statistics
        if 'Label' in df.columns:
            attack_data = df[df['Label'] != 'Benign'] if 'Benign' in df['Label'].values else df[df['Label'] != 'Normal']
            stats['total_attacks'] = len(attack_data)
            stats['attack_percentage'] = (len(attack_data) / len(df)) * 100
        
        return stats

class AlertManager:
    """Manages security alerts and notifications"""
    
    def __init__(self):
        self.alerts = []
        self.alert_file = os.path.join(Config.LOGS_DIR, 'alerts.log')
    
    def add_alert(self, level, message, source="System", details=None):
        """Add a new security alert"""
        alert = {
            'timestamp': Config.get_timestamp(),
            'level': level,
            'message': message,
            'source': source,
            'details': details or {}
        }
        
        self.alerts.append(alert)
        
        # Log alert to file
        with open(self.alert_file, 'a') as f:
            f.write(f"{alert['timestamp']} - {level} - {message} - Source: {source}\n")
        
        logging.warning(f"ALERT: {level} - {message}")
        
        # Keep only last 1000 alerts in memory
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    def get_recent_alerts(self, limit=50):
        """Get recent alerts"""
        return self.alerts[-limit:] if self.alerts else []
    
    def get_alert_summary(self):
        """Get summary of alerts by level"""
        if not self.alerts:
            return {}
        
        summary = {}
        for alert in self.alerts:
            level = alert['level']
            summary[level] = summary.get(level, 0) + 1
        
        return summary

def export_report(df, model_results, alerts, filename=None):
    """Export analysis report to CSV"""
    if filename is None:
        filename = f"network_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    filepath = os.path.join(Config.STATIC_DIR, filename)
    
    # Create summary data
    report_data = {
        'Metric': [
            'Total Connections',
            'Attack Connections',
            'Normal Connections',
            'Attack Percentage',
            'Model Accuracy',
            'Model Precision',
            'Model Recall',
            'Total Alerts',
            'Critical Alerts',
            'High Alerts'
        ],
        'Value': [
            len(df),
            len(df[df['Label'] != 'Benign']) if 'Label' in df.columns else 0,
            len(df[df['Label'] == 'Benign']) if 'Label' in df.columns else len(df),
            (len(df[df['Label'] != 'Benign']) / len(df) * 100) if 'Label' in df.columns else 0,
            model_results.get('accuracy', 0) * 100,
            model_results.get('precision', 0) * 100,
            model_results.get('recall', 0) * 100,
            len(alerts),
            len([a for a in alerts if a['level'] == 'CRITICAL']),
            len([a for a in alerts if a['level'] == 'HIGH'])
        ]
    }
    
    report_df = pd.DataFrame(report_data)
    report_df.to_csv(filepath, index=False)
    
    logging.info(f"Report exported to {filepath}")
    return filepath
