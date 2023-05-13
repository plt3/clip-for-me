import json
import os
import re
import sys

from pytube import YouTube


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
    else:
        print(f"No streams found for {yt.title}.")


def main():
    with open(sys.argv[1]) as f:
        highlights = json.load(f)

    mainDirectory = stringToFilename(list(highlights.keys())[0])

    if not os.path.exists(mainDirectory):
        os.makedirs(mainDirectory)

    for tournament, games in list(highlights.values())[0].items():
        tournamentPath = os.path.join(mainDirectory, stringToFilename(tournament))
        os.makedirs(tournamentPath)

        for gameLink in games:
            gameName, gameUrl = linkToGameInfo(gameLink)
            gamePath = os.path.join(tournamentPath, stringToFilename(gameName))
            os.makedirs(gamePath)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main()
    else:
        print(f"USAGE: python3 {sys.argv[0]} /path/to/highlights.json")
