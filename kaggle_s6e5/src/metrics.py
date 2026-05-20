import numpy as np
from sklearn.metrics import f1_score, cohen_kappa_score

def f1_macro_score(y_true, y_pred):
    """
    F1-Macro score for F1 Racing Pit Prediction.
    Handles class imbalance between 'Stay Out' and 'Pit'.
    """
    return f1_score(y_true, y_pred, average="macro")

def kappa_score(y_true, y_pred):
    """
    Quadratic-weighted Cohen's Kappa.
    """
    return cohen_kappa_score(y_true, y_pred, weights="quadratic")

def f1_macro_lgbm_eval(y_true, y_pred):
    """
    Custom F1-Macro evaluation function for LightGBM.
    Handles the case where y_true is a numpy array (Sklearn API).
    """
    # For binary classification in LightGBM, y_pred is usually probabilities
    # But in feval, it might be the raw scores depending on the version
    # We'll assume probabilities for now, but handle binary conversion
    y_pred_binary = (y_pred > 0.5).astype(int)
    
    score = f1_score(y_true.astype(int), y_pred_binary, average='macro')
    return 'f1_macro', score, True
