ACTION_PARSE = 'parse'
ACTION_TRAIN = 'train'


def queue_name(action, language):
    return '{}:{}'.format(action, language)
