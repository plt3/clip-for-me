from enum import Enum


# type specify what to do when traversing highlight directories in
# ClipHighlights.traverseHighlights()
class TraversalType(Enum):
    CREATE_DIRS = 1
    DOWNLOAD_FULL_GAMES = 2
    CLIP_HIGHLIGHTS = 3
    DELETE_FULL_GAMES = 4
    SAVE_STORAGE = 5


# length of each highlight clip in seconds
HIGHLIGHT_CLIP_LENGTH = 10
# offset from the marked timestamp to start a highlight in seconds
# (so a value of 2 means start the clip 2 seconds before the marked timestamp)
HIGHLIGHT_CLIP_OFFSET = 2
# number of words from timestamp description to include in the clip's filename
CLIP_NUM_WORDS = 4
# delimiter between timestamp and clip description in each highlight line in JSON
CLIP_DELIMITER = "- "
