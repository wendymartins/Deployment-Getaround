docker run -it \
-p 4000:80 \
-e PORT=80 \
-e AWS_ACCESS_KEY_ID=XXXXX \
-e AWS_SECRET_ACCESS_KEY=XXXXX \
-e BACKEND_STORE_URI=nothing \
-e ARTIFACT_ROOT=XXXXX \
image1