import json
import os
from concurrent.futures import ThreadPoolExecutor

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from .constants import (
    CLIP_DELIMITER,
    CLIP_NUM_WORDS,
    HIGHLIGHT_CLIP_LENGTH,
    HIGHLIGHT_CLIP_OFFSET,
    TraversalType,
)
from .errors import JSONParseError
from .utils import (
    downloadVideo,
    linkToGameInfo,
    parseTimeAndDescription,
    stringToFilename,
)


class ClipHighlights:
    def __init__(
        self,
        highlights,
        clipDelimiter=CLIP_DELIMITER,
        clipNumWords=CLIP_NUM_WORDS,
        clipLength=HIGHLIGHT_CLIP_LENGTH,
        clipOffset=HIGHLIGHT_CLIP_OFFSET,
    ):
        self.highlights = highlights
        self.clipDelimiter = clipDelimiter
        self.clipNumWords = clipNumWords
        self.clipLength = clipLength
        self.clipOffset = clipOffset

        self.__validateJSON()

    def __validateJSON(self):
        try:
            tournaments = list(self.highlights.values())[0]
            for tournament, games in tournaments.items():
                for gameLink, timestamps in games.items():
                    try:
                        linkToGameInfo(gameLink)
                    except ValueError:
                        raise JSONParseError(
                            f"{gameLink} from {tournament} is not in the right format."
                            " Is it formatted as a markdown link correctly?"
                        )
                    for timestamp in timestamps:
                        try:
                            parseTimeAndDescription(timestamp, self.clipDelimiter)
                        except ValueError:
                            raise JSONParseError(
                                f"{timestamp} in {gameLink} from {tournament} is not"
                                " in the right format. Did you use the correct"
                                f' delimiter ("{self.clipDelimiter}") between the'
                                " timestamp and the description?"
                            )
        except Exception:
            raise JSONParseError(
                "The JSON provided does not have the correct structure."
                " See the previous error in the callback for more information."
                " Otherwise, please refer to the JSON specification in the README"
                " and try again."
            )

    def makeClipsFromFilm(self, outputPath, filmFilename, timestamps):
        filmFullPath = os.path.join(outputPath, filmFilename)

        for timestampStr in timestamps:
            seconds, description = parseTimeAndDescription(
                timestampStr, self.clipDelimiter
            )
            firstNDescriptionWords = " ".join(
                description.split(" ")[: self.clipNumWords]
            )
            clipName = stringToFilename(firstNDescriptionWords) + ".mp4"
            clipFullPath = os.path.join(outputPath, clipName)

            # don't clip highlight if it has already been done previously
            if not os.path.exists(clipFullPath):
                print(f"Writing {clipFullPath}")

                ffmpeg_extract_subclip(
                    filmFullPath,
                    seconds - self.clipOffset,
                    seconds - self.clipOffset + self.clipLength,
                    targetname=clipFullPath,
                )
            else:
                print(f"Skipping {clipFullPath} because it already exists")

    def traverseHighlights(self, traversalType, threading=True):
        saveStorage = False
        if traversalType == TraversalType.SAVE_STORAGE:
            saveStorage = True
            threading = False

        mainKey, tournaments = list(self.highlights.items())[0]
        mainDirectory = stringToFilename(mainKey)

        # to use threading when downloading full games
        with ThreadPoolExecutor() as executor:
            # loop through tournaments
            for tournament, games in tournaments.items():
                tournamentPath = os.path.join(
                    mainDirectory, stringToFilename(tournament)
                )

                # loop through games in tournament
                for gameLink, timestamps in games.items():
                    gameName, gameURL = linkToGameInfo(gameLink)

                    gameName = stringToFilename(gameName)
                    gamePath = os.path.join(tournamentPath, gameName)
                    filmFile = f"{gameName}.mp4"
                    fullFilmPath = os.path.join(gamePath, filmFile)

                    if traversalType == TraversalType.CREATE_DIRS or saveStorage:
                        if not os.path.exists(gamePath):
                            print(f"Creating {gamePath} directory.")
                            os.makedirs(gamePath)

                    if (
                        traversalType == TraversalType.DOWNLOAD_FULL_GAMES
                        or saveStorage
                    ):
                        # don't try to download video if it has already previously been
                        # downloaded (yt-dlp already has this functionality but best to
                        # avoid starting a new thread altogether)
                        if not os.path.exists(fullFilmPath):
                            if threading:
                                # create and start thread to download game
                                executor.submit(
                                    downloadVideo,
                                    gameURL,
                                    filmFile,
                                    outputPath=gamePath,
                                )
                            else:
                                # download game sequentially (will take much longer)
                                downloadVideo(gameURL, filmFile, outputPath=gamePath)
                        else:
                            print(f"{fullFilmPath} already exists, skipping download")
                    if traversalType == TraversalType.CLIP_HIGHLIGHTS or saveStorage:
                        # don't try to clip highlights if full game film is not in directory
                        # (presumably due to issue with download)
                        if os.path.exists(fullFilmPath):
                            print(f"Clipping highlights from {fullFilmPath}:")
                            self.makeClipsFromFilm(gamePath, filmFile, timestamps)
                        else:
                            print(
                                f"{fullFilmPath} not found, skipping clipping highlights..."
                            )

                    if traversalType == TraversalType.DELETE_FULL_GAMES or saveStorage:
                        filmFilePath = os.path.join(gamePath, filmFile)
                        if os.path.exists(filmFilePath):
                            print(f"Deleting {filmFilePath}.")
                            os.remove(filmFilePath)
