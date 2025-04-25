import datetime
from typing import Dict, Optional

from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytubefix.exceptions import VideoUnavailable


def get_youtube(
    url: str,
    output_path: str,
    verbose=True,
    youtube_args: Optional[Dict] = None,
    dl_args: Optional[Dict] = None,
):
    """Download the audio portion of a youtube video given a valid youtube url

    Args:
        url (str): Url of the youtube video
        output_path (str): Output path of the downloaded file
        verbose (bool, optional): Whether to print information during download. Defaults to True.
        youtube_args (dict, optional): Arguments to feed into the main youtube downloader objects, see docs [here](https://pytubefix.readthedocs.io/en/latest/api.html#youtube-object)
        dl_args (dict, optional): Additional arguments to feed into the stream download method, see docs [here](https://pytube.io/en/latest/api.html#pytube.Stream.download)

    Returns:
        str: File path of the downloaded file

    """
    youtube_args = youtube_args or dict()
    dl_args = dl_args or dict()

    # Set up function to show progress bar if verbose
    on_progress_fn = on_progress if verbose else None

    # Attempt to get video from url
    try:
        yt = YouTube(url, on_progress_callback=on_progress_fn, **youtube_args)
    except VideoUnavailable:
        raise ValueError(
            f"Cannot obtain media from {url}, please check if url is valid"
        )

    # Print info if verbose
    if verbose:
        show_info(yt)

    # Obtaining audio only
    ys = yt.streams.get_audio_only()

    # Set default download arguments
    default_dl_args = {"output_path": output_path, "skip_existing": True, "mp3": True}

    # Update default arguments with user-provided arguments
    if dl_args:
        default_dl_args.update(dl_args)

    # Downloads media and obtaining it's path
    file_path = ys.download(
        output_path=output_path, skip_existing=True, mp3=True, **dl_args
    )

    return file_path


def show_info(yt: YouTube, date_format: str = "%d/%m/%y %H:%M:%S"):
    """Shows selected info for obtained youtube video

    Args:
        yt (YouTube): Youtube object (from pytubefix)
        date_format: String to formate the date output, please refer to [datetime_documentation](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    """
    print(f"Title: {yt.title}")
    print(f"Upload date: {yt.publish_date.strftime(date_format)}")
    print(f"Time length: {str(datetime.timedelta(seconds=yt.length))}")
