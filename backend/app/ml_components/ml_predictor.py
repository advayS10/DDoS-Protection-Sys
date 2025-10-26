"""
ML Predictor - uses models + scaler
File: ml_predictor.py
"""

import numpy as np
import pandas as pd
from typing import Dict
from .model_loader import load_models
from .feature_calculator import FeatureCalculator


class MLPredictor:
    """Makes predictions using RF, NN, and Scaler"""
    
    def __init__(self):
        # Load all 3 files
        print("Initializing ML Predictor...")
        self.rf_model, self.nn_model, self.scaler, self.ready = load_models()
        
        # Feature calculator
        self.feature_calc = FeatureCalculator()
        
        # Default threshold
        self.threshold = 0.7
    
    def predict(self, ip: str, features_df: pd.DataFrame = None, threshold: float = None) -> Dict:
        """
        Make DDoS prediction
        
        Args:
            ip: Client IP address
            threshold: Confidence threshold (default 0.7)
        
        Returns:
            dict with is_threat, confidence, predictions
        """
        if not self.ready:
            return {
                'is_threat': False,
                'confidence': 0.0,
                'error': 'Models not loaded'
            }
        
        if threshold is not None:
            self.threshold = threshold
        
        try:
            # Step 1: Calculate 10 features (returns DataFrame)
            
            if features_df is None:
                if ip is None:
                    return {'is_threat': False, 'confidence': 0.0, 'error': 'No input provided'}
                features_df = self.feature_calc.calculate_features(ip)
            features_df = features_df.reindex(columns=self.scaler.feature_names_in_, fill_value=0)

            # Step 2: Scale features (CRITICAL!)
            # Scaler expects DataFrame with feature names
            features_scaled = self.scaler.transform(features_df)
            
            # Step 3: Get predictions from both models
            predictions = {}
            probabilities = []
            
            # Random Forest prediction
            if self.rf_model:
                try:
                    rf_pred = self.rf_model.predict(features_scaled)[0]
                    rf_proba = self.rf_model.predict_proba(features_scaled)[0]
                    
                    predictions['rf'] = int(rf_pred)
                    probabilities.append(float(rf_proba[1]))  # Prob of DDoS
                    
                except Exception as e:
                    print(f"RF prediction error: {e}")
            
            # Neural Network prediction
            if self.nn_model:
                try:
                    nn_pred = self.nn_model.predict(features_scaled)[0]
                    
                    if hasattr(self.nn_model, 'predict_proba'):
                        nn_proba = self.nn_model.predict_proba(features_scaled)[0]
                        probabilities.append(float(nn_proba[1]))
                    else:
                        probabilities.append(float(nn_pred))
                    
                    predictions['nn'] = int(nn_pred > 0.5 if isinstance(nn_pred, float) else nn_pred)
                    
                except Exception as e:
                    print(f"NN prediction error: {e}")
            
            # Step 4: Calculate ensemble confidence
            confidence = float(np.mean(probabilities)) if probabilities else 0.0
            
            # Step 5: Make decision
            is_threat = confidence > self.threshold
            
            return {
                'is_threat': is_threat,
                'confidence': confidence,
                'predictions': predictions,
                'threshold': self.threshold
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'is_threat': False,
                'confidence': 0.0,
                'error': str(e)
            }


# Test it
if __name__ == "__main__":
    from flask import Flask
    
    print("\n" + "="*60)
    print("TESTING ML PREDICTOR")
    print("="*60 + "\n")
    
    app = Flask(__name__)
    predictor = MLPredictor()
    
    if not predictor.ready:
        print("❌ Predictor not ready - check model loading")
        exit(1)
    
    test_ip = "192.168.1.100"
    
    # Test 1: Normal traffic (few requests)
    print("Test 1: Normal traffic (5 requests)")
    print("-" * 60)
    
    for i in range(5):
        predictor.feature_calc.tracker.track_request(test_ip, 500 + i*10)
    
    with app.test_request_context('/'):
        result = predictor.predict(test_ip)
    
    print(f"Is Threat: {result['is_threat']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"RF prediction: {result['predictions'].get('rf')}")
    print(f"NN prediction: {result['predictions'].get('nn')}")
    
    # Test 2: Attack traffic (many requests)
    print("\n" + "-" * 60)
    print("Test 2: Attack traffic (100 requests)")
    print("-" * 60)
    
    for i in range(95):  # Add 95 more
        predictor.feature_calc.tracker.track_request(test_ip, 500 + i*10)
    
    with app.test_request_context('/'):
        result = predictor.predict(test_ip)
    
    print(f"Is Threat: {result['is_threat']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"RF prediction: {result['predictions'].get('rf')}")
    print(f"NN prediction: {result['predictions'].get('nn')}")
    
    print("\n" + "="*60)
    print("✅ ML PREDICTOR TEST COMPLETE")
    print("="*60 + "\n")

    # Test 3: Custom data
    print("\n" + "-"*60)
    print("Test 3: Custom data")
    print("-" * 60)

    my_features = pd.DataFrame([{
        'Packet Length Std': 12.5,
        'Bwd Packet Length Max': 80,
        'Average Packet Size': 60,
        'Packet Length Variance': 15,
        'Bwd Packet Length Std': 10,
        'Subflow Fwd Bytes': 500,
        'Avg Fwd Segment Size': 50,
        'Total Length of Fwd Packets': 600,
        'Max Packet Length': 120,
        'Subflow Fwd Packets': 5
    }])

    result = predictor.predict(test_ip, features_df=my_features)

    print(f"Is Threat: {result['is_threat']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"RF prediction: {result['predictions'].get('rf')}")
    print(f"NN prediction: {result['predictions'].get('nn')}")