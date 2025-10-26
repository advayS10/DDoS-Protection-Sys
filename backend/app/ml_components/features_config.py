# Your 10 features in EXACT order
FEATURE_NAMES = [
    'Packet Length Std',
    'Bwd Packet Length Max',
    'Average Packet Size',
    'Packet Length Variance',
    'Bwd Packet Length Std',
    'Subflow Fwd Bytes',
    'Avg Fwd Segment Size',
    'Total Length of Fwd Packets',
    'Max Packet Length',
    'Subflow Fwd Packets'
]

# Quick check
if __name__ == "__main__":
    print(f"Total features: {len(FEATURE_NAMES)}")
    if len(FEATURE_NAMES) == 10:
        print("✅ Correct!")
    else:
        print("❌ Wrong count!")