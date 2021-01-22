import logging

# Explicitly set logging level for this module before any import
# because otherwise it logs tensorflow/pytorch versions
logging.getLogger("transformers.file_utils").setLevel(logging.WARNING)

from transformers import (
    TFBertModel,
    # TFOpenAIGPTModel,
    # TFGPT2Model,
    # TFXLNetModel,
    # TFXLMModel,
    # TFDistilBertModel,
    # TFRobertaModel,
    BertTokenizer,
    # OpenAIGPTTokenizer,
    # GPT2Tokenizer,
    # XLNetTokenizer,
    # XLMTokenizer,
    # DistilBertTokenizer,
    # RobertaTokenizer,
)

from rasa.nlu.utils.hugging_face.transformers_pre_post_processors import (
    bert_tokens_pre_processor,
    # gpt_tokens_pre_processor,
    # xlnet_tokens_pre_processor,
    # roberta_tokens_pre_processor,
    bert_embeddings_post_processor,
    # gpt_embeddings_post_processor,
    # xlnet_embeddings_post_processor,
    # roberta_embeddings_post_processor,
    bert_tokens_cleaner,
    # openaigpt_tokens_cleaner,
    # gpt2_tokens_cleaner,
    # xlnet_tokens_cleaner,
)

language_to_model = {
    "en": "bert_english",
    "pt_br": "bert_portuguese",
    "multilang": "bert_multilang"
}

from_pt_dict = {
    "bert_portuguese": True
}

model_class_dict = {
    "bert_english": TFBertModel,
    "bert_portuguese": TFBertModel,
    "bert_multilang": TFBertModel,
}
model_tokenizer_dict = {
    "bert_english": BertTokenizer,
    "bert_portuguese": BertTokenizer,
    "bert_multilang": BertTokenizer,
}
model_weights_defaults = {
    "bert_english": "bert-base-uncased",
    "bert_portuguese": "neuralmind/bert-base-portuguese-cased",
    "bert_multilang": "bert-base-multilingual-uncased"
}

model_special_tokens_pre_processors = {
    "bert_english": bert_tokens_pre_processor,
    "bert_portuguese": bert_tokens_pre_processor,
    "bert_multilang": bert_tokens_pre_processor,
}

model_tokens_cleaners = {
    "bert_english": bert_tokens_cleaner,
    "bert_portuguese": bert_tokens_cleaner,
    "bert_multilang": bert_tokens_cleaner,
}

model_embeddings_post_processors = {
    "bert_english": bert_embeddings_post_processor,
    "bert_portuguese": bert_embeddings_post_processor,
    "bert_multilang": bert_embeddings_post_processor,
}

model_config_url = {
    "bert_portuguese": "https://bothub-nlp-models.s3.amazonaws.com/bert-portuguese/config.json",
    "bert_english": "https://bothub-nlp-models.s3.amazonaws.com/bert-english/config.json",
    "bert_multilang": "https://bothub-nlp-models.s3.amazonaws.com/bert_multilang/config.json"
}

model_download_url = {
    "bert_portuguese": "https://bothub-nlp-models.s3.amazonaws.com/bert-portuguese/pytorch_model.bin",
    "bert_english": "https://bothub-nlp-models.s3.amazonaws.com/bert-english/tf_model.h5",
    "bert_multilang": "https://bothub-nlp-models.s3.amazonaws.com/bert_multilang/tf_model.h5"
}
