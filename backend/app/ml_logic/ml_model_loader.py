import pickle
import os

class ModelLoader:

    def __init__(self):
        self.rf_model = None
        self.nn_model = None
        self.models_loaded = False

    def load_models(self):

        print("Loading ml models....")

        # check if ml_model directory exist
        if not os.path.exists('../ml_model'):
            print("ml_model directory doesn't exist.")
            return False
        
        # try to load rf_model
        try:
            rf_path = '../ml_model/rf_model.pkl'
            if os.path.exists(rf_path):
                with open(rf_path, 'rb') as f:
                    self.rf_model = pickle.load(f)
                print(f"Random Forest loaded from {rf_path}")
            else:
                print(f"Random Forest model not found at {rf_path}")
        except Exception as e:
            print(f"Error loading RF Model: {e}")
            return False

        # try to load nn_model
        try:
            nn_path = '../ml_model/nn_model.pkl'
            if os.path.exists(nn_path):
                with open(nn_path, 'rb') as f:
                    self.nn_model = pickle.load(f)
                print(f"Neural Network loaded from {nn_path}")
            else:
                print(f"Neural Network not found at {nn_path}")
        except Exception as e:
            print(f"Error loading NN Model: {e}")
            return False
        
        if self.rf_model or self.nn_model:
            self.models_loaded = True
            print("Model loading complete!")
            return True
        else:
            print("No model loaded")
            return False
        
    def check_model_types(self):

        if self.rf_model:
            print(f"RF model type: {type(self.rf_model)}")
            print(f"RF model class: {self.rf_model.__class__.__name__}")

        if self.nn_model:
            print(f"NN model type: {type(self.nn_model)}")
            print(f"NN model class: {self.nn_model.__class__.__name__}")

if __name__ == "__main__":

    loader = ModelLoader()

    if loader.load_models():
        print("\n=== Model Info ===")
        loader.check_model_types()
    else:
        print("\nModel loading Failed")
        print("Make sure models are in correct directory 'ml_model'")