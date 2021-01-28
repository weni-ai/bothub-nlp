import unittest
import os
import emoji

import sys
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from bothub.shared.utils.preprocessing.preprocessing_factory import PreprocessingFactory
from bothub.shared.utils.preprocessing.preprocessing_base import PreprocessingBase
from bothub.shared.utils.preprocessing.preprocessing_english import PreprocessingEnglish
from bothub.shared.utils.preprocessing.preprocessing_portuguese import PreprocessingPortuguese


class TestPipelineBuilder(unittest.TestCase):
    def setUp(self, *args):
        self.preprocess_factory = PreprocessingFactory()
        self.base = self.preprocess_factory.factory()
        self.portuguese = self.preprocess_factory.factory('pt_br')
        self.english = self.preprocess_factory.factory('en')

    def test__factory(self):
        base = PreprocessingFactory.factory()
        self.assertIsInstance(base, PreprocessingBase)
        base = PreprocessingFactory.factory('unexisting_language')
        self.assertIsInstance(base, PreprocessingBase)
        portuguese = PreprocessingFactory.factory('pt_br')
        self.assertIsInstance(portuguese, PreprocessingPortuguese)
        english = PreprocessingFactory.factory('en')
        self.assertIsInstance(english, PreprocessingEnglish)

    def test__default_preprocessing(self):
        phrase = "i'`m GOING não tô é the gym"
        expected = "im going nao to e the gym"
        self.assertEqual(self.base.default_preprocessing(phrase), expected)
        self.assertEqual(self.portuguese.default_preprocessing(phrase), expected)
        self.assertEqual(self.english.default_preprocessing(phrase), expected)

        self.assertRaises(ValueError, self.base.default_preprocessing, None)

    def test__extract_emoji_text(self):
        emoji_code = ':smile_face:'
        emoji_text = 'smile face'
        self.assertEqual(self.base.extract_emoji_text(emoji_code), emoji_text)
        self.assertRaises(ValueError, self.base.extract_emoji_text, None)
        self.assertRaises(ValueError, self.base.extract_emoji_text, 'not a emoji code')

    def test__emoji_handling(self):
        self.assertEqual(self.base.emoji_handling('😂'), "face with tears of joy")
        self.assertEqual(self.base.emoji_handling(''), '')

        for emoji_code in self.portuguese.emoji_contractions.keys():
            # transform code to emoji
            emj = emoji.emojize(emoji_code)

            self.assertEqual(self.portuguese.emoji_handling(emj), self.portuguese.emoji_contractions[emoji_code])
            self.assertEqual(self.english.emoji_handling(emj), self.english.emoji_contractions[emoji_code])

    def test__preprocess(self):
        phrase = "i'`m GOING não tô é the gym 😂"
        self.assertEqual(self.base.preprocess(phrase), "im going nao to e the gym face with tears of joy")
        self.assertEqual(self.portuguese.preprocess(phrase), "im going nao estou e the gym hahaha")
        self.assertEqual(self.english.preprocess(phrase), "im going nao to e the gym hahaha")
