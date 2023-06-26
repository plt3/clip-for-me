import os
import re
import time
from datetime import datetime

from markdown_to_json.scripts.md_to_json import jsonify_markdown
from yt_dlp import YoutubeDL


def convert_highlights(markdownFile, output_file=None):
    # Convert markdown highlight timestamps to JSON for easier parsing later
    if output_file is None:
        date = datetime.now().strftime("%-m-%-d-%Y")
        output_file = f"highlights_{date}.json"
    jsonify_markdown(markdownFile, output_file, 2)
    print(f"{output_file} created in current directory.")


def string_to_filename(s):
    """Convert arbitrary string to filename-safe representation (i.e. no spaces or non-ASCII characters)"""

    ret_str = ""

    for character in s:
        if character == " ":
            ret_str += "_"
        elif character.isalnum() or character == "-":
            ret_str += character

    # return just an underscore if there are no safe characters in the string
    return ret_str or "_"


def link_to_game_info(link_str):
    """Return tuple of the form (link name, link address) from Markdown link"""

    title_url_pattern = re.compile(r"\[(.+?)\]\((.+?)\)")
    match = title_url_pattern.search(link_str)

    if match is not None:
        return (match.group(1), match.group(2))
    else:
        raise ValueError(f"Title and URL parsing failed for {link_str}.")


def download_video(url, output_file, output_path=""):
    # note that this does not raise an exception if the download fails (but it does
    # print that it failed in the output)
    opts = {
        "format": "mp4",
        "outtmpl": {"default": output_file},
        "paths": {"home": output_path},
    }
    full_path = os.path.join(output_path, output_file)
    print(f"Beginning download of {full_path}, this may take a while...")

    try:
        with YoutubeDL(opts) as ydl:
            ydl.download(url)
        print(f"{full_path} successfully downloaded.")
    except Exception:
        print(
            f"Error downloading {full_path}. This game will be skipped when clipping highlights."
        )


def parse_time_and_description(highlight_line, delimiter):
    # only split at the first occurrence of delimiter
    timestamp, description = tuple(highlight_line.split(delimiter, 1))
    time_obj = None
    seconds = 0

    # try to parse MM:SS format first, then HH:MM:SS
    try:
        time_obj = time.strptime(timestamp, "%M:%S")
    except ValueError:
        time_obj = time.strptime(timestamp, "%H:%M:%S")
        seconds += time_obj.tm_hour * 3600

    seconds += time_obj.tm_min * 60 + time_obj.tm_sec

    return seconds, description
