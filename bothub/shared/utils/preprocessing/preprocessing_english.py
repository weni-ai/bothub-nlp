import re
from bothub.shared.utils.preprocessing.preprocessing_base import PreprocessingBase


class PreprocessingEnglish(PreprocessingBase):
    emoji_contractions = {
        ":face_with_tears_of_joy:": "hahaha",  # 😂
        ":red_heart_selector:": "love",  # ❤️
        ":smiling_face_with_heart-eyes:": "loved it",  # 😍
        ":rolling_on_the_floor_laughing:": "hahaha",  # 🤣
        ":smiling_face_with_smiling_eyes:": "happy",  # 😊
        ":folded_hands:": "amen",  # 🙏
        ":two_hearts:": "affection",  # 💕
        ":loudly_crying_face:": "sad",  # 😭
        ":face_blowing_a_kiss:": "kiss",  # 😘
        ":thumbs_up:": "ok",  # 👍
        ":grinning_face_with_sweat:": "hehehe",  # 😅
        ":clapping_hands:": "congratulations",  # 👏
        ":beaming_face_with_smiling_eyes:": "happy",  # 😁
        ":heart_suit_selector:": "love",  # ♥️
        ":fire:": "hot",  # 🔥
        ":broken_heart:": "hurt",  # 💔
        ":sparkling_heart:": "affection",  # 💖
        ":blue_heart:": "friendship",  # 💙
        ":crying_face:": "sad",  # 😢
        ":thinking_face:": "thinking",  # 🤔
        ":grinning_squinting_face:": "laughs",  # 😆
        ":face_with_rolling_eyes:": "doubt",  # 🙄
        ":flexed_biceps:": "strong",  # 💪
        ":winking_face:": "wink",  # 😉
        ":smiling_face_selector:": "happy",  # ☺️
        ":OK_hand:": "ok",  # 👌
        ":hugging_face:": "hug",  # 🤗
        ":purple_heart:": "love",  # 💜
        ":pensive_face:": "sad",  # 😔
        ":smiling_face_with_sunglasses:": "proud",  # 😎
        ":smiling_face_with_halo:": "saint",  # 😇
        ":rose:": "rose",  # 🌹
        ":person_facepalming:": "facepalm",  # 🤦
        ":party_popper:": "party",  # 🎉
        ":double_exclamation_mark_selector:": "exclamation",  # ‼️
        ":revolving_hearts:": "affection",  # 💞
        ":victory_hand_selector:": "vitory",  # ✌️
        ":sparkles:": "sparkles",  # ✨
        ":person_shrugging:": "indiferent",  # 🤷
        ":face_screaming_in_fear:": "fear",  # 😱
        ":relieved_face:": "relieved",  # 😌
        ":cherry_blossom:": "cherry blossom",  # 🌸
        ":raising_hands:": "glad",  # 🙌
        ":face_savoring_food:": "face_savoring_food",  # 😋
        ":growing_heart:": "heart",  # 💗
        ":green_heart:": "friendship",  # 💚
        ":smirking_face:": "smirk",  # 😏
        ":yellow_heart:": "friendship",  # 💛
        ":slightly_smiling_face:": "smile",  # 🙂
        ":beating_heart:": "love",  # 💓
        ":star-struck:": "fabulous",  # 🤩
        ":grinning_face_with_smiling_eyes:": "happy",  # 😄
        ":grinning_face:": "happy",  # 😀
        ":grinning_face_with_big_eyes:": "happy",  # 😃
        ":hundred_points:": "hundred points",  # 💯
        ":see-no-evil_monkey:": "joke",  # 🙈
        ":backhand_index_pointing_down:": "point down",  # 👇
        ":musical_notes:": "music",  # 🎶
        ":unamused_face:": "unamused",  # 😒
        ":face_with_hand_over_mouth:": "laughs",  # 🤭
        ":heart_exclamation:": "heart",  # ❣️
        ":exclamation_mark:": "!",  # ❗
        ":winking_face_with_tongue:": "wink",  # 😜
        ":kiss_mark:": "kiss",  # 💋
        ":eyes:": "curious",  # 👀
        ":sleepy_face:": "sleepy",  # 😪
        ":expressionless_face:": "indiferent",  # 😑
        ":collision:": "hit",  # 💥
        ":person_raising_hand:": "raise hand",  # 🙋
        ":disappointed_face:": "disappointed",  # 😞
        ":weary_face:": "weary",  # 😩
        ":pouting_face:": "furious",  # 😡
        ":zany_face:": "zany",  # 🤪
        ":oncoming_fist:": "oncoming fist",  # 👊
        ":sun_selector:": "sun",  # ☀️
        ":sad_but_relieved_face:": "sad",  # 😥
        ":drooling_face:": "drooling",  # 🤤
        ":backhand_index_pointing_right:": "point right",  # 👉
        ":woman_dancing:": "dancing",  # 💃
        ":flushed_face:": "flushed",  # 😳
        ":raised_hand:": "raised hand",  # ✋
        ":kissing_face_with_closed_eyes:": "kiss",  # 😚
        ":squinting_face_with_tongue:": "joke",  # 😝
        ":sleeping_face:": "sleepy",  # 😴
        ":glowing_star:": "glow",  # 🌟
        ":grimacing_face:": "grimacing",  # 😬
        ":upside-down_face:": "playful",  # 🙃
        ":four_leaf_clover:": "clover",  # 🍀
        ":tulip:": "tulip",  # 🌷
        ":smiling_cat_face_with_heart-eyes:": "love",  # 😻
        ":downcast_face_with_sweat:": "disappointed",  # 😓
        ":white_medium_star:": "star",  # ⭐
        ":white_heavy_check_mark:": "check mark",  # ✅
        ":rainbow:": "rainbow",  # 🌈
        ":smiling_face_with_horns:": "evil",  # 😈
        ":sign_of_the_horns:": "metal",  # 🤘
        ":sweat_droplets:": "droplets",  # 💦
        ":check_mark:": "check mark",  # ✔️
        ":persevering_face:": "persevering",  # 😣
        ":person_running:": "running",  # 🏃
        ":bouquet:": "bouquet",  # 💐
        ":frowning_face_selector:": "frowning",  # ☹️
        ":confetti_ball:": "confetti",  # 🎊
        ":heart_with_arrow:": "love",  # 💘
        ":angry_face:": "angry",  # 😠
        ":index_pointing_up_selector:": "point up",  # ☝️
        ":confused_face:": "confused",  # 😕
        ":hibiscus:": "hibiscus",  # 🌺
        ":birthday_cake:": "birthday",  # 🎂
        ":sunflower:": "sunflower",  # 🌻
        ":neutral_face:": "indiferent",  # 😐
        ":middle_finger:": "angry",  # 🖕
        ":heart_with_ribbon:": "heart",  # 💝
        ":speak-no-evil_monkey:": "secret",  # 🙊
        ":cat_face_with_tears_of_joy:": "hahaha",  # 😹
        ":speaking_head_selector:": "talk",  # 🗣️
        ":dizzy:": "dizzy",  # 💫
        ":skull:": "skull",  # 💀
        ":crown:": "crown",  # 👑
        ":musical_note:": "music",  # 🎵
        ":crossed_fingers:": "wishful",  # 🤞
        ":face_with_tongue:": "joke",  # 😛
        ":red_circle:": "red circle",  # 🔴
        ":face_with_steam_from_nose:": "angry",  # 😤
        ":blossom:": "blossom",  # 🌼
        ":tired_face:": "tired",  # 😫
        ":soccer_ball:": "ball",  # ⚽
        ":call_me_hand:": "cool",  # 🤙
        ":hot_beverage:": "hot beverage",  # ☕
        ":trophy:": "winner",  # 🏆
        ":orange_heart:": "heart",  # 🧡
        ":wrapped_gift:": "gift",  # 🎁
        ":high_voltage:": "high voltage",  # ⚡
        ":sun_with_face:": "sun",  # 🌞
        ":balloon:": "balloon",  # 🎈
        ":cross_mark:": "wrong",  # ❌
        ":raised_fist:": "fist",  # ✊
        ":waving_hand:": "goodbye",  # 👋
        ":astonished_face:": "astonished",  # 😲
        ":herb:": "herb",  # 🌿
        ":shushing_face:": "shush",  # 🤫
        ":backhand_index_pointing_left:": "point left",  # 👈
        ":face_with_open_mouth:": "astonished",  # 😮
        ":person_gesturing_OK:": "ok",  # 🙆
        ":clinking_beer_mugs:": "toast",  # 🍻
        ":dog_face:": "dog",  # 🐶
        ":anxious_face_with_sweat:": "anxious",  # 😰
        ":face_with_raised_eyebrow:": "doubt",  # 🤨
        ":face_without_mouth:": "speachless",  # 😶
        ":handshake:": "deal",  # 🤝
        ":person_walking:": "walk",  # 🚶
        ":money_bag:": "money",  # 💰
        ":strawberry:": "strawberry",  # 🍓
        ":anger_symbol:": "hit",  # 💢
    }

    contractions = {
        "marketing": r"\b(mkt)\b",
        "okay": r"\b(ok)\b",
        "thank you": r"\b(ty)|(thx)|(tks)\b",
        "am": r"('m)m*\b",
        " are": r"('re)e*\b",
        " not": r"(n't)\b",
    }

    def __init__(self, remove_accent=True):
        super(PreprocessingEnglish, self).__init__(remove_accent=remove_accent)

    def training_preprocess(self, example):
        phrase = example.text
        entities = example.data.get('entities')

        phrase = self.emoji_handling(phrase)
        phrase, entities = self.default_preprocessing(phrase, entities, is_training=True)

        for word in self.contractions.keys():
            phrase = re.sub(self.contractions[word], word, phrase)

        example.text = phrase
        example.data['entities'] = entities

        return example

    def parse_preprocess(self, phrase: str = None):
        phrase = self.emoji_handling(phrase)
        phrase = self.default_preprocessing(phrase)

        for word in self.contractions.keys():
            phrase = re.sub(self.contractions[word], word, phrase)

        return phrase
