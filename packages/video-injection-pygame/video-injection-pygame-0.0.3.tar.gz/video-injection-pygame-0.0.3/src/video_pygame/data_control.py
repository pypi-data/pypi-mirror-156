import os, glob


def get_data_folder_path() -> str:
    """
    get data folder path to use
    """

    string_path = ''

    list_path = os.path.dirname(os.path.abspath(__file__)).split('\\')
    list_path.pop(-1)

    for part in list_path:
        string_path += '%s\\' % part

    string_path += 'data'

    return string_path


class DataControl(object):
    """
    used to control data saved inside
    of /data folder (frames are saved in there)
    """

    # data folder path
    __DATA_PATH = get_data_folder_path()

    def create_folder(name) -> str:
        """
        create a new folder in /data to store frames in
        """

        new_folder_path = DataControl.__DATA_PATH + '\\%s' % name
        
        if os.path.exists(new_folder_path):
            return new_folder_path

        os.mkdir(new_folder_path)

        return new_folder_path

    def folder_is_empty(path: str) -> bool:
        """
        check if folder is empty or not
        """

        if len(os.listdir(path)) == 0:
            return True
        
        return False

    def clear_folder(path: str) -> None:
        """
        empty a folder
        """

        files = glob.glob('%s\\*' % path)
        for f in files:
            os.remove(f)
