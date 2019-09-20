# Bothub NLP API Service

This is a Python Web service.

## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_NLP_API_PORT | `int` | `2657` | Web service port |
| BOTHUB_NLP_SENTRY_CLIENT | `bool` | `None` | Sentry Client |
| SUPPORTED_LANGUAGES | `str` | `en|pt` | Set supported languages. Separe languages using |. You can set location follow the format: [LANGUAGE_CODE]:[LANGUAGE_LOCATION]. |
| BOTHUB_ENGINE_URL | `str` | `https://api.bothub.it` | Web service url |
