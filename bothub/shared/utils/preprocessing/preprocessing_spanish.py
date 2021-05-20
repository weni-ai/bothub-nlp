import re
from bothub.shared.utils.preprocessing.preprocessing_base import PreprocessingBase


class PreprocessingSpanish(PreprocessingBase):
    emoji_contractions = {
        ":face_with_tears_of_joy:": "hahaha",  # 😂
        ":red_heart_selector:": "amor",  # ❤️
        ":smiling_face_with_heart-eyes:": "me gusto",  # 😍
        ":rolling_on_the_floor_laughing:": "hahaha",  # 🤣
        ":smiling_face_with_smiling_eyes:": "felíz",  # 😊
        ":folded_hands:": "amén",  # 🙏
        ":two_hearts:": "afecto",  # 💕
        ":loudly_crying_face:": "triste",  # 😭
        ":face_blowing_a_kiss:": "beso",  # 😘
        ":thumbs_up:": "ok",  # 👍
        ":grinning_face_with_sweat:": "hehehe",  # 😅
        ":clapping_hands:": "parabens",  # 👏
        ":beaming_face_with_smiling_eyes:": "muy felíz",  # 😁
        ":heart_suit_selector:": "amor",  # ♥️
        ":fire:": "caliente",  # 🔥
        ":broken_heart:": "lastimar",  # 💔
        ":sparkling_heart:": "afecto",  # 💖
        ":blue_heart:": "amigo",  # 💙
        ":crying_face:": "triste",  # 😢
        ":thinking_face:": "pensar",  # 🤔
        ":grinning_squinting_face:": "se rié",  # 😆
        ":face_with_rolling_eyes:": "duda",  # 🙄
        ":flexed_biceps:": "fuerte",  # 💪
        ":winking_face:": "parpadear",  # 😉
        ":smiling_face_selector:": "felíz",  # ☺️
        ":OK_hand:": "ok",  # 👌
        ":hugging_face:": "abrazo",  # 🤗
        ":purple_heart:": "amor",  # 💜
        ":pensive_face:": "triste",  # 😔
        ":smiling_face_with_sunglasses:": "orgulloso",  # 😎
        ":smiling_face_with_halo:": "santo",  # 😇
        ":rose:": "rosa",  # 🌹
        ":person_facepalming:": "increíble",  # 🤦
        ":party_popper:": "fiesta",  # 🎉
        ":double_exclamation_mark_selector:": "urgente",  # ‼️
        ":revolving_hearts:": "afecto",  # 💞
        ":victory_hand_selector:": "victoria",  # ✌️
        ":sparkles:": "brillo",  # ✨
        ":person_shrugging:": "indiferencia",  # 🤷
        ":face_screaming_in_fear:": "miedo",  # 😱
        ":relieved_face:": "alivio",  # 😌
        ":cherry_blossom:": "rosa",  # 🌸
        ":raising_hands:": "menos mal",  # 🙌
        ":face_savoring_food:": "es una broma",  # 😋
        ":growing_heart:": "amistad",  # 💗
        ":green_heart:": "amistad",  # 💚
        ":smirking_face:": "flirtear",  # 😏
        ":yellow_heart:": "amistad",  # 💛
        ":slightly_smiling_face:": "feliz",  # 🙂
        ":beating_heart:": "amor",  # 💓
        ":star-struck:": "fabuloso",  # 🤩
        ":grinning_face_with_smiling_eyes:": "sonreír",  # 😄
        ":grinning_face:": "sonreír",  # 😀
        ":grinning_face_with_big_eyes:": "feliz",  # 😃
        ":hundred_points:": "puntuación máxima",  # 💯
        ":see-no-evil_monkey:": "es una broma",  # 🙈
        ":backhand_index_pointing_down:": "apuntar",  # 👇
        ":musical_notes:": "musica",  # 🎶
        ":unamused_face:": "disgustado",  # 😒
        ":face_with_hand_over_mouth:": "la risa",  # 🤭
        ":heart_exclamation:": "corazon",  # ❣️
        ":exclamation_mark:": "importante",  # ❗
        ":winking_face_with_tongue:": "juguetón",  # 😜
        ":kiss_mark:": "beso",  # 💋
        ":eyes:": "curiosidad",  # 👀
        ":sleepy_face:": "sueno",  # 😪
        ":expressionless_face:": "indiferente",  # 😑
        ":collision:": "batida",  # 💥
        ":person_raising_hand:": "atencion",  # 🙋
        ":disappointed_face:": "decepcionado",  # 😞
        ":weary_face:": "cansado",  # 😩
        ":pouting_face:": "furioso",  # 😡
        ":zany_face:": "es una broma",  # 🤪
        ":oncoming_fist:": "golpeo",  # 👊
        ":sun_selector:": "sol",  # ☀️
        ":sad_but_relieved_face:": "triste",  # 😥
        ":drooling_face:": "deseo",  # 🤤
        ":backhand_index_pointing_right:": "apuntar",  # 👉
        ":woman_dancing:": "baile",  # 💃
        ":flushed_face:": "avergonzado",  # 😳
        ":raised_hand:": "atencion",  # ✋
        ":kissing_face_with_closed_eyes:": "beso",  # 😚
        ":squinting_face_with_tongue:": "es una broma",  # 😝
        ":sleeping_face:": "sueno",  # 😴
        ":glowing_star:": "estrella",  # 🌟
        ":grimacing_face:": "desangelado",  # 😬
        ":upside-down_face:": "bromista",  # 🙃
        ":four_leaf_clover:": "trébol",  # 🍀
        ":tulip:": "tulipan",  # 🌷
        ":smiling_cat_face_with_heart-eyes:": "enamorado",  # 😻
        ":downcast_face_with_sweat:": "decepcionado",  # 😓
        ":white_medium_star:": "estrella",  # ⭐
        ":white_heavy_check_mark:": "terminado",  # ✅
        ":rainbow:": "arcoiris",  # 🌈
        ":smiling_face_with_horns:": "malvado",  # 😈
        ":sign_of_the_horns:": "metal",  # 🤘
        ":sweat_droplets:": "churrete",  # 💦
        ":check_mark:": "terminado",  # ✔️
        ":persevering_face:": "exhausto ",  # 😣
        ":person_running:": "carrera",  # 🏃
        ":bouquet:": "flores",  # 💐
        ":frowning_face_selector:": "triste",  # ☹️
        ":confetti_ball:": "fiesta",  # 🎊
        ":heart_with_arrow:": "enamorado",  # 💘
        ":angry_face:": "enfurecido",  # 😠
        ":index_pointing_up_selector:": "atencion",  # ☝️
        ":confused_face:": "lioso",  # 😕
        ":hibiscus:": "flor",  # 🌺
        ":birthday_cake:": "cumpleanos",  # 🎂
        ":sunflower:": "girasol",  # 🌻
        ":neutral_face:": "indiferente",  # 😐
        ":middle_finger:": "rabia",  # 🖕
        ":heart_with_ribbon:": "regalo corazon",  # 💝
        ":speak-no-evil_monkey:": "secreto",  # 🙊
        ":cat_face_with_tears_of_joy:": "hahaha",  # 😹
        ":speaking_head_selector:": "hablar",  # 🗣️
        ":dizzy:": "mareo",  # 💫
        ":skull:": "calavera",  # 💀
        ":crown:": "corona",  # 👑
        ":musical_note:": "musica",  # 🎵
        ":crossed_fingers:": "ansioso",  # 🤞
        ":face_with_tongue:": "es una broma",  # 😛
        ":red_circle:": "circulo rojo",  # 🔴
        ":face_with_steam_from_nose:": "bravo",  # 😤
        ":blossom:": "flor",  # 🌼
        ":tired_face:": "cansado",  # 😫
        ":soccer_ball:": "pelota",  # ⚽
        ":call_me_hand:": "chachi",  # 🤙
        ":hot_beverage:": "bebida caliente",  # ☕
        ":trophy:": "vencedor",  # 🏆
        ":orange_heart:": "amistad",  # 🧡
        ":wrapped_gift:": "regalo",  # 🎁
        ":high_voltage:": "electricidad",  # ⚡
        ":sun_with_face:": "sol",  # 🌞
        ":balloon:": "globo",  # 🎈
        ":cross_mark:": "negacion",  # ❌
        ":raised_fist:": "puno",  # ✊
        ":waving_hand:": "adiós",  # 👋
        ":astonished_face:": "perplejo",  # 😲
        ":herb:": "planta",  # 🌿
        ":shushing_face:": "secreto",  # 🤫
        ":backhand_index_pointing_left:": "apuntar",  # 👈
        ":face_with_open_mouth:": "perplejo",  # 😮
        ":person_gesturing_OK:": "ok",  # 🙆
        ":clinking_beer_mugs:": "brindis",  # 🍻
        ":dog_face:": "perro",  # 🐶
        ":anxious_face_with_sweat:": "ansiedad",  # 😰
        ":face_with_raised_eyebrow:": "duda",  # 🤨
        ":face_without_mouth:": "mudo",  # 😶
        ":handshake:": "acuerdo",  # 🤝
        ":person_walking:": "caminar",  # 🚶
        ":money_bag:": "dinero",  # 💰
        ":strawberry:": "fresa",  # 🍓
        ":anger_symbol:": "batida",  # 💢
    }

    def __init__(self, remove_accent=True):
        super(PreprocessingSpanish, self).__init__(remove_accent=remove_accent)
