import pickle

with open('rf_model.pkl', 'rb') as f:
    model = pickle.load(f)
print(model)  # Does this work?