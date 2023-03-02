# Importing libraries
import os
import time
import pandas as pd
import numpy as np
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import  OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression


if __name__ == "__main__":

    # MLFLOW Experiment setup
    experiment_name="getaround-experiment"
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    client = mlflow.tracking.MlflowClient()

    mlflow.set_tracking_uri("https://mlflow-server.herokuapp.com/")

    run = client.create_run(experiment.experiment_id)

    print("training model...")
    
    start_time = time.time()

    mlflow.sklearn.autolog()


    # Importing dataset
    dataset = pd.read_csv('get_around_pricing_project.csv', index_col= 0)


    # Separating target variable Y from features X
    target_variable = "rental_price_per_day"
    X = dataset.drop(target_variable, axis = 1)
    Y = dataset.loc[:,target_variable]


    # Dividing dataset between Train set & Test set 
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)


    # Preprocessing
    numeric_features = ['mileage', 'engine_power']
    categorical_features = ['model_key','fuel', 'paint_color','car_type','private_parking_available','has_gps',
                        'has_air_conditioning', 'automatic_car', 'has_getaround_connect','has_speed_regulator', 'winter_tires']

    numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
    categorical_transformer = Pipeline(steps=[('encoder', OneHotEncoder(drop='first', handle_unknown = 'ignore'))])
    # drop='first': to drop one of the encoded columns, to prevent collinearity. 
    # handle_unknown='ignore': prevent errors if unknown categories appear on a new data to study (such as brand or new color)


    preprocessor = ColumnTransformer(transformers=[('num', numeric_transformer, numeric_features),
                                                ('cat', categorical_transformer, categorical_features)])


    model = Pipeline(steps=[("Preprocessing", preprocessor),
                            ("Regressor", LinearRegression())
                            ])    


    # Log experiment to MLFlow
    with mlflow.start_run(run_id = run.info.run_id) as run:
        model.fit(X_train, Y_train)
        predictions = model.predict(X_train)

    # Log model seperately to have more flexibility on setup 
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="Car_Rental_Price_Predictor",
            registered_model_name="Car_Rental_Price_Predictor_LR",
            signature=infer_signature(X_train, predictions)
            )
    # Infer_signature: useful to get the input needed and output with Mlflow

        print("...Done!")
        print(f"---Total training time: {time.time()-start_time}")