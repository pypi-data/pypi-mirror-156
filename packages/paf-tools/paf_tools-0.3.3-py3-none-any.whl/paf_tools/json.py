import json
import os.path


def read(path, in_app_path=False, is_config_file=False):
    """
    if (inAppPath)
    {
      path = Path.Combine(Directory.GetCurrentDirectory(), path);
    }
    """
    if is_config_file is True:
        path = os.path.join(r'C:\AS_Programme\Configuration', path)

    if os.path.exists(path) is False:
        raise FileNotFoundError

    try:
        with open(path) as json_file:
            return json.loads(json_file.read())
    except Exception as ex:
        print(ex)


def write(data, path, in_app_path=False, is_config_file=False):
    '''
    if (inAppPath)
    {
      path = Path.Combine(Directory.GetCurrentDirectory(), path);
    }
    '''
    if is_config_file is True:
        path = os.path.join(r'C:\AS_Programme\Configuration', path)

    with open(path) as json_file:
        json.dump(data, json_file)
