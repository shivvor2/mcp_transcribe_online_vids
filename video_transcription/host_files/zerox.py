import logging
import os

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_file_to_zerox(file_path: str, timeout: int = 600) -> str:
    """
    Upload a file to 0x0.st and return the URL

    Args:
        file_path (str): Path to the file to upload
        timeout (int): Upload timeout in seconds, defaults to 60 seconds

    Returns:
        str: URL of the uploaded file
    """
    filename = os.path.basename(file_path)
    logger.info(f"Uploading file: {filename}")

    with open(file_path, "rb") as f:
        response = requests.post(
            os.getenv("ZERO_X_URL"),
            files={"file": (filename, f, "audio/wav")},
            timeout=timeout,
        )

    response.raise_for_status()
    url = response.text.strip()
    logger.info(f"Successfully uploaded to {url}")

    return url
