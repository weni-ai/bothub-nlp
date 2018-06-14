import spacy


class SpacyLanguages(object):
    spacy_languages = {}

    def __getitem__(self, language):
        if language in self.spacy_languages:
            return self.spacy_languages.get(language)
        self.spacy_languages[language] = spacy.load(language)
        return self.__getitem__(language)
