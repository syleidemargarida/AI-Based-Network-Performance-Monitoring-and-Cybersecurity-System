 AI-Based Network Performance Monitoring and Cybersecurity System

An intelligent system that uses Artificial Intelligence to monitor network performance, detect anomalies, identify cyber threats, and provide real-time visualization through a web-based dashboard.

Features

 Core Functionality
- Network Performance Monitoring**: Analyze latency, throughput, packet loss, and bandwidth usage
-  AI-Based Anomaly Detection**: Detect unusual patterns using Isolation Forest and clustering methods
-  Cybersecurity Integration**: Identify DDoS, brute force, intrusion attempts, and other attacks
-  Machine Learning Models**: Random Forest and SVM for classification
-  Real-Time Simulation**: Continuous data monitoring with instant alerts
-  Interactive Dashboard**: Beautiful Streamlit-based web interface

 Advanced Features
-  Multi-Dataset Support**: Compare and analyze different network datasets
- Alert Management**: Intelligent security alerts with severity levels
-  Comprehensive Logging**: Detailed attack detection logs
-  Report Export**: Generate and export analysis reports
-  Feature Importance Analysis**: Understand key network metrics
-  Real-time Visualization**: Live monitoring with automatic updates

 Quick Start

 Prerequisites
- Python 3.8+
- pip package manager

Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd AI-Network-Security-Monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## 📁 Project Structure

```
AI-Network-Security-Monitor/
├── 📁 data/                    # Dataset files
├── 📁 model/                   # Trained ML models
├── 📁 logs/                    # System and alert logs
├── 📁 static/                  # Static files and exports
├── 📁 config/                  # Configuration files
├── 📄 app.py                   # Streamlit dashboard
├── 📄 main.py                  # Core ML logic
├── 📄 utils.py                 # Helper functions
├── 📄 requirements.txt         # Python dependencies
└── 📄 README.md               # This file
```

How to Use

 1. Data Loading
- **Upload Dataset**: Support for CSV files with network traffic data
- **Generate Sample Data**: Create synthetic data for testing
- **Real-time Simulation**: Generate live streaming data

 2. Model Training
- **Classification Model**: Random Forest or SVM for attack detection
- **Anomaly Detection**: Isolation Forest for unsupervised anomaly detection
- **Performance Metrics**: Accuracy, precision, recall, F1-score

 3. Threat Detection
- **Real-time Scanning**: Analyze network traffic for threats
- **Pattern Analysis**: Identify suspicious network patterns
- **Confidence Scoring**: Probability-based threat assessment

 4. Performance Analysis
- **Network Metrics**: Duration, throughput, packet rate analysis
- **Time Series Analysis**: Performance trends over time
- **Correlation Analysis**: Relationship between metrics

 5. Security Alerts
- **Severity Levels**: LOW, MEDIUM, HIGH, CRITICAL
- **Alert Sources**: Classification, Anomaly Detection, Pattern Analysis
- **Alert Management**: View, filter, and export alerts

 Supported Datasets

Recommended Datasets
- **CICIDS2017**: Comprehensive intrusion detection dataset
- **NSL-KDD**: Network attack detection dataset
- **UNSW-NB15**: Network security dataset

 Data Format
Your dataset should include the following columns:
- **Flow Duration**: Connection duration in microseconds
- **Total Fwd/Backward Packets**: Packet counts
- **Total Length of Fwd/Backward Packets**: Byte counts
- **Flow Bytes/s**: Throughput metric
- **Flow Packets/s**: Packet rate
- **Label**: Attack/Normal classification

 Machine Learning Models

 Classification Models
- **Random Forest**: Ensemble method with feature importance
- **Support Vector Machine (SVM)**: Kernel-based classification

 Anomaly Detection
- **Isolation Forest**: Unsupervised anomaly detection
- **Statistical Analysis**: Pattern-based anomaly identification

 Model Evaluation
- **Accuracy**: Overall classification accuracy
- **Precision**: Attack detection precision
- **Recall**: Attack detection recall
- **F1-Score**: Harmonic mean of precision and recall
- **Cross-Validation**: 5-fold CV for robustness

 Configuration

 Settings (config/settings.py)
- **Model Parameters**: Random state, test size, anomaly threshold
- **Feature Columns**: Network metrics for analysis
- **Attack Types**: Mapping of attack categories
- **Alert Levels**: Severity color coding

 Customization
- Modify `NUMERIC_FEATURES` for your dataset
- Adjust `ANOMALY_THRESHOLD` for sensitivity
- Update `ATTACK_TYPES` for your attack categories

 Dashboard Features

 Data Overview Tab
- Dataset statistics and preview
- Traffic distribution visualization
- Data quality metrics

 Model Training Tab
- Model selection and configuration
- Training progress and results
- Feature importance analysis

 Threat Detection Tab
- Real-time threat scanning
- Threat classification and analysis
- Confidence scoring

 Performance Analysis Tab
- Network performance metrics
- Time series visualization
- Correlation analysis

 Security Alerts Tab
- Alert summary and statistics
- Recent alerts display
- Alert filtering and export

 Reports Tab
- Comprehensive report generation
- Export capabilities (CSV, JSON)
- System logs and model information

 Alert System

 Alert Types
- **CRITICAL**: High-confidence attacks (>90%)
- **HIGH**: Medium-confidence attacks (70-90%)
- **MEDIUM**: Low-confidence attacks (50-70%)
- **LOW**: Informational alerts

 Alert Sources
- **Classification Model**: Supervised threat detection
- **Anomaly Detection**: Unsupervised anomaly identification
- **Pattern Analysis**: Statistical pattern recognition
- **Performance Monitor**: Network performance issues

 Logging

 System Logs
- Model training progress
- Error messages and warnings
- System performance metrics

Alert Logs
- Security alert history
- Threat detection details
- Alert severity levels

 Real-time Features

 Live Monitoring
- Continuous data streaming
- Automatic threat detection
- Real-time alert generation

 Performance Updates
- Live metric updates
- Dynamic visualization
- Automatic dashboard refresh

 Export Capabilities

 Report Formats
- **CSV**: Tabular data export
- **JSON**: Structured data export
- **Logs**: System and alert logs

Export Options
- Analysis reports
- Alert history
- Model performance metrics
- Network statistics

 Troubleshooting

Common Issues

 Data Loading Errors
- **Issue**: "Could not read file with any supported encoding"
- **Solution**: Check file format and encoding. Use UTF-8 or Latin-1 encoding.

 Model Training Errors
- **Issue**: "No target column found in dataset"
- **Solution**: Ensure your dataset has a 'Label' column with attack/normal classifications.

 Memory Issues
- **Issue**: System runs out of memory with large datasets
- **Solution**: Reduce dataset size or increase system RAM.

Performance Optimization
- Use smaller datasets for initial testing
- Limit the number of displayed rows
- Clear alerts periodically
- Use appropriate model parameters

 Contributing

 Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Include error handling

 License

This project is licensed under the MIT License - see the LICENSE file for details.

 Acknowledgments

- **CICIDS2017 Dataset**: Canadian Institute for Cybersecurity
- **Scikit-learn**: Machine learning library
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualization library

 Support

For questions, issues, or suggestions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

Version History

 v1.0.0 (Current)
- Initial release
- Basic ML models
- Streamlit dashboard
- Real-time monitoring
- Alert system

Planned Features
- User authentication
- Advanced visualization
- More ML algorithms
- Database integration
- API endpoints

---

"An AI-powered system that monitors network performance, detects anomalies, and enhances cybersecurity through real-time intelligent analysis."


