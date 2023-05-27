import json
import os
from concurrent.futures import ThreadPoolExecutor

from ClipForMe.constants import CLIP_DELIMITER, TraversalType
from ClipForMe.errors import JSONParseError
from ClipForMe.utils import (
    downloadVideo,
    linkToGameInfo,
    makeClipsFromFilm,
    parseTimeAndDescription,
    stringToFilename,
)


class ClipHighlights:
    def __init__(self, highlights):
        self.highlights = highlights
        self.__validateJSON()

    @classmethod
    def fromFile(cls, filePath):
        with open(filePath) as f:
            return cls(json.load(f))

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
                            parseTimeAndDescription(timestamp)
                        except ValueError:
                            raise JSONParseError(
                                f"{timestamp} in {gameLink} from {tournament} is not"
                                " in the right format. Did you use the correct"
                                f' delimiter ("{CLIP_DELIMITER}") between the'
                                " timestamp and the description?"
                            )
        except Exception:
            raise JSONParseError(
                "The JSON provided does not have the correct structure."
                " See the previous error in the callback for more information."
                " Otherwise, please refer to the JSON specification in the README"
                " and try again."
            )

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
                            makeClipsFromFilm(gamePath, filmFile, timestamps)
                        else:
                            print(
                                f"{fullFilmPath} not found, skipping clipping highlights..."
                            )

                    if traversalType == TraversalType.DELETE_FULL_GAMES or saveStorage:
                        filmFilePath = os.path.join(gamePath, filmFile)
                        if os.path.exists(filmFilePath):
                            print(f"Deleting {filmFilePath}.")
                            os.remove(filmFilePath)
