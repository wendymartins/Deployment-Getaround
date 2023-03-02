docker run -it \
-v "$(pwd):/home/app" \
-e MLFLOW_TRACKING_URI="https://mlflow-server.herokuapp.com/" \
-e AWS_ACCESS_KEY_ID=XXXXX \
-e AWS_SECRET_ACCESS_KEY=XXXXX \
-e BACKEND_STORE_URI=XXXXX \
-e ARTIFACT_ROOT=XXXXX \
image1bis python trainlr.py