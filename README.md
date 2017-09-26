# Bothub Demo

 ##### How to run 
 #
    docker build -t bothub-demo . 
 #
    docker run -e APP_REPOSITORY_URL=https://github.com/push-flow/bothub-nlp.git \
    -e APP_REPOSITORY_BRANCH=develop \
    -e BOTHUB_POSTGRES_USER=postgres \
    -e BOTHUB_POSTGRES_PASSWORD=postgres \
    -e BOTHUB_POSTGRES_DB=bothub \
    -e BOTHUB_POSTGRES=10.200.10.1 \
    -e BOTHUB_POSTGRES_PORT=5432 \
    -e BOTHUB_REDIS=10.200.10.1 \
    -e BOTHUB_REDIS_PORT=6379 \
    -e BOTHUB_REDIS_DB=2 -p "8000:80" \
    bothub-demo
