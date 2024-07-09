'''
generate a text description of the content of message
'''


def text(content):
    return f'a text message says "{content["msg"]}"'


def image(_):
    return 'an image'


def voice(content):
    duration = content.get('duration', 'unkown')
    transcription = content.get('transcription', 'no transcription')
    return f"a {duration} seconds audio with transcription: '{transcription}'"


def video(_):
    return 'a video'


def emoji(_):
    return 'an emoji'


def file(_):
    return 'a file'


def forwarded_message(content):
    title = content.get('title', 'no title')
    des = content.get('des', 'no description')
    return f"a forwarded '{title}' and the contents are '{des}'"


def quoted_message(content):
    ref_description = content.get('ref_desc', 'no description')
    reply_with = content.get('reply_with', 'empty content')
    # reply_to = content.get('reply_to', 'empty content')
    reply_to_name = content.get('reply_to_name', 'unkown name')
    return f"reply {reply_to_name}'s message '{ref_description}' with '{reply_with}'"


def transfer(content):
    amount = content.get('amount', 'unkown amount')
    return f"a transfer of {amount}"


def card(content):
    title = content.get('title', 'no title')
    des = content.get('des', 'no description')
    sourcedisplayname = content.get('sourcedisplayname', 'unkown source')
    return f"a article written by {sourcedisplayname}, with title '{title}', and description '{des}'"


def contact_card(content):
    wxid = content.get('username', 'unkown wxid')
    nickname = content.get('nickname', 'unkown nickname')
    full_displayname = content.get(
        'full_displayname', 'unkown full displayname')
    return f"a contact card of {full_displayname}({nickname}) with wxid {wxid}"

def other_type(content):
    return content.get('msg', 'unkown message')

def audio_call(_):
    return 'an audio call'
