from . import io
import os.path
from sklearn.preprocessing import StandardScaler,MinMaxScaler

def analyze(id):
    '''
    id : dataset id or a full path
    '''
    
    if (id in io.DATASET_MAP.keys()):
        X, y, X_names, _ = io.LoadDataSet(id)
    elif os.path.exists(id):
        X, y, X_names, _ = io.OpenDataSet(id)

    # normalization

    scaler = StandardScaler()
    scaler.fit(X)
    X_scaled = scaler.transform(X)

    # scaling to [0,1]

    mm_scaler = MinMaxScaler()
    X_mm_scaled = mm_scaler.fit_transform(X)

    
