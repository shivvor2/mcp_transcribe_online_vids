import time
from typing import Any, Dict, List


def reformat_segments(inputs: List[Dict[Any, Any]]):
    """
    Reformats a list of transcript dictionaries into a single formatted string.

    Args:
        inputs (List[Dict[Any, Any]]): List of dictionaries containing transcript segments,where each dictionary has 'start', 'end', and 'text' keys.

    Returns:
        str: A formatted string with all transcript segments, including timestamps and text, separated by newlines.
    """
    input_list = [reformat_one(input) for input in inputs]
    processed_text = "\n".join(input_list)
    return processed_text


def reformat_one(input: Dict[Any, Any]):
    """
    Reformats a list of transcript dictionaries into a single formatted string.

    Args:
        inputs (List[Dict[Any, Any]]): List of dictionaries containing transcript segments, where each dictionary has 'start', 'end', and 'text' keys.

    Returns:
        str: A formatted string with all transcript segments, including timestamps and text, separated by newlines.
    """
    formatted_text = ""
    input_fields = input.keys()
    if "start" in input_fields:
        start_time = time.strftime("%H:%M:%S", time.gmtime(input["start"]))
        start_string = f"Start: {start_time} - "
        formatted_text += start_string
    if "end" in input_fields:
        end_time = time.strftime("%H:%M:%S", time.gmtime(input["end"]))
        end_string = f"End: {end_time}\n"
        formatted_text += end_string
    if "text" in input_fields:
        formatted_text += input["text"]
    return formatted_text
