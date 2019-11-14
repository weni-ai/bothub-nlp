import uvicorn
from bothub_nlp_api.app import app


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=2657, log_level='info')
