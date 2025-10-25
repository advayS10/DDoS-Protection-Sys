
# The 79 features your models were trained on
FEATURE_NAMES = [
    # Flow features (0-4)
    'Flow Duration',
    'Total Fwd Packets',
    'Total Backward Packets',
    'Total Length of Fwd Packets',
    'Total Length of Bwd Packets',
    
    # Forward packet stats (5-8)
    'Fwd Packet Length Max',
    'Fwd Packet Length Min',
    'Fwd Packet Length Mean',
    'Fwd Packet Length Std',
    
    # Backward packet stats (9-12)
    'Bwd Packet Length Max',
    'Bwd Packet Length Min',
    'Bwd Packet Length Mean',
    'Bwd Packet Length Std',
    
    # Flow rates (13-14)
    'Flow Bytes/s',
    'Flow Packets/s',
    
    # Flow IAT (15-18)
    'Flow IAT Mean',
    'Flow IAT Std',
    'Flow IAT Max',
    'Flow IAT Min',
    
    # Forward IAT (19-23)
    'Fwd IAT Total',
    'Fwd IAT Mean',
    'Fwd IAT Std',
    'Fwd IAT Max',
    'Fwd IAT Min',
    
    # Backward IAT (24-28)
    'Bwd IAT Total',
    'Bwd IAT Mean',
    'Bwd IAT Std',
    'Bwd IAT Max',
    'Bwd IAT Min',
    
    # TCP Flags (29-32)
    'Fwd PSH Flags',
    'Bwd PSH Flags',
    'Fwd URG Flags',
    'Bwd URG Flags',
    
    # Header lengths (33-34)
    'Fwd Header Length',
    'Bwd Header Length',
    
    # Packet rates (35-36)
    'Fwd Packets/s',
    'Bwd Packets/s',
    
    # Packet length stats (37-41)
    'Min Packet Length',
    'Max Packet Length',
    'Packet Length Mean',
    'Packet Length Std',
    'Packet Length Variance',
    
    # Flag counts (42-49)
    'FIN Flag Count',
    'SYN Flag Count',
    'RST Flag Count',
    'PSH Flag Count',
    'ACK Flag Count',
    'URG Flag Count',
    'CWE Flag Count',
    'ECE Flag Count',
    
    # Ratios (50)
    'Down/Up Ratio',
    
    # Average sizes (51-52)
    'Average Packet Size',
    'Avg Fwd Segment Size',
    'Avg Bwd Segment Size',
    
    # Bulk transfer (53-58)
    'Fwd Avg Bytes/Bulk',
    'Fwd Avg Packets/Bulk',
    'Fwd Avg Bulk Rate',
    'Bwd Avg Bytes/Bulk',
    'Bwd Avg Packets/Bulk',
    'Bwd Avg Bulk Rate',
    
    # Subflow (59-62)
    'Subflow Fwd Packets',
    'Subflow Fwd Bytes',
    'Subflow Bwd Packets',
    'Subflow Bwd Bytes',
    
    # Window & data (63-66)
    'Init_Win_bytes_forward',
    'Init_Win_bytes_backward',
    'act_data_pkt_fwd',
    'min_seg_size_forward',
    
    # Active times (67-70)
    'Active Mean',
    'Active Std',
    'Active Max',
    'Active Min',
    
    # Idle times (71-74)
    'Idle Mean',
    'Idle Std',
    'Idle Max',
    'Idle Min'
]


def verify_features():
    """Check we have exactly 79 features"""
    count = len(FEATURE_NAMES)
    print(f"Total features: {count}")
    
    if count == 79:
        print("✅ Correct! 79 features defined")
        return True
    else:
        print(f"❌ Error! Expected 79, got {count}")
        return False
    
if __name__ == "__main__":
    verify_features()
    print("\nFirst 5 features:")
    for i, name in enumerate(FEATURE_NAMES[:5]):
        print(f"  {i}: {name}")
    
    print("\nLast 5 features:")
    for i, name in enumerate(FEATURE_NAMES[-5:], start=70):
        print(f"  {i}: {name}")