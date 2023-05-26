import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from yt_dlp import YoutubeDL

# length of each highlight clip in seconds
HIGHLIGHT_CLIP_LENGTH = 10
# offset from the marked timestamp to start a highlight in seconds
# (so a value of 2 means start the clip 2 seconds before the marked timestamp)
HIGHLIGHT_CLIP_OFFSET = 2
# number of words from timestamp description to include in the clip's filename
CLIP_NUM_WORDS = 4


class TraversalType(Enum):
    CREATE_DIRS = 1
    DOWNLOAD_FULL_GAMES = 2
    CLIP_HIGHLIGHTS = 3
    DELETE_FULL_GAMES = 4
    SAVE_STORAGE = 5


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
            raise IndexError(f"Title and URL parsing failed for {linkStr}.")
    else:
        raise IndexError(f"Title and URL parsing failed for {linkStr}.")


def downloadVideo(url, outputFile, outputPath=""):
    # note that this does not raise an exception if the download fails (but it does
    # print that it failed in the output)
    opts = {
        "format": "mp4",
        "outtmpl": {"default": outputFile},
        "paths": {"home": outputPath},
    }
    with YoutubeDL(opts) as ydl:
        ydl.download(url)


def makeClipsFromFilm(outputPath, filmFilename, timestamps):
    filmFullPath = os.path.join(outputPath, filmFilename)

    for timestampStr in timestamps:
        # only split at the first occurrence of "- "
        timestamp, description = tuple(timestampStr.split("- ", 1))
        timeObj = time.strptime(timestamp, "%M:%S")
        seconds = timeObj.tm_min * 60 + timeObj.tm_sec - HIGHLIGHT_CLIP_OFFSET
        firstNDescriptionWords = " ".join(description.split(" ")[:CLIP_NUM_WORDS])
        clipName = stringToFilename(firstNDescriptionWords) + ".mp4"
        clipFullPath = os.path.join(outputPath, clipName)
        print(f"Writing {clipFullPath}")

        ffmpeg_extract_subclip(
            filmFullPath,
            seconds,
            seconds + HIGHLIGHT_CLIP_LENGTH,
            targetname=clipFullPath,
        )


def traverseHighlights(highlights, traversalType, threading=True):
    saveStorage = False
    if traversalType == TraversalType.SAVE_STORAGE:
        saveStorage = True
        threading = False

    mainKey, tournaments = list(highlights.items())[0]
    mainDirectory = stringToFilename(mainKey)

    # to use threading when downloading full games
    with ThreadPoolExecutor() as executor:
        # loop through tournaments
        for tournament, games in tournaments.items():
            tournamentPath = os.path.join(mainDirectory, stringToFilename(tournament))

            # loop through games in tournament
            for gameLink, timestamps in games.items():
                gameName, gameURL = linkToGameInfo(gameLink)

                gameName = stringToFilename(gameName)
                gamePath = os.path.join(tournamentPath, gameName)
                filmFile = f"{gameName}.mp4"

                if traversalType == TraversalType.CREATE_DIRS or saveStorage:
                    print(f"Creating {gamePath} directory.")
                    os.makedirs(gamePath)

                if traversalType == TraversalType.DOWNLOAD_FULL_GAMES or saveStorage:
                    if threading:
                        # create and start thread to download game
                        executor.submit(
                            downloadVideo, gameURL, filmFile, outputPath=gamePath
                        )
                    else:
                        # download game sequentially (will take much longer)
                        downloadVideo(gameURL, filmFile, outputPath=gamePath)

                if traversalType == TraversalType.CLIP_HIGHLIGHTS or saveStorage:
                    print(f"Clipping {gameName} highlights from {tournament}:")
                    makeClipsFromFilm(gamePath, filmFile, timestamps)

                if traversalType == TraversalType.DELETE_FULL_GAMES or saveStorage:
                    filmFilePath = os.path.join(gamePath, filmFile)
                    print(f"Deleting {filmFilePath}.")
                    os.remove(filmFilePath)


def main():
    with open(sys.argv[1]) as f:
        highlights = json.load(f)

    # TODO: turn this into a class and have highlights be a member variable
    traverseHighlights(highlights, TraversalType.CREATE_DIRS)
    traverseHighlights(highlights, TraversalType.DOWNLOAD_FULL_GAMES)
    traverseHighlights(highlights, TraversalType.CLIP_HIGHLIGHTS)

    # traverseHighlights(highlights, TraversalType.SAVE_STORAGE)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main()
    else:
        print(f"USAGE: python3 {sys.argv[0]} /path/to/highlights.json")
