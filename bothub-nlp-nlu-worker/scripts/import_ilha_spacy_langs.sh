#!/bin/sh

if [ ! -d "./spacy-langs" ]
then
    git clone --branch master --depth 1 --single-branch \
        https://github.com/Ilhasoft/spacy-lang-models \
        ./spacy-langs
else
    cd ./spacy-langs && git pull origin master && cd ..
fi

python scripts/link_lang_spacy.py pt_br ./spacy-langs/pt_br/ || :
python scripts/link_lang_spacy.py mn ./spacy-langs/mn/ || :
