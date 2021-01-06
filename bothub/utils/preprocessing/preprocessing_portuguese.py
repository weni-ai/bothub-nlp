from .preprocessing_interface import PreprocessingInterface
from .preprocessing_base import PreprocessingBase

import re


class PreprocessingPortuguese(PreprocessingInterface):

    def preprocess(self, phrase: str = None):

        if phrase == None:
            return

        phrase = PreprocessingBase().preprocess(phrase)

        contractions = {
            "oi": r"\b((o+)(i+)(e*))\b",
            "sim": r"\b(s|S)+\b",
            "nao": r"\b(n|N)+\b",
            "beleza": r"\b(blz)z*a*\b",
            "estou": r"\b(t)o+\b",
            "esta": r"\b(t)a+\b",
            "marketing": r"\b(mkt)\b",
            "okay": r"\b(ok(a|e)*(y*))\b",
            "bom dia": r"\b(bd)\b",
            "falou": r"\b(f(a*)l(o*)(w|u)+(s*))\b",
            "valeu": r"\b(v(a*)l(e*)(w|u)+(s*))\b",
            "tranquilo": r"\b(tranks)\b"
        }

        for word in contractions.keys():
            phrase = re.sub(contractions[word], word, phrase)

        emoji_contractions = {
            ":face_with_tears_of_joy:": "hahaha",  # 😂
            ":red_heart_selector:": "amor",  # ❤️
            ":smiling_face_with_heart-eyes:": "amei",  # 😍
            ":rolling_on_the_floor_laughing:": "hahaha",  # 🤣
            ":smiling_face_with_smiling_eyes:": "feliz",  # 😊
            ":folded_hands:": "amem",  # 🙏
            ":two_hearts:": "carinho",  # 💕
            ":loudly_crying_face:": "triste",  # 😭
            ":face_blowing_a_kiss:": "beijo",  # 😘
            ":thumbs_up:": "ok",  # 👍
            ":grinning_face_with_sweat:": "hehehe",  # 😅
            ":clapping_hands:": "parabens",  # 👏
            ":beaming_face_with_smiling_eyes:": "feliz",  # 😁
            ":heart_suit_selector:": "amor",  # ♥️
            ":fire:": "quente",  # 🔥
            ":broken_heart:": "magoado",  # 💔
            ":sparkling_heart:": "carinho",  # 💖
            ":blue_heart:": "amigo",  # 💙
            ":crying_face:": "triste",  # 😢
            ":thinking_face:": "pensar",  # 🤔
            ":grinning_squinting_face:": "risos",  # 😆
            ":face_with_rolling_eyes:": "duvida",  # 🙄
            ":flexed_biceps:": "forte",  # 💪
            ":winking_face:": "piscar",  # 😉
            ":smiling_face_selector:": "feliz",  # ☺️
            ":OK_hand:": "ok",  # 👌
            ":hugging_face:": "abraco",  # 🤗
            ":purple_heart:": "amor",  # 💜
            ":pensive_face:": "triste",  # 😔
            ":smiling_face_with_sunglasses:": "orgulhoso",  # 😎
            ":smiling_face_with_halo:": "santo",  # 😇
            ":rose:": "rosa",  # 🌹
            ":person_facepalming:": "inacreditavel",  # 🤦
            ":party_popper:": "festa",  # 🎉
            ":double_exclamation_mark_selector:": "urgente",  # ‼️
            ":revolving_hearts:": "carinho",  # 💞
            ":victory_hand_selector:": "vitoria",  # ✌️
            ":sparkles:": "brilho",  # ✨
            ":person_shrugging:": "indiferenca",  # 🤷
            ":face_screaming_in_fear:": "medo",  # 😱
            ":relieved_face:": "alivio",  # 😌
            ":cherry_blossom:": "rosa",  # 🌸
            ":raising_hands:": "ainda bem",  # 🙌
            ":face_savoring_food:": "brincadeira",  # 😋
            ":growing_heart:": "amizade",  # 💗
            ":green_heart:": "amizade",  # 💚
            ":smirking_face:": "flertar",  # 😏
            ":yellow_heart:": "amizade",  # 💛
            ":slightly_smiling_face:": "feliz",  # 🙂
            ":beating_heart:": "amor",  # 💓
            ":star-struck:": "fabuloso",  # 🤩
            ":grinning_face_with_smiling_eyes:": "sorriso",  # 😄
            ":grinning_face:": "sorriso",  # 😀
            ":grinning_face_with_big_eyes:": "feliz",  # 😃
            ":hundred_points:": "pontuacao maxima",  # 💯
            ":see-no-evil_monkey:": "brincadeira",  # 🙈
            ":backhand_index_pointing_down:": "apontar",  # 👇
            ":musical_notes:": "musica",  # 🎶
            ":unamused_face:": "chateado",  # 😒
            ":face_with_hand_over_mouth:": "risada",  # 🤭
            ":heart_exclamation:": "coracao",  # ❣️
            ":exclamation_mark:": "importante",  # ❗
            ":winking_face_with_tongue:": "brincalhao",  # 😜
            ":kiss_mark:": "beijo",  # 💋
            ":eyes:": "curiosidade",  # 👀
            ":sleepy_face:": "sono",  # 😪
            ":expressionless_face:": "indiferente",  # 😑
            ":collision:": "batida",  # 💥
            ":person_raising_hand:": "atencao",  # 🙋
            ":disappointed_face:": "desapontado",  # 😞
            ":weary_face:": "cansado",  # 😩
            ":pouting_face:": "furioso",  # 😡
            ":zany_face:": "brincadeira",  # 🤪
            ":oncoming_fist:": "firme",  # 👊
            ":sun_selector:": "sol",  # ☀️
            ":sad_but_relieved_face:": "triste",  # 😥
            ":drooling_face:": "desejo",  # 🤤
            ":backhand_index_pointing_right:": "apontar",  # 👉
            ":woman_dancing:": "danca",  # 💃
            ":flushed_face:": "envergonhado",  # 😳
            ":raised_hand:": "atencao",  # ✋
            ":kissing_face_with_closed_eyes:": "beijo",  # 😚
            ":squinting_face_with_tongue:": "brincadeira",  # 😝
            ":sleeping_face:": "sono",  # 😴
            ":glowing_star:": "estrela",  # 🌟
            ":grimacing_face:": "sem graca",  # 😬
            ":upside-down_face:": "brincalhao",  # 🙃
            ":four_leaf_clover:": "trevo",  # 🍀
            ":tulip:": "tulipa",  # 🌷
            ":smiling_cat_face_with_heart-eyes:": "apaixonado",  # 😻
            ":downcast_face_with_sweat:": "desapontado",  # 😓
            ":white_medium_star:": "estrela",  # ⭐
            ":white_heavy_check_mark:": "concluido",  # ✅
            ":rainbow:": "arco-iris",  # 🌈
            ":smiling_face_with_horns:": "malvado",  # 😈
            ":sign_of_the_horns:": "metal",  # 🤘
            ":sweat_droplets:": "respingo",  # 💦
            ":check_mark:": "concluido",  # ✔️
            ":persevering_face:": "exausto",  # 😣
            ":person_running:": "corrida",  # 🏃
            ":bouquet:": "flores",  # 💐
            ":frowning_face_selector:": "triste",  # ☹️
            ":confetti_ball:": "festa",  # 🎊
            ":heart_with_arrow:": "apaixonado",  # 💘
            ":angry_face:": "furioso",  # 😠
            ":index_pointing_up_selector:": "atencao",  # ☝️
            ":confused_face:": "confuso",  # 😕
            ":hibiscus:": "flor",  # 🌺
            ":birthday_cake:": "aniversario",  # 🎂
            ":sunflower:": "girassol",  # 🌻
            ":neutral_face:": "indiferente",  # 😐
            ":middle_finger:": "raiva",  # 🖕
            ":heart_with_ribbon:": "presente coracao",  # 💝
            ":speak-no-evil_monkey:": "segredo",  # 🙊
            ":cat_face_with_tears_of_joy:": "hahaha",  # 😹
            ":speaking_head_selector:": "falar",  # 🗣️
            ":dizzy:": "tontura",  # 💫
            ":skull:": "caveira",  # 💀
            ":crown:": "coroa",  # 👑
            ":musical_note:": "musica",  # 🎵
            ":crossed_fingers:": "ansioso",  # 🤞
            ":face_with_tongue:": "pegadinha",  # 😛
            ":red_circle:": "circulo vermelho",  # 🔴
            ":face_with_steam_from_nose:": "bravo",  # 😤
            ":blossom:": "flor",  # 🌼
            ":tired_face:": "cansado",  # 😫
            ":soccer_ball:": "bola",  # ⚽
            ":call_me_hand:": "maneiro",  # 🤙
            ":hot_beverage:": "bebida quente",  # ☕
            ":trophy:": "vencedor",  # 🏆
            ":orange_heart:": "amizade",  # 🧡
            ":wrapped_gift:": "presente",  # 🎁
            ":high_voltage:": "eletricidade",  # ⚡
            ":sun_with_face:": "sol",  # 🌞
            ":balloon:": "balao",  # 🎈
            ":cross_mark:": "negacao",  # ❌
            ":raised_fist:": "punho",  # ✊
            ":waving_hand:": "adeus",  # 👋
            ":astonished_face:": "perplexo",  # 😲
            ":herb:": "planta",  # 🌿
            ":shushing_face:": "segredo",  # 🤫
            ":backhand_index_pointing_left:": "apontar",  # 👈
            ":face_with_open_mouth:": "perplexo",  # 😮
            ":person_gesturing_OK:": "ok",  # 🙆
            ":clinking_beer_mugs:": "brinde",  # 🍻
            ":dog_face:": "cachorro",  # 🐶
            ":anxious_face_with_sweat:": "ansiedade",  # 😰
            ":face_with_raised_eyebrow:": "duvida",  # 🤨
            ":face_without_mouth:": "mudo",  # 😶
            ":handshake:": "acordo",  # 🤝
            ":person_walking:": "caminhar",  # 🚶
            ":money_bag:": "dinheiro",  # 💰
            ":strawberry:": "morango",  # 🍓
            ":anger_symbol:": "batida",  # 💢
        }

        regex_emoji = r":[A-Za-z0-9\-_]+:"
        emojis = re.findall(regex_emoji, phrase)

        for emoji in emojis:
            if emoji in emoji_contractions:
                phrase = re.sub(emoji, emoji_contractions[emoji], phrase)

        return phrase
