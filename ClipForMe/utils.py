import os
import re
import time
from datetime import datetime

from markdown_to_json.scripts.md_to_json import jsonify_markdown
from yt_dlp import YoutubeDL


def convertHighlights(markdownFile, outputFile=None):
    # Convert markdown highlight timestamps to JSON for easier parsing later
    if outputFile is None:
        date = datetime.now().strftime("%-m-%-d-%Y")
        outputFile = f"highlights_{date}.json"
    jsonify_markdown(markdownFile, outputFile, 2)
    print(f"{outputFile} created in current directory.")


def stringToFilename(str):
    """Convert arbitrary string to filename-safe representation (i.e. no spaces or non-ASCII characters)"""

    retStr = ""

    for character in str:
        if character == " ":
            retStr += "_"
        elif character.isalnum() or character == "-":
            retStr += character

    # return just an underscore if there are no safe characters in the string
    return retStr or "_"


def linkToGameInfo(linkStr):
    """Return tuple of the form (link name, link address) from Markdown link"""

    titlePattern = re.compile(r"(\[)(.*?)(\])")
    urlPattern = re.compile(r"(\()(.*?)(\))")
    title = titlePattern.search(linkStr)

    if title is not None:
        secondStr = linkStr[title.end() :]
        url = urlPattern.search(secondStr)
        if url is not None:
            return (title.group(2), url.group(2))
        else:  # TODO: fix error handling
            raise ValueError(f"Title and URL parsing failed for {linkStr}.")
    else:
        raise ValueError(f"Title and URL parsing failed for {linkStr}.")


def downloadVideo(url, outputFile, outputPath=""):
    # note that this does not raise an exception if the download fails (but it does
    # print that it failed in the output)
    opts = {
        "format": "mp4",
        "outtmpl": {"default": outputFile},
        "paths": {"home": outputPath},
    }
    fullPath = os.path.join(outputPath, outputFile)
    print(f"Beginning download of {fullPath}, this may take a while...")

    try:
        with YoutubeDL(opts) as ydl:
            ydl.download(url)
        print(f"{fullPath} successfully downloaded.")
    except Exception:
        print(
            f"Error downloading {fullPath}. This game will be skipped when clipping highlights."
        )


def parseTimeAndDescription(highlightLine, delimiter):
    # only split at the first occurrence of delimiter
    timestamp, description = tuple(highlightLine.split(delimiter, 1))
    timeObj = None
    seconds = 0

    # try to parse MM:SS format first, then HH:MM:SS
    try:
        timeObj = time.strptime(timestamp, "%M:%S")
    except ValueError:
        timeObj = time.strptime(timestamp, "%H:%M:%S")
        seconds += timeObj.tm_hour * 3600

    seconds += timeObj.tm_min * 60 + timeObj.tm_sec

    return seconds, description
