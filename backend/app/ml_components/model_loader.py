import pickle
import os


def load_models():
    """Load Random Forest, Neural Network, and Scaler"""
    
    rf_model = None
    nn_model = None
    scaler = None
    

    # Get the directory where THIS file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to 'app', then into 'ml_model'
    base_path = os.path.join(current_dir, '..', 'ml_model')
    base_path = os.path.abspath(base_path)  # Convert to absolute path

    # Load Random Forest
    try:
        rf_path = os.path.join(base_path, 'rf_model.pkl')
        if os.path.exists(rf_path):
            with open(rf_path, 'rb') as f:
                rf_model = pickle.load(f)
            print("Random Forest loaded")
        else:
            print(f"File not found: {rf_path}")
            return None, None, None, False
    except Exception as e:
        print(f"RF loading error: {e}")
        return None, None, None, False
    
    # Load Neural Network
    try:
        nn_path = os.path.join(base_path, 'nn_model.pkl')
        if os.path.exists(nn_path):
            with open(nn_path, 'rb') as f:
                nn_model = pickle.load(f)
            print("Neural Network loaded")
        else:
            print(f"File not found: {nn_path}")
            return None, None, None, False
    except Exception as e:
        print(f"NN loading error: {e}")
        return None, None, None, False
    
    # Load Scaler (CRITICAL - needed for feature scaling!)
    try:
        scaler_path = os.path.join(base_path, 'scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            print("Scaler loaded")
        else:
            print(f"File not found: {scaler_path}")
            return None, None, None, False
    except Exception as e:
        print(f"Scaler loading error: {e}")
        return None, None, None, False
    
    # Check if ALL 3 loaded successfully
    ready = (rf_model is not None and 
             nn_model is not None and 
             scaler is not None)
    
    if ready:
        print("All models ready!")
    else:
        print("Models not ready")
    
    return rf_model, nn_model, scaler, ready


if __name__ == "__main__":

    print("TESTING MODEL LOADER")
    print("\n")
    
    # Try to load
    rf, nn, scaler, ready = load_models()
    

    print("RESULTS")
    print()
    
    if ready:
        print("ALL MODELS LOADED SUCCESSFULLY!")
        print(f"\n   RF Model:  {type(rf).__name__}")
        print(f"   NN Model:  {type(nn).__name__}")
        print(f"   Scaler:    {type(scaler).__name__}")
        print(f"   Ready:     {ready}")
        
        # Additional info
        if hasattr(rf, 'n_estimators'):
            print(f"\n   RF trees:  {rf.n_estimators}")
        if hasattr(nn, 'hidden_layer_sizes'):
            print(f"   NN layers: {nn.hidden_layer_sizes}")
        
        print("\nYou're ready to make predictions!")
        
    else:
        print("MODEL LOADING FAILED")
        print("\nTroubleshooting:")
        print("1. Check models/ folder exists")
        print("2. Verify all 3 .pkl files are present:")
        print("   - models/rf_model.pkl")
        print("   - models/nn_model.pkl")
        print("   - models/scaler.pkl")
        print("3. Run: ls -lh models/")
    
    print("\n")