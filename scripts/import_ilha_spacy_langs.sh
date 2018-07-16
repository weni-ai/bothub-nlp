#!/bin/sh

if [[ ! -d "./ilha_spacy" ]]
then
    git clone --branch develop --depth 1 --single-branch https://github.com/Ilhasoft/spaCy.git ./ilha_spacy
else
    cd ./ilha_spacy && git pull origin develop && cd ..
fi

python scripts/link_lang_spacy.py pt_br ./ilha_spacy/spacy/lang/pt_br/ || :
