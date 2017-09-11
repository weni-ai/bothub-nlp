# Bothub Demo

 ##### How to run 
 #
    docker build -t bothub-demo . 
 #
    docker run -e APP_REPOSITORY_URL=https://github.com/push-flow/bothub-demo-python -e BOTHUB_REDIS=10.200.10.1 -e BOTHUB_POSTGRES=10.200.10.1 -p "8000:80" bothub-demo
