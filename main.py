import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score, GridSearchCV
import joblib
import os
import logging
from datetime import datetime
from config.settings import Config
from utils import DataProcessor, AlertManager

class NetworkSecurityModel:
    """Main ML model class for network security analysis"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.alert_manager = AlertManager()
        self.classification_model = None
        self.anomaly_model = None
        self.model_metrics = {}
        Config.ensure_directories()
    
    def train_classification_model(self, df, model_type='random_forest'):
        """Train supervised classification model"""
        try:
            logging.info(f"Training {model_type} classification model")
            
            # Prepare features and target
            X, y, feature_names = self.data_processor.prepare_features(df)
            
            if y is None:
                raise ValueError("No target column found in dataset")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=Config.TEST_SIZE, random_state=Config.RANDOM_STATE, stratify=y
            )
            
            # Select model
            if model_type == 'random_forest':
                self.classification_model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=Config.RANDOM_STATE,
                    max_depth=10,
                    min_samples_split=5
                )
            elif model_type == 'svm':
                self.classification_model = SVC(
                    kernel='rbf',
                    random_state=Config.RANDOM_STATE,
                    probability=True
                )
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Train model
            self.classification_model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.classification_model.predict(X_test)
            y_pred_proba = self.classification_model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            self.model_metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, pos_label='Attack', average='binary'),
                'recall': recall_score(y_test, y_pred, pos_label='Attack', average='binary'),
                'f1_score': f1_score(y_test, y_pred, pos_label='Attack', average='binary'),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'classification_report': classification_report(y_test, y_pred, output_dict=True),
                'feature_names': feature_names,
                'feature_importance': None
            }
            
            # Feature importance for Random Forest
            if model_type == 'random_forest':
                self.model_metrics['feature_importance'] = dict(zip(
                    feature_names, self.classification_model.feature_importances_
                ))
            
            # Cross-validation
            cv_scores = cross_val_score(self.classification_model, X, y, cv=5)
            self.model_metrics['cv_mean'] = cv_scores.mean()
            self.model_metrics['cv_std'] = cv_scores.std()
            
            logging.info(f"Model trained successfully. Accuracy: {self.model_metrics['accuracy']:.4f}")
            
            # Save model
            self.save_model('classification_model.pkl')
            
            return self.model_metrics
            
        except Exception as e:
            logging.error(f"Error training classification model: {str(e)}")
            raise
    
    def train_anomaly_detection(self, df):
        """Train unsupervised anomaly detection model"""
        try:
            logging.info("Training anomaly detection model")
            
            # Prepare features (unsupervised, so no target needed)
            X, _, feature_names = self.data_processor.prepare_features(df)
            
            # Train Isolation Forest
            self.anomaly_model = IsolationForest(
                contamination=Config.ANOMALY_THRESHOLD,
                random_state=Config.RANDOM_STATE,
                n_estimators=100
            )
            
            # Fit model
            self.anomaly_model.fit(X)
            
            # Get anomaly scores
            anomaly_scores = self.anomaly_model.decision_function(X)
            predictions = self.anomaly_model.predict(X)
            
            # Calculate statistics
            anomaly_count = np.sum(predictions == -1)
            normal_count = len(predictions) - anomaly_count
            
            anomaly_stats = {
                'total_samples': len(X),
                'anomaly_count': anomaly_count,
                'normal_count': normal_count,
                'anomaly_percentage': (anomaly_count / len(X)) * 100,
                'mean_anomaly_score': np.mean(anomaly_scores),
                'std_anomaly_score': np.std(anomaly_scores),
                'feature_names': feature_names
            }
            
            logging.info(f"Anomaly detection trained. Found {anomaly_count} anomalies ({anomaly_stats['anomaly_percentage']:.2f}%)")
            
            # Save model
            self.save_model('anomaly_model.pkl')
            
            return anomaly_stats
            
        except Exception as e:
            logging.error(f"Error training anomaly detection model: {str(e)}")
            raise
    
    def detect_threats(self, df):
        """Detect threats using trained models"""
        if self.classification_model is None and self.anomaly_model is None:
            raise ValueError("No trained models available")
        
        threats = []
        
        try:
            # Prepare features
            X, _, feature_names = self.data_processor.prepare_features(df)
            
            # Classification-based detection
            if self.classification_model is not None:
                predictions = self.classification_model.predict(X)
                probabilities = self.classification_model.predict_proba(X)
                
                for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                    if pred == 'Attack' and prob[1] > 0.7:  # High confidence attacks
                        threat = {
                            'index': i,
                            'type': 'Classification',
                            'confidence': prob[1],
                            'prediction': pred,
                            'features': dict(zip(feature_names, X.iloc[i].values))
                        }
                        threats.append(threat)
                        
                        # Add alert
                        self.alert_manager.add_alert(
                            level='HIGH' if prob[1] > 0.9 else 'MEDIUM',
                            message=f"Attack detected with {prob[1]:.2f} confidence",
                            source="Classification Model",
                            details={'confidence': prob[1], 'sample_index': i}
                        )
            
            # Anomaly-based detection
            if self.anomaly_model is not None:
                anomaly_predictions = self.anomaly_model.predict(X)
                anomaly_scores = self.anomaly_model.decision_function(X)
                
                for i, (pred, score) in enumerate(zip(anomaly_predictions, anomaly_scores)):
                    if pred == -1:  # Anomaly detected
                        threat = {
                            'index': i,
                            'type': 'Anomaly',
                            'score': score,
                            'prediction': 'Anomaly',
                            'features': dict(zip(feature_names, X.iloc[i].values))
                        }
                        threats.append(threat)
                        
                        # Add alert
                        self.alert_manager.add_alert(
                            level='MEDIUM' if score > -0.1 else 'HIGH',
                            message=f"Anomalous traffic detected (score: {score:.3f})",
                            source="Anomaly Detection",
                            details={'anomaly_score': score, 'sample_index': i}
                        )
            
            logging.info(f"Detected {len(threats)} potential threats")
            return threats
            
        except Exception as e:
            logging.error(f"Error detecting threats: {str(e)}")
            raise
    
    def analyze_network_performance(self, df):
        """Analyze network performance metrics"""
        performance_analysis = {}
        
        try:
            # Basic network metrics
            if 'Flow_Duration' in df.columns:
                performance_analysis['duration_stats'] = {
                    'mean': df['Flow_Duration'].mean(),
                    'median': df['Flow_Duration'].median(),
                    'std': df['Flow_Duration'].std(),
                    'min': df['Flow_Duration'].min(),
                    'max': df['Flow_Duration'].max()
                }
            
            if 'Flow_Bytes_s' in df.columns:
                performance_analysis['throughput_stats'] = {
                    'mean': df['Flow_Bytes_s'].mean(),
                    'median': df['Flow_Bytes_s'].median(),
                    'std': df['Flow_Bytes_s'].std(),
                    'min': df['Flow_Bytes_s'].min(),
                    'max': df['Flow_Bytes_s'].max()
                }
            
            if 'Flow_Packets_s' in df.columns:
                performance_analysis['packet_rate_stats'] = {
                    'mean': df['Flow_Packets_s'].mean(),
                    'median': df['Flow_Packets_s'].median(),
                    'std': df['Flow_Packets_s'].std(),
                    'min': df['Flow_Packets_s'].min(),
                    'max': df['Flow_Packets_s'].max()
                }
            
            # Identify performance issues
            issues = []
            
            if 'Flow_Bytes_s' in df.columns:
                low_throughput = df[df['Flow_Bytes_s'] < df['Flow_Bytes_s'].quantile(0.05)]
                if len(low_throughput) > 0:
                    issues.append({
                        'type': 'Low Throughput',
                        'count': len(low_throughput),
                        'percentage': (len(low_throughput) / len(df)) * 100
                    })
            
            if 'Flow_Duration' in df.columns:
                long_duration = df[df['Flow_Duration'] > df['Flow_Duration'].quantile(0.95)]
                if len(long_duration) > 0:
                    issues.append({
                        'type': 'Long Duration Connections',
                        'count': len(long_duration),
                        'percentage': (len(long_duration) / len(df)) * 100
                    })
            
            performance_analysis['issues'] = issues
            
            # Add alerts for performance issues
            for issue in issues:
                if issue['percentage'] > 10:
                    self.alert_manager.add_alert(
                        level='MEDIUM',
                        message=f"Performance issue detected: {issue['type']} ({issue['percentage']:.1f}% of connections)",
                        source="Performance Monitor",
                        details=issue
                    )
            
            return performance_analysis
            
        except Exception as e:
            logging.error(f"Error analyzing network performance: {str(e)}")
            raise
    
    def save_model(self, filename):
        """Save trained model to file"""
        model_path = os.path.join(Config.MODEL_DIR, filename)
        
        if filename == 'classification_model.pkl' and self.classification_model is not None:
            joblib.dump({
                'model': self.classification_model,
                'scaler': self.data_processor.scaler,
                'feature_names': self.model_metrics.get('feature_names', []),
                'metrics': self.model_metrics
            }, model_path)
        elif filename == 'anomaly_model.pkl' and self.anomaly_model is not None:
            joblib.dump({
                'model': self.anomaly_model,
                'scaler': self.data_processor.scaler,
                'feature_names': self.data_processor.feature_columns
            }, model_path)
        
        logging.info(f"Model saved to {model_path}")
    
    def load_model(self, filename):
        """Load trained model from file"""
        model_path = os.path.join(Config.MODEL_DIR, filename)
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        model_data = joblib.load(model_path)
        
        if filename == 'classification_model.pkl':
            self.classification_model = model_data['model']
            self.data_processor.scaler = model_data['scaler']
            self.model_metrics = model_data['metrics']
        elif filename == 'anomaly_model.pkl':
            self.anomaly_model = model_data['model']
            self.data_processor.scaler = model_data['scaler']
        
        logging.info(f"Model loaded from {model_path}")
    
    def generate_report(self, df):
        """Generate comprehensive analysis report"""
        report = {
            'timestamp': Config.get_timestamp(),
            'dataset_info': {
                'total_samples': len(df),
                'columns': list(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'data_types': df.dtypes.to_dict()
            },
            'network_stats': self.data_processor.calculate_network_stats(df),
            'model_metrics': self.model_metrics,
            'alerts': self.alert_manager.get_recent_alerts(20),
            'alert_summary': self.alert_manager.get_alert_summary()
        }
        
        # Add performance analysis if possible
        try:
            report['performance_analysis'] = self.analyze_network_performance(df)
        except:
            pass
        
        # Add threat detection if models are trained
        if self.classification_model is not None or self.anomaly_model is not None:
            try:
                threats = self.detect_threats(df)
                report['threats_detected'] = len(threats)
                report['threat_summary'] = {
                    'classification_threats': len([t for t in threats if t['type'] == 'Classification']),
                    'anomaly_threats': len([t for t in threats if t['type'] == 'Anomaly'])
                }
            except:
                pass
        
        return report

def simulate_real_time_data(num_samples=100, attack_ratio=0.1):
    """Simulate real-time network traffic data for testing"""
    np.random.seed(Config.RANDOM_STATE)
    
    # Generate normal traffic
    normal_samples = int(num_samples * (1 - attack_ratio))
    attack_samples = num_samples - normal_samples
    
    # Normal traffic features
    normal_data = {
        'Flow_Duration': np.random.exponential(1000, normal_samples),
        'Total_Fwd_Packets': np.random.poisson(10, normal_samples),
        'Total_Backward_Packets': np.random.poisson(8, normal_samples),
        'Total_Length_of_Fwd_Packets': np.random.exponential(1000, normal_samples),
        'Total_Length_of_Bwd_Packets': np.random.exponential(800, normal_samples),
        'Flow_Bytes_s': np.random.exponential(10000, normal_samples),
        'Flow_Packets_s': np.random.exponential(50, normal_samples),
        'Label': ['Benign'] * normal_samples
    }
    
    # Attack traffic features (different patterns)
    attack_data = {
        'Flow_Duration': np.random.exponential(5000, attack_samples),  # Longer duration
        'Total_Fwd_Packets': np.random.poisson(100, attack_samples),  # More packets
        'Total_Backward_Packets': np.random.poisson(50, attack_samples),
        'Total_Length_of_Fwd_Packets': np.random.exponential(5000, attack_samples),
        'Total_Length_of_Bwd_Packets': np.random.exponential(3000, attack_samples),
        'Flow_Bytes_s': np.random.exponential(50000, attack_samples),  # Higher throughput
        'Flow_Packets_s': np.random.exponential(200, attack_samples),
        'Label': ['DDoS'] * attack_samples
    }
    
    # Combine data
    combined_data = {}
    for key in normal_data:
        combined_data[key] = np.concatenate([normal_data[key], attack_data[key]])
    
    # Create DataFrame
    df = pd.DataFrame(combined_data)
    
    # Add timestamp
    df['Timestamp'] = pd.date_range(start=datetime.now(), periods=len(df), freq='1S')
    
    # Shuffle data
    df = df.sample(frac=1, random_state=Config.RANDOM_STATE).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    # Example usage
    model = NetworkSecurityModel()
    
    # Generate sample data
    sample_data = simulate_real_time_data(1000)
    
    # Train models
    print("Training classification model...")
    model.train_classification_model(sample_data)
    
    print("Training anomaly detection model...")
    model.train_anomaly_detection(sample_data)
    
    # Generate report
    report = model.generate_report(sample_data)
    print("Analysis complete!")
