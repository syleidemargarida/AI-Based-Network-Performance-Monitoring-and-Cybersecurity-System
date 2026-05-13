import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
from datetime import datetime
import base64
from io import BytesIO

# Import our custom modules
from main import NetworkSecurityModel, simulate_real_time_data
from utils import DataProcessor, AlertManager, export_report
from config.settings import Config

# Set page configuration
st.set_page_config(
    page_title="AI Network Security Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Apply custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-medium {
        background-color: #ff8800;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-low {
        background-color: #00C851;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .stButton>button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #764ba2, #667eea);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = NetworkSecurityModel()
if 'data' not in st.session_state:
    st.session_state.data = None
if 'trained' not in st.session_state:
    st.session_state.trained = False
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

def main():
    # Header
    st.markdown('<h1 class="main-header"> AI Network Security Monitor</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header(" Control Panel")
        
        # Data Source Selection
        st.subheader("Data Source")
        data_source = st.radio(
            "Choose Data Source:",
            ["Upload Dataset", "Generate Sample Data", "Use Real-time Simulation"]
        )
        
        if data_source == "Upload Dataset":
            uploaded_file = st.file_uploader(
                "Upload Network Traffic Data (CSV)",
                type=['csv']
            )
            
            if uploaded_file is not None:
                with st.spinner("Loading data..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = os.path.join("data", "temp_upload.csv")
                        os.makedirs("data", exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Load data
                        st.session_state.data = st.session_state.model.data_processor.load_data(temp_path)
                        st.success(f" Data loaded successfully! Shape: {st.session_state.data.shape}")
                        
                        # Show data preview
                        st.subheader("Data Preview")
                        st.dataframe(st.session_state.data.head())
                        
                    except Exception as e:
                        st.error(f" Error loading data: {str(e)}")
        
        elif data_source == "Generate Sample Data":
            num_samples = st.slider("Number of Samples", 100, 10000, 1000)
            attack_ratio = st.slider("Attack Ratio (%)", 5, 30, 10) / 100
            
            if st.button("Generate Sample Data"):
                with st.spinner("Generating sample data..."):
                    st.session_state.data = simulate_real_time_data(num_samples, attack_ratio)
                    st.success(f" Generated {num_samples} samples with {attack_ratio*100:.1f}% attacks")
                    st.dataframe(st.session_state.data.head())
        
        elif data_source == "Use Real-time Simulation":
            st.info("Real-time simulation will start automatically when models are trained")
            if st.button("Start Real-time Monitoring"):
                if st.session_state.trained:
                    start_real_time_monitoring()
                else:
                    st.warning(" Please train models first!")
    
    # Main content area
    if st.session_state.data is not None:
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            " Data Overview", 
            " Model Training", 
            " Threat Detection", 
            " Performance Analysis",
            " Security Alerts",
            " Reports"
        ])
        
        with tab1:
            show_data_overview()
        
        with tab2:
            show_model_training()
        
        with tab3:
            show_threat_detection()
        
        with tab4:
            show_performance_analysis()
        
        with tab5:
            show_security_alerts()
        
        with tab6:
            show_reports()
    else:
        # Welcome screen
        st.markdown("""
        ##  Welcome to AI Network Security Monitor
        
        This intelligent system uses Artificial Intelligence to:
        -  Monitor network performance in real-time
        -  Detect cybersecurity threats and anomalies
        -  Provide comprehensive visualization and analysis
        -  Generate intelligent security alerts
        
        ###  Getting Started:
        1. **Upload your dataset** or generate sample data from the sidebar
        2. **Train AI models** using our advanced ML algorithms
        3. **Monitor threats** in real-time with intelligent detection
        4. **Analyze performance** metrics and network health
        5. **Export reports** for documentation and compliance
        
        ###  Supported Features:
        - **Multiple ML Models**: Random Forest, SVM, Isolation Forest
        - **Real-time Detection**: Continuous monitoring and alerting
        - **Comprehensive Analytics**: Network performance and security metrics
        - **Interactive Dashboard**: Beautiful visualizations and insights
        - **Export Capabilities**: Generate detailed reports
        
        ---
        **Start by uploading your network traffic data or generating sample data from the sidebar!**
        """)

def show_data_overview():
    st.header(" Data Overview & Analysis")
    
    if st.session_state.data is None:
        st.warning(" No data loaded. Please upload or generate data first.")
        return
    
    df = st.session_state.data
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Connections", f"{len(df):,}")
    
    with col2:
        if 'Label' in df.columns:
            attack_count = len(df[df['Label'] != 'Benign']) if 'Benign' in df['Label'].values else len(df[df['Label'] != 'Normal'])
            st.metric("Attack Connections", f"{attack_count:,}")
        else:
            st.metric("Attack Connections", "N/A")
    
    with col3:
        if 'Source_IP' in df.columns:
            unique_sources = df['Source_IP'].nunique()
            st.metric("Unique Sources", f"{unique_sources:,}")
        else:
            st.metric("Unique Sources", "N/A")
    
    with col4:
        if 'Destination_IP' in df.columns:
            unique_dests = df['Destination_IP'].nunique()
            st.metric("Unique Destinations", f"{unique_dests:,}")
        else:
            st.metric("Unique Destinations", "N/A")
    
    # Data Statistics
    st.subheader(" Data Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Dataset Info:**")
        st.write(f"- Shape: {df.shape}")
        st.write(f"- Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        st.write(f"- Missing Values: {df.isnull().sum().sum()}")
        
        # Data types
        st.write("**Data Types:**")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            st.write(f"- {dtype}: {count} columns")
    
    with col2:
        # Traffic distribution
        if 'Label' in df.columns:
            st.write("**Traffic Distribution:**")
            label_counts = df['Label'].value_counts()
            for label, count in label_counts.items():
                percentage = (count / len(df)) * 100
                st.write(f"- {label}: {count:,} ({percentage:.1f}%)")
    
    # Visualizations
    st.subheader(" Visualizations")
    
    figures = st.session_state.model.data_processor.create_visualizations(df)
    
    if figures:
        for name, fig in figures.items():
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(" No visualizations available. Ensure your dataset has required columns.")
    
    # Data Preview
    st.subheader(" Data Preview")
    
    # Column selection for display
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to display:",
        all_columns,
        default=all_columns[:10] if len(all_columns) > 10 else all_columns
    )
    
    if selected_columns:
        st.dataframe(df[selected_columns].head(100))
    else:
        st.dataframe(df.head(100))

def show_model_training():
    st.header(" Model Training & Evaluation")
    
    if st.session_state.data is None:
        st.warning(" No data loaded. Please upload or generate data first.")
        return
    
    # Model Selection
    st.subheader("Select Models to Train")
    
    col1, col2 = st.columns(2)
    
    with col1:
        train_classification = st.checkbox("Train Classification Model", value=True)
        if train_classification:
            model_type = st.selectbox(
                "Classification Algorithm:",
                ["random_forest", "svm"],
                index=0
            )
    
    with col2:
        train_anomaly = st.checkbox("Train Anomaly Detection", value=True)
        if train_anomaly:
            contamination = st.slider(
                "Anomaly Contamination Rate",
                0.01, 0.3, 0.1, 0.01
            )
    
    # Training button
    if st.button(" Start Training", type="primary"):
        with st.spinner("Training models... This may take a few minutes."):
            try:
                # Train classification model
                if train_classification:
                    st.write(" Training Classification Model...")
                    Config.ANOMALY_THRESHOLD = contamination
                    class_metrics = st.session_state.model.train_classification_model(
                        st.session_state.data, model_type
                    )
                    
                    st.success(" Classification Model Trained Successfully!")
                    
                    # Display metrics
                    st.subheader(" Classification Model Performance")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Accuracy", f"{class_metrics['accuracy']:.4f}")
                    with col2:
                        st.metric("Precision", f"{class_metrics['precision']:.4f}")
                    with col3:
                        st.metric("Recall", f"{class_metrics['recall']:.4f}")
                    with col4:
                        st.metric("F1-Score", f"{class_metrics['f1_score']:.4f}")
                    
                    # Cross-validation
                    st.write(f"Cross-validation Score: {class_metrics['cv_mean']:.4f} ± {class_metrics['cv_std']:.4f}")
                    
                    # Feature importance
                    if 'feature_importance' in class_metrics and class_metrics['feature_importance']:
                        st.subheader(" Feature Importance")
                        importance_df = pd.DataFrame(
                            list(class_metrics['feature_importance'].items()),
                            columns=['Feature', 'Importance']
                        ).sort_values('Importance', ascending=False).head(10)
                        
                        fig = px.bar(
                            importance_df,
                            x='Importance',
                            y='Feature',
                            orientation='h',
                            title="Top 10 Important Features"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Train anomaly detection model
                if train_anomaly:
                    st.write(" Training Anomaly Detection Model...")
                    anomaly_metrics = st.session_state.model.train_anomaly_detection(
                        st.session_state.data
                    )
                    
                    st.success(" Anomaly Detection Model Trained Successfully!")
                    
                    # Display metrics
                    st.subheader(" Anomaly Detection Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Samples", f"{anomaly_metrics['total_samples']:,}")
                    with col2:
                        st.metric("Anomalies Detected", f"{anomaly_metrics['anomaly_count']:,}")
                    with col3:
                        st.metric("Anomaly Percentage", f"{anomaly_metrics['anomaly_percentage']:.2f}%")
                
                st.session_state.trained = True
                st.success("🎉 All models trained successfully!")
                st.balloons()
                
            except Exception as e:
                st.error(f" Training failed: {str(e)}")
    
    # Model status
    if st.session_state.trained:
        st.subheader(" Model Status")
        st.write("🟢 Classification Model: Trained")
        st.write("🟢 Anomaly Detection Model: Trained")
        
        # Test models
        if st.button("🧪 Test Models"):
            test_models()

def test_models():
    """Test trained models with sample data"""
    if not st.session_state.trained:
        st.warning("⚠️ Models not trained yet!")
        return
    
    st.subheader(" Model Testing")
    
    # Generate test data
    test_data = simulate_real_time_data(100, 0.2)
    
    # Test classification
    try:
        X_test, _, _ = st.session_state.model.data_processor.prepare_features(test_data)
        
        if st.session_state.model.classification_model is not None:
            predictions = st.session_state.model.classification_model.predict(X_test)
            probabilities = st.session_state.model.classification_model.predict_proba(X_test)
            
            # Results
            results_df = pd.DataFrame({
                'Prediction': predictions,
                'Attack_Probability': probabilities[:, 1],
                'Actual': test_data['Label']
            })
            
            st.write("**Classification Results:**")
            st.dataframe(results_df.head(10))
            
            # Accuracy on test set
            accuracy = (results_df['Prediction'] == results_df['Actual']).mean()
            st.metric("Test Accuracy", f"{accuracy:.4f}")
        
        if st.session_state.model.anomaly_model is not None:
            anomaly_predictions = st.session_state.model.anomaly_model.predict(X_test)
            anomaly_scores = st.session_state.model.anomaly_model.decision_function(X_test)
            
            # Results
            anomaly_results = pd.DataFrame({
                'Anomaly_Prediction': anomaly_predictions,
                'Anomaly_Score': anomaly_scores
            })
            
            st.write("**Anomaly Detection Results:**")
            st.dataframe(anomaly_results.head(10))
            
            anomaly_count = np.sum(anomaly_predictions == -1)
            st.metric("Anomalies Detected", f"{anomaly_count} out of {len(test_data)}")
            
    except Exception as e:
        st.error(f"❌ Testing failed: {str(e)}")

def show_threat_detection():
    st.header("🔍 Threat Detection & Analysis")
    
    if not st.session_state.trained:
        st.warning("⚠️ Please train models first!")
        return
    
    # Real-time detection
    st.subheader(" Real-time Threat Detection")
    
    if st.button(" Scan for Threats"):
        with st.spinner("Analyzing network traffic for threats..."):
            try:
                threats = st.session_state.model.detect_threats(st.session_state.data)
                
                st.success(f"✅ Scan complete! Found {len(threats)} potential threats")
                
                if threats:
                    # Threat summary
                    st.subheader(" Threat Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        class_threats = len([t for t in threats if t['type'] == 'Classification'])
                        st.metric("Classification Threats", class_threats)
                    
                    with col2:
                        anomaly_threats = len([t for t in threats if t['type'] == 'Anomaly'])
                        st.metric("Anomaly Threats", anomaly_threats)
                    
                    with col3:
                        avg_confidence = np.mean([t.get('confidence', 0.5) for t in threats if 'confidence' in t])
                        st.metric("Avg Confidence", f"{avg_confidence:.3f}")
                    
                    # Threat details
                    st.subheader(" Threat Details")
                    
                    threat_df = pd.DataFrame(threats)
                    st.dataframe(threat_df)
                    
                    # Visualization
                    if len(threats) > 0:
                        # Threat type distribution
                        threat_types = [t['type'] for t in threats]
                        type_counts = pd.Series(threat_types).value_counts()
                        
                        fig = px.pie(
                            values=type_counts.values,
                            names=type_counts.index,
                            title="Threat Type Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Confidence distribution (for classification threats)
                        class_confidences = [t['confidence'] for t in threats if 'confidence' in t]
                        if class_confidences:
                            fig2 = px.histogram(
                                x=class_confidences,
                                nbins=20,
                                title="Threat Confidence Distribution",
                                labels={'x': 'Confidence', 'y': 'Count'}
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                
                else:
                    st.info(" No threats detected in the current dataset")
                    
            except Exception as e:
                st.error(f" Threat detection failed: {str(e)}")
    
    # Manual threat analysis
    st.subheader(" Manual Threat Analysis")
    
    if st.button(" Analyze Network Patterns"):
        with st.spinner("Analyzing network patterns..."):
            try:
                # Network pattern analysis
                df = st.session_state.data
                
                patterns = []
                
                # High traffic patterns
                if 'Flow_Bytes_s' in df.columns:
                    high_traffic = df[df['Flow_Bytes_s'] > df['Flow_Bytes_s'].quantile(0.95)]
                    if len(high_traffic) > 0:
                        patterns.append({
                            'type': 'High Traffic Volume',
                            'count': len(high_traffic),
                            'percentage': (len(high_traffic) / len(df)) * 100,
                            'severity': 'HIGH' if len(high_traffic) / len(df) > 0.05 else 'MEDIUM'
                        })
                
                # Long duration connections
                if 'Flow_Duration' in df.columns:
                    long_duration = df[df['Flow_Duration'] > df['Flow_Duration'].quantile(0.95)]
                    if len(long_duration) > 0:
                        patterns.append({
                            'type': 'Long Duration Connections',
                            'count': len(long_duration),
                            'percentage': (len(long_duration) / len(df)) * 100,
                            'severity': 'MEDIUM'
                        })
                
                # High packet rate
                if 'Flow_Packets_s' in df.columns:
                    high_packet_rate = df[df['Flow_Packets_s'] > df['Flow_Packets_s'].quantile(0.95)]
                    if len(high_packet_rate) > 0:
                        patterns.append({
                            'type': 'High Packet Rate',
                            'count': len(high_packet_rate),
                            'percentage': (len(high_packet_rate) / len(df)) * 100,
                            'severity': 'HIGH' if len(high_packet_rate) / len(df) > 0.03 else 'MEDIUM'
                        })
                
                if patterns:
                    st.write("**Suspicious Patterns Detected:**")
                    pattern_df = pd.DataFrame(patterns)
                    st.dataframe(pattern_df)
                    
                    # Create alerts for high-severity patterns
                    for pattern in patterns:
                        if pattern['severity'] == 'HIGH':
                            st.session_state.model.alert_manager.add_alert(
                                level='HIGH',
                                message=f"Suspicious pattern detected: {pattern['type']}",
                                source="Pattern Analysis",
                                details=pattern
                            )
                else:
                    st.info(" No suspicious patterns detected")
                    
            except Exception as e:
                st.error(f" Pattern analysis failed: {str(e)}")

def show_performance_analysis():
    st.header(" Network Performance Analysis")
    
    if st.session_state.data is None:
        st.warning(" No data loaded. Please upload or generate data first.")
        return
    
    df = st.session_state.data
    
    # Performance metrics
    st.subheader(" Network Performance Metrics")
    
    try:
        performance_stats = st.session_state.model.analyze_network_performance(df)
        
        # Display performance metrics
        if 'duration_stats' in performance_stats:
            st.write("**Connection Duration Statistics:**")
            duration_stats = performance_stats['duration_stats']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Duration", f"{duration_stats['mean']:.2f}")
            with col2:
                st.metric("Median Duration", f"{duration_stats['median']:.2f}")
            with col3:
                st.metric("Std Duration", f"{duration_stats['std']:.2f}")
            with col4:
                st.metric("Max Duration", f"{duration_stats['max']:.2f}")
        
        if 'throughput_stats' in performance_stats:
            st.write("**Throughput Statistics (Bytes/sec):**")
            throughput_stats = performance_stats['throughput_stats']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Throughput", f"{throughput_stats['mean']:.2f}")
            with col2:
                st.metric("Median Throughput", f"{throughput_stats['median']:.2f}")
            with col3:
                st.metric("Std Throughput", f"{throughput_stats['std']:.2f}")
            with col4:
                st.metric("Max Throughput", f"{throughput_stats['max']:.2f}")
        
        if 'packet_rate_stats' in performance_stats:
            st.write("**Packet Rate Statistics (Packets/sec):**")
            packet_stats = performance_stats['packet_rate_stats']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean Packet Rate", f"{packet_stats['mean']:.2f}")
            with col2:
                st.metric("Median Packet Rate", f"{packet_stats['median']:.2f}")
            with col3:
                st.metric("Max Packet Rate", f"{packet_stats['max']:.2f}")
        
        # Performance issues
        if performance_stats.get('issues'):
            st.subheader(" Performance Issues Detected")
            
            for issue in performance_stats['issues']:
                severity = '🔴' if issue['percentage'] > 15 else '🟡' if issue['percentage'] > 5 else '🟢'
                st.write(f"{severity} **{issue['type']}**: {issue['count']} connections ({issue['percentage']:.1f}%)")
        
        # Performance visualizations
        st.subheader(" Performance Visualizations")
        
        # Time series analysis
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            
            # Create time series plots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Duration Over Time', 'Throughput Over Time', 
                             'Packet Rate Over Time', 'Traffic Volume'],
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Duration plot
            if 'Flow_Duration' in df.columns:
                df_time = df.groupby(df['Timestamp'].dt.floor('1Min'))['Flow_Duration'].mean()
                fig.add_trace(
                    go.Scatter(x=df_time.index, y=df_time.values, name='Avg Duration'),
                    row=1, col=1
                )
            
            # Throughput plot
            if 'Flow_Bytes_s' in df.columns:
                df_time = df.groupby(df['Timestamp'].dt.floor('1Min'))['Flow_Bytes_s'].mean()
                fig.add_trace(
                    go.Scatter(x=df_time.index, y=df_time.values, name='Avg Throughput'),
                    row=1, col=2
                )
            
            # Packet rate plot
            if 'Flow_Packets_s' in df.columns:
                df_time = df.groupby(df['Timestamp'].dt.floor('1Min'))['Flow_Packets_s'].mean()
                fig.add_trace(
                    go.Scatter(x=df_time.index, y=df_time.values, name='Avg Packet Rate'),
                    row=2, col=1
                )
            
            # Traffic volume
            df_time = df.groupby(df['Timestamp'].dt.floor('1Min')).size()
            fig.add_trace(
                go.Scatter(x=df_time.index, y=df_time.values, name='Connection Count'),
                row=2, col=2
            )
            
            fig.update_layout(
                title="Network Performance Over Time",
                height=600,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Distribution plots
        numeric_cols = ['Flow_Duration', 'Flow_Bytes_s', 'Flow_Packets_s']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if available_cols:
            st.subheader("Performance Metric Distributions")
            
            fig = make_subplots(
                rows=1, cols=len(available_cols),
                subplot_titles=[col.replace('_', ' ').title() for col in available_cols]
            )
            
            for i, col in enumerate(available_cols, 1):
                fig.add_histogram(
                    x=df[col],
                    nbinsx=30,
                    name=col.replace('_', ' ').title(),
                    row=1, col=i
                )
            
            fig.update_layout(
                title="Performance Metric Distributions",
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Correlation analysis
        st.subheader(" Performance Correlation Analysis")
        
        if len(available_cols) > 1:
            correlation_df = df[available_cols].corr()
            
            fig = px.imshow(
                correlation_df,
                text_auto=True,
                aspect="auto",
                title="Performance Metrics Correlation Matrix"
            )
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f" Performance analysis failed: {str(e)}")

def show_security_alerts():
    st.header(" Security Alerts & Notifications")
    
    # Alert statistics
    alerts = st.session_state.model.alert_manager.get_recent_alerts(100)
    alert_summary = st.session_state.model.alert_manager.get_alert_summary()
    
    # Alert summary cards
    st.subheader(" Alert Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_alerts = len(alerts)
        st.metric("Total Alerts", total_alerts)
    
    with col2:
        critical_alerts = alert_summary.get('CRITICAL', 0)
        st.metric("Critical", critical_alerts, delta=f"{'🔴' if critical_alerts > 0 else '✅'}")
    
    with col3:
        high_alerts = alert_summary.get('HIGH', 0)
        st.metric("High", high_alerts, delta=f"{'🟠' if high_alerts > 0 else '✅'}")
    
    with col4:
        medium_alerts = alert_summary.get('MEDIUM', 0)
        st.metric("Medium", medium_alerts)
    
    # Alert level distribution
    if alert_summary:
        st.subheader("📈 Alert Distribution")
        
        alert_levels = list(alert_summary.keys())
        alert_counts = list(alert_summary.values())
        colors = [Config.ALERT_LEVELS.get(level, '#6c757d') for level in alert_levels]
        
        fig = px.bar(
            x=alert_levels,
            y=alert_counts,
            color=alert_levels,
            color_discrete_map=Config.ALERT_LEVELS,
            title="Alerts by Severity Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent alerts
    st.subheader("Recent Alerts")
    
    if alerts:
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            level_filter = st.selectbox(
                "Filter by Level:",
                ["All"] + list(Config.ALERT_LEVELS.keys())
            )
        
        with col2:
            source_filter = st.selectbox(
                "Filter by Source:",
                ["All"] + list(set([alert['source'] for alert in alerts]))
            )
        
        # Apply filters
        filtered_alerts = alerts
        
        if level_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if a['level'] == level_filter]
        
        if source_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if a['source'] == source_filter]
        
        # Display alerts
        for alert in reversed(filtered_alerts[-20:]):  # Show last 20 alerts
            alert_class = f"alert-{alert['level'].lower()}"
            
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{alert['level']}</strong> - {alert['timestamp']}<br>
                <strong>Source:</strong> {alert['source']}<br>
                <strong>Message:</strong> {alert['message']}
            </div>
            """, unsafe_allow_html=True)
        
        # Alert details expansion
        if st.button(" Show Alert Details"):
            alert_details_df = pd.DataFrame(filtered_alerts)
            st.dataframe(alert_details_df)
    
    else:
        st.info(" No security alerts detected")
    
    # Alert management
    st.subheader("🔧 Alert Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Alerts"):
            st.session_state.model.alert_manager.alerts = []
            st.success(" All alerts cleared")
            st.experimental_rerun()
    
    with col2:
        if st.button("📥 Export Alerts"):
            if alerts:
                alert_df = pd.DataFrame(alerts)
                csv = alert_df.to_csv(index=False)
                st.download_button(
                    label="Download Alert Log",
                    data=csv,
                    file_name=f"security_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No alerts to export")

def show_reports():
    st.header("📋 Reports & Documentation")
    
    # Generate comprehensive report
    st.subheader(" Generate Analysis Report")
    
    if st.button(" Generate Full Report"):
        with st.spinner("Generating comprehensive report..."):
            try:
                report = st.session_state.model.generate_report(st.session_state.data)
                
                st.success("✅ Report generated successfully!")
                
                # Display report summary
                st.subheader("📋 Report Summary")
                
                # Dataset information
                if 'dataset_info' in report:
                    st.write("**Dataset Information:**")
                    dataset_info = report['dataset_info']
                    st.write(f"- Total Samples: {dataset_info['total_samples']:,}")
                    st.write(f"- Total Columns: {len(dataset_info['columns'])}")
                    st.write(f"- Missing Values: {sum(dataset_info['missing_values'].values())}")
                
                # Network statistics
                if 'network_stats' in report:
                    st.write("**Network Statistics:**")
                    network_stats = report['network_stats']
                    for key, value in network_stats.items():
                        if isinstance(value, (int, float)):
                            st.write(f"- {key.replace('_', ' ').title()}: {value:,.2f}")
                        else:
                            st.write(f"- {key.replace('_', ' ').title()}: {value}")
                
                # Model performance
                if 'model_metrics' in report and report['model_metrics']:
                    st.write("**Model Performance:**")
                    metrics = report['model_metrics']
                    st.write(f"- Accuracy: {metrics.get('accuracy', 0):.4f}")
                    st.write(f"- Precision: {metrics.get('precision', 0):.4f}")
                    st.write(f"- Recall: {metrics.get('recall', 0):.4f}")
                    st.write(f"- F1-Score: {metrics.get('f1_score', 0):.4f}")
                
                # Security summary
                if 'threat_summary' in report:
                    st.write("**Security Summary:**")
                    threat_summary = report['threat_summary']
                    st.write(f"- Total Threats Detected: {report.get('threats_detected', 0)}")
                    st.write(f"- Classification Threats: {threat_summary.get('classification_threats', 0)}")
                    st.write(f"- Anomaly Threats: {threat_summary.get('anomaly_threats', 0)}")
                
                # Alert summary
                if 'alert_summary' in report:
                    st.write("**Alert Summary:**")
                    alert_summary = report['alert_summary']
                    for level, count in alert_summary.items():
                        st.write(f"- {level}: {count}")
                
                # Export options
                st.subheader("💾 Export Report")
                
                # CSV export
                if st.button("📥 Export as CSV"):
                    report_data = {
                        'Metric': ['Total Samples', 'Model Accuracy', 'Model Precision', 
                                 'Model Recall', 'Total Threats', 'Total Alerts'],
                        'Value': [
                            report['dataset_info']['total_samples'],
                            report['model_metrics'].get('accuracy', 0),
                            report['model_metrics'].get('precision', 0),
                            report['model_metrics'].get('recall', 0),
                            report.get('threats_detected', 0),
                            len(report['alerts'])
                        ]
                    }
                    
                    report_df = pd.DataFrame(report_data)
                    csv = report_df.to_csv(index=False)
                    
                    st.download_button(
                        label="Download Report (CSV)",
                        data=csv,
                        file_name=f"network_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                # JSON export
                if st.button("📥 Export as JSON"):
                    import json
                    json_data = json.dumps(report, indent=2, default=str)
                    
                    st.download_button(
                        label="Download Report (JSON)",
                        data=json_data,
                        file_name=f"network_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"❌ Report generation failed: {str(e)}")
    
    # System logs
    st.subheader("📜 System Logs")
    
    log_file = os.path.join(Config.LOGS_DIR, 'system.log')
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                log_lines = f.readlines()[-100:]  # Last 100 lines
                
            if log_lines:
                st.text_area("System Logs", value=''.join(log_lines), height=300)
            else:
                st.info("ℹ️ No system logs available")
        except Exception as e:
            st.error(f"❌ Error reading logs: {str(e)}")
    else:
        st.info("ℹ️ No system logs available")
    
    # Model information
    st.subheader("🤖 Model Information")
    
    if st.session_state.trained:
        st.write("**Trained Models:**")
        
        if st.session_state.model.classification_model is not None:
            st.write("✅ Classification Model: Random Forest")
        
        if st.session_state.model.anomaly_model is not None:
            st.write("✅ Anomaly Detection Model: Isolation Forest")
        
        # Model paths
        st.write("**Model Files:**")
        model_dir = Config.MODEL_DIR
        if os.path.exists(model_dir):
            model_files = os.listdir(model_dir)
            for file in model_files:
                file_path = os.path.join(model_dir, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                st.write(f"- {file} ({file_size:.1f} KB)")
    else:
        st.warning("⚠️ No models trained yet")

def start_real_time_monitoring():
    """Start real-time monitoring simulation"""
    st.subheader("🔄 Real-time Monitoring")
    
    # Create placeholder for real-time updates
    status_placeholder = st.empty()
    metrics_placeholder = st.empty()
    alerts_placeholder = st.empty()
    
    # Simulate real-time monitoring
    for i in range(10):  # Run for 10 iterations
        # Generate new data
        new_data = simulate_real_time_data(50, 0.15)
        
        # Detect threats
        try:
            threats = st.session_state.model.detect_threats(new_data)
            
            # Update status
            status_placeholder.info(f"🔄 Monitoring... Iteration {i+1}/10")
            
            # Update metrics
            with metrics_placeholder.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("New Connections", len(new_data))
                with col2:
                    st.metric("Threats Detected", len(threats))
                with col3:
                    if threats:
                        avg_confidence = np.mean([t.get('confidence', 0.5) for t in threats if 'confidence' in t])
                        st.metric("Avg Threat Confidence", f"{avg_confidence:.3f}")
            
            # Update alerts
            if threats:
                with alerts_placeholder.container():
                    for threat in threats[:3]:  # Show top 3 threats
                        st.warning(f"🚨 {threat['type']} Threat - Confidence: {threat.get('confidence', 'N/A')}")
            
            time.sleep(2)  # Wait 2 seconds between updates
            
        except Exception as e:
            st.error(f"❌ Monitoring error: {str(e)}")
            break
    
    status_placeholder.success("✅ Real-time monitoring completed!")

if __name__ == "__main__":
    main()
