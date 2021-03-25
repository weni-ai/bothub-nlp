import unittest
import os
import emoji

import sys
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bothub.shared.utils.preprocessing.preprocessing_factory import PreprocessingFactory
from bothub.shared.utils.preprocessing.preprocessing_base import PreprocessingBase
from bothub.shared.utils.preprocessing.preprocessing_english import PreprocessingEnglish
from bothub.shared.utils.preprocessing.preprocessing_portuguese import PreprocessingPortuguese
from bothub.shared.utils.preprocessing.preprocessing_spanish import PreprocessingSpanish
from rasa.nlu.training_data import Message


class TestPipelineBuilder(unittest.TestCase):
    def setUp(self, *args):
        self.base = PreprocessingFactory().factory()
        self.portuguese = PreprocessingFactory('pt_br').factory()
        self.english = PreprocessingFactory('en').factory()
        self.spanish = PreprocessingFactory('es').factory()

    def test__factory(self):
        base = PreprocessingFactory().factory()
        self.assertIsInstance(base, PreprocessingBase)
        base = PreprocessingFactory('unexisting_language').factory()
        self.assertIsInstance(base, PreprocessingBase)
        portuguese = PreprocessingFactory('pt_br').factory()
        self.assertIsInstance(portuguese, PreprocessingPortuguese)
        english = PreprocessingFactory('en').factory()
        self.assertIsInstance(english, PreprocessingEnglish)
        spanish = PreprocessingFactory('es').factory()
        self.assertIsInstance(spanish, PreprocessingSpanish)

    def test__default_preprocessing(self):
        phrase = "i'`m GOING não tô é the gym"
        expected = "im going nao to e the gym"
        self.assertEqual(self.base.default_preprocessing(phrase), (expected, None))
        self.assertEqual(self.portuguese.default_preprocessing(phrase), (expected, None))
        self.assertEqual(self.english.default_preprocessing(phrase), (expected, None))
        self.assertEqual(self.spanish.default_preprocessing(phrase), (expected, None))

        self.assertRaises(ValueError, self.base.default_preprocessing, None)

        phrase = "i'`m GOING não tô é the 'gym"
        expected = "im going nao to e the gym"
        entities = [
            {
                "start": 0,
                "end": 4,
                "value": "i'`m",
                "entity": "me"
            },
            {
                "start": 24,
                "end": 28,
                "value": "'gym",
                "entity": "gym"
            },
        ]
        expected_entities = [
            {
                "start": 0,
                "end": 2,
                "value": "im",
                "entity": "me"
            },
            {
                "start": 22,
                "end": 25,
                "value": "gym",
                "entity": "gym"
            },
        ]
        self.assertEqual(
            self.base.default_preprocessing(phrase, entities),
            (expected, expected_entities)
        )
        self.assertEqual(
            self.base.default_preprocessing(phrase, None),
            (expected, None)
        )

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
            self.assertEqual(self.spanish.emoji_handling(emj), self.spanish.emoji_contractions[emoji_code])

    def test__parse_preprocess(self):

        phrase = "i'`m GOING não tô é the gym 😂"

        self.assertEqual(self.base.preprocess(Message(text=phrase)).text, "im going nao to e the gym face with tears of joy")
        self.assertEqual(self.portuguese.preprocess(Message(text=phrase)).text, "im going nao to e the gym hahaha")
        self.assertEqual(self.english.preprocess(Message(text=phrase)).text, "im going nao to e the gym hahaha")
        self.assertEqual(self.spanish.preprocess(Message(text=phrase)).text, "im going nao to e the gym hahaha")

        pp = PreprocessingFactory(remove_accent=False).factory()
        self.assertEqual(pp.preprocess(Message(text=phrase)).text, "im going não tô é the gym face with tears of joy")
        pp = PreprocessingFactory('pt_br', remove_accent=False).factory()
        self.assertEqual(pp.preprocess(Message(text=phrase)).text, "im going não tô é the gym hahaha")
        pp = PreprocessingFactory('en', remove_accent=False).factory()
        self.assertEqual(pp.preprocess(Message(text=phrase)).text, "im going não tô é the gym hahaha")
        pp = PreprocessingFactory('es', remove_accent=False).factory()
        self.assertEqual(pp.preprocess(Message(text=phrase)).text, "im going não tô é the gym hahaha")

    def test__training_preprocess(self):
        preprocessors = [
            PreprocessingFactory(remove_accent=False).factory(),
            PreprocessingFactory('pt_br', remove_accent=False).factory(),
            PreprocessingFactory('en', remove_accent=False).factory(),
            PreprocessingFactory('es', remove_accent=False).factory()
        ]
        for preprocessor in preprocessors:
            phrase = "i'`m GOING não tô é the 'gym"
            expected_phrase = "im going não tô é the gym"
            entities = [
                {
                    "start": 0,
                    "end": 4,
                    "value": "i'`m",
                    "entity": "me"
                },
                {
                    "start": 24,
                    "end": 28,
                    "value": "'gym",
                    "entity": "gym"
                },
            ]
            expected_entities = [
                {
                    "start": 0,
                    "end": 2,
                    "value": "im",
                    "entity": "me"
                },
                {
                    "start": 22,
                    "end": 25,
                    "value": "gym",
                    "entity": "gym"
                },
            ]
            message = Message.build(
                text=phrase,
                intent='test',
                entities=entities,
            )

            self.assertEqual(
                preprocessor.preprocess(message).text,
                expected_phrase
            )
            self.assertEqual(
                preprocessor.preprocess(message).data.get('entities'),
                expected_entities
            )

            message = Message.build(
                text=phrase,
                intent='test',
                entities=None,
            )
            self.assertEqual(
                preprocessor.preprocess(message).text,
                expected_phrase
            )
            with self.assertRaises(KeyError):
                _ = preprocessor.preprocess(message).data['entities']

    def test__test(self):
        example = {
            "text": "The new coronavirus doesn\u2019t affect young people.",
            "intent": "myth",
            "entities": [
                {
                    "start": 8,
                    "end": 19,
                    "value": "coronavirus",
                    "entity": "coronavirus"
                },
                {
                    "start": 35,
                    "end": 40,
                    "value": "young",
                    "entity": "young"
                }
            ]
        }
        message = Message.build(
            text=example['text'],
            intent=example['intent'],
            entities=example['entities'],
        )

        result = PreprocessingFactory('en', remove_accent=False).factory().preprocess(message)
        result2 = PreprocessingFactory('en', remove_accent=False).factory().preprocess(Message(text=example['text']))

        self.assertEqual(result.text, result2.text)
