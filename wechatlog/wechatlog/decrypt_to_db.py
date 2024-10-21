from pywxdump.wx_info.get_wx_info import read_info
from pywxdump.wx_info.merge_db import decrypt_merge

# Read WeChat info


def get_wx_info():
    wx_info_list = read_info()
    # Parse the list into a dictionary
    wx_info_dict = {}
    if wx_info_list and isinstance(wx_info_list, list) and len(wx_info_list) > 0:
        # Assuming we want the first item if there are multiple
        wx_info_dict = wx_info_list[0]
    return wx_info_dict


if __name__ == "__main__":
    # if output directory is not empty it will override it
    output_path = r"c:\Users\88the\OneDrive\Desktop\wechatlog-export-module\test_output"
    wx_info = get_wx_info()
    print(wx_info)
    print('began decrypt')
    code, save_path = decrypt_merge(wx_path=wx_info['filePath'],
                                    key=wx_info['key'],
                                    outpath=output_path)
    if code:
        print(f'decrypt finished save_path: {save_path}')
    else:
        print(f'decrypt failed')
    # need to test and figure out following error
    # TODO: test if output_path not exist
    # TODO: test if output_path is not empty
    # TODO: test if wx_path is not exist
    # TODO: test if db in wx_path is not exist
    # TODO: test if key is wrong

