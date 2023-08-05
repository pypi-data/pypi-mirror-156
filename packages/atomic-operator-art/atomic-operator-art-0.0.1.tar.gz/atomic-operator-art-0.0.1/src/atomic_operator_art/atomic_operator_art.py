import os
import zipfile
from io import BytesIO

import requests

import atomic_operator

ATOMIC_RED_TEAM_REPO = 'https://github.com/redcanaryco/atomic-red-team/zipball/master/'


def download_atomic_red_team_repo(save_path, **kwargs) -> str:
    """Downloads the Atomic Red Team repository from github

    Args:
        save_path (str): The path to save the downloaded and extracted ZIP contents

    Returns:
        str: A string of the location the data was saved to.
    """
    response = requests.get(ATOMIC_RED_TEAM_REPO, stream=True, **kwargs)
    z = zipfile.ZipFile(BytesIO(response.content))
    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        for member in zf.infolist():
            file_path = os.path.realpath(os.path.join(save_path, member.filename))
            if file_path.startswith(os.path.realpath(save_path)):
                zf.extract(member, save_path)
    return z.namelist()[0]


@atomic_operator.hookimpl
def atomic_operator_get_content(value=os.getcwd(), **kwargs):
    """Downloads the RedCanary atomic-red-team repository to your local system.

    Args:
        destination (str, optional): A folder path to download the repository data to. Defaults to os.getcwd().
        kwargs (dict, optional): This kwargs will be passed along to Python requests library during download. Defaults to None.

    Returns:
        str: The path the data can be found at.
    """
    if not os.path.exists(destination):
        os.makedirs(destination)
    destination = kwargs.pop('destination') if kwargs.get('destination') else destination
    folder_name = download_atomic_red_team_repo(
        save_path=destination, 
        **kwargs
    )
    return os.path.join(destination, folder_name)
