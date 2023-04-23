import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import pickle

# Importamos las librerias necesarias.
data = pd.read_csv('src\\data\\processed\\dataset_modelo.csv')

# Dividimos los datos en X e y. Utilizaremos como X todas las columnas excepto la columna 'status', que será nuestro vector y.
X = data.iloc[:, 0:-1]
y = data['status']

# Dividimos en X_test, X_val, y_train, y_val.
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenamos el modelo (le marcamos un early stopping a las 2 rondas sin mejorar).
xgb = XGBClassifier(colsample_bytree=0.5, learning_rate=0.1, max_depth=None, min_child_weight=1, n_estimators=200, reg_alpha=0.1, reg_lambda=0.1, subsample=0.9, 
                    early_stopping_rounds = 2)
xgb.fit(X_train,y_train, eval_set = [(X_val, y_val)])

# Guardamos el modelo en un archivo pickle.
with open('Fishing_Phishing.pkl', 'wb') as modelo:
    pickle.dump(xgb, modelo)