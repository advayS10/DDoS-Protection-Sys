"""
Feature Calculator - Fixed to return DataFrame with feature names
File: your_module/ml_components/feature_calculator.py
"""

import numpy as np
import pandas as pd  # ← ADD THIS IMPORT
from flask import request
from .features_config import FEATURE_NAMES
from .request_tracker import RequestTracker


class FeatureCalculator:
    """Calculate 10 features with proper naming"""
    
    def __init__(self):
        self.tracker = RequestTracker()
    
    def calculate_current_packet_size(self):
        """Estimate size of current HTTP request"""
        size = 0
        
        # Headers
        for key, value in request.headers.items():
            size += len(key) + len(value)
        
        # Path
        size += len(request.path)
        
        # Query
        if request.query_string:
            size += len(request.query_string)
        
        # Body
        if request.content_length:
            size += request.content_length
        
        # HTTP overhead
        size += 100
        
        return max(size, 200)
    
    def calculate_features(self, ip: str):
        """
        Calculate all 10 features and return as DataFrame
        
        Returns:
            pandas DataFrame with shape (1, 10) and proper column names
        """
        
        # Get recent packet sizes
        sizes = self.tracker.get_recent_sizes(ip)
        
        # If no history, use current only
        if not sizes:
            current = self.calculate_current_packet_size()
            sizes = [current]
        
        # Convert to numpy for calculations
        sizes_array = np.array(sizes)
        
        # Calculate each feature
        features = {}
        
        # 1. Packet Length Std
        features['Packet Length Std'] = float(np.std(sizes_array))
        
        # 2. Bwd Packet Length Max (estimate 70% of forward)
        features['Bwd Packet Length Max'] = float(np.max(sizes_array)) * 0.7
        
        # 3. Average Packet Size
        features['Average Packet Size'] = float(np.mean(sizes_array))
        
        # 4. Packet Length Variance
        features['Packet Length Variance'] = float(np.var(sizes_array))
        
        # 5. Bwd Packet Length Std (estimate 60% of forward)
        features['Bwd Packet Length Std'] = features['Packet Length Std'] * 0.6
        
        # 6. Subflow Fwd Bytes (total)
        features['Subflow Fwd Bytes'] = float(np.sum(sizes_array))
        
        # 7. Avg Fwd Segment Size (same as average)
        features['Avg Fwd Segment Size'] = features['Average Packet Size']
        
        # 8. Total Length of Fwd Packets (total)
        features['Total Length of Fwd Packets'] = features['Subflow Fwd Bytes']
        
        # 9. Max Packet Length
        features['Max Packet Length'] = float(np.max(sizes_array))
        
        # 10. Subflow Fwd Packets (count)
        features['Subflow Fwd Packets'] = float(len(sizes_array))
        
        # Convert to DataFrame with proper column names (CRITICAL!)
        feature_df = pd.DataFrame([features], columns=FEATURE_NAMES)
        
        # Clean up NaN/inf
        feature_df = feature_df.replace([np.inf, -np.inf], 0)
        feature_df = feature_df.fillna(0)
        
        return feature_df


# Test it
if __name__ == "__main__":
    from flask import Flask
    
    app = Flask(__name__)
    calc = FeatureCalculator()
    test_ip = "1.2.3.4"
    
    # Track some requests
    print("Tracking requests...")
    for i in range(10):
        calc.tracker.track_request(test_ip, 500 + i*50)
    
    # Calculate features
    with app.test_request_context('/'):
        features = calc.calculate_features(test_ip)
    
    print(f"\nFeature type: {type(features)}")
    print(f"Feature shape: {features.shape}")
    print(f"Expected: (1, 10)")
    
    if features.shape == (1, 10):
        print("✅ Correct!")
        print("\nFeature names:")
        print(features.columns.tolist())
        print("\nFirst 3 values:")
        print(features.iloc[0, :3])
    else:
        print("❌ Wrong shape!")