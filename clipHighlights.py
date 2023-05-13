import json
import os
import re
import sys
import time

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from pytube import YouTube

# length of each highlight clip in seconds
HIGHLIGHT_CLIP_LENGTH = 10
# offset from the marked timestamp to start a highlight in seconds
# (so a value of 2 means start the clip 2 seconds before the marked timestamp)
HIGHLIGHT_CLIP_OFFSET = 2
# number of words from timestamp description to include in the clip's filename
CLIP_NUM_WORDS = 4


def stringToFilename(str):
    """Convert arbitrary string to filename-safe representation (i.e. no spaces or non-ASCII characters)"""

    retStr = ""

    for character in str:
        if character == " ":
            retStr += "_"
        elif character.isalnum() or character == "-":
            retStr += character

    return retStr


def linkToGameInfo(linkStr):
    """Return tuple of the form (link name, link address) from Markdown link"""

    titlePattern = re.compile(r"(\[)(.*?)(\])")
    urlPattern = re.compile(r"(\()(.*?)(\))")
    title = titlePattern.search(linkStr)
    url = urlPattern.search(linkStr)
    if title is not None and url is not None:
        return (title.group(2), url.group(2))
    else:
        raise IndexError(f"Title and URL parsing failed for {linkStr}.")


def downloadVideo(url, outputFile, outputPath=None):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()

    if stream is not None:
        print(f"Beginning download of {yt.title}, this may take a while...")
        stream.download(output_path=outputPath, filename=outputFile)
        print(f"{yt.title} successfully downloaded.")
    else:
        print(f"No streams found for {yt.title}.")


def makeClipsFromFilm(outputPath, filmFilename, timestamps):
    filmFullPath = os.path.join(outputPath, filmFilename)

    for timestampStr in timestamps:
        timestamp, description = tuple(timestampStr.split("- "))
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


def main():
    with open(sys.argv[1]) as f:
        highlights = json.load(f)

    # mainKey is top-level key (usually just says "season highlights")
    mainKey, tournaments = list(highlights.items())[0]
    mainDirectory = stringToFilename(mainKey)

    if not os.path.exists(mainDirectory):
        os.makedirs(mainDirectory)

    for tournament, games in tournaments.items():
        tournamentPath = os.path.join(mainDirectory, stringToFilename(tournament))
        os.makedirs(tournamentPath)

        for gameLink, timestamps in games.items():
            gameName, gameUrl = linkToGameInfo(gameLink)

            print(f"\n------------\n\nProcessing {gameName} game from {tournament}:\n")

            gameName = stringToFilename(gameName)
            gamePath = os.path.join(tournamentPath, gameName)

            os.makedirs(gamePath)
            filmFile = f"{gameName}.mp4"

            downloadVideo(gameUrl, filmFile, gamePath)
            makeClipsFromFilm(gamePath, filmFile, timestamps)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main()
    else:
        print(f"USAGE: python3 {sys.argv[0]} /path/to/highlights.json")
