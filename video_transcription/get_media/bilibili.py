"""Provides a wrapper over a DownloaderBilibili object to download bilibili videos

There is no way to get the file path directly, see the [source code](https://github.com/HFrost0/bilix/blob/bb5b234cdfe3fafc4db9d992b91091f2edf791e5/bilix/sites/bilibili/downloader.py#L314)

we use the following workaround instead (very hacky):
- Create a new temp folder (with a unique randomized name)
- Download the media inside the folder, now it only contains 1 file
- Obtain the name of the file
- Move the file back to the parent file and then delete the temp folder
"""

import asyncio
import os
import shutil
from time import time
from typing import Dict, Optional

from bilix.sites.bilibili import DownloaderBilibili

# Reusable global instance,
bili = DownloaderBilibili()


# TODO: Doc string
# TODO: set up collision stratergies (rename, replace, )
def get_bilibili(url: str, output_path: str, bili_args: Optional[Dict] = None):
    """Download a bilibili video given a valid youtube url

    Args:
        url (str): URL of the bilibili video
        output_path (str): The file path of where to provide the video
        bili_args (Optional[Dict], optional): Arguments to provide to the inner DownloaderBilibili object. Defaults to None.

    Returns:
        str: File path of the downloaded file
    """
    temp_output_path = os.path.join(output_path, get_random_name())

    os.makedirs(temp_output_path)

    # Downloads the video
    asyncio.run(
        download_from_bilibili(
            url=url, output_path=temp_output_path, bili_args=bili_args
        )
    )

    original_filename = os.listdir(temp_output_path)[
        0
    ]  # only 1 object in the temp folder

    destination_filename = str(original_filename)

    while os.path.exists(os.path.join(output_path, destination_filename)):
        base_name, extension = os.path.splitext(destination_filename)
        destination_filename = base_name + " - copy" + extension

    file_path_temp = os.path.join(temp_output_path, original_filename)
    file_path_dest = os.path.join(output_path, destination_filename)

    shutil.move(file_path_temp, file_path_dest)

    # Delete the temp folder after moving the file
    shutil.rmtree(temp_output_path)

    return file_path_dest


async def download_from_bilibili(url: str, output_path: str, bili_args):
    await bili.get_video(url=url, path=output_path, only_audio=True, **bili_args)
    return


def get_random_name(prefix: str = "temp", name_length: int = 32):
    """Creates a psudo random name consisting of a prefix and a hex string of specified length

    Args:
        prefix (str, optional): prefix of the returned name. Defaults to "temp_".
        name_length (int, optional): length of the randomized hex string. Defaults to 32 (corrected to nearest even number).

    Returns:
        str: A randomized name
    """

    return "_".join((prefix, str(int(time())), os.urandom(name_length / 2).hex()))
