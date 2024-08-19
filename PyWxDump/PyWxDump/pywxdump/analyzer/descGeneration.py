def get_text_desc(content: dict) -> str:
    """
    raise ValueError Exception when 
    msg not in content
    """
    if 'msg' not in content:
        raise ValueError("this text type doesn't have msg field")
    return content['msg']


def get_img_desc(content: dict) -> str:
    if 'src' not in content:
        raise ValueError("") 