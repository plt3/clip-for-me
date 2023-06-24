import argparse
import json

from . import ClipHighlights
from .constants import (
    CLIP_DELIMITER,
    CLIP_NUM_WORDS,
    HIGHLIGHT_CLIP_LENGTH,
    HIGHLIGHT_CLIP_OFFSET,
    TraversalType,
)
from .utils import convertHighlights


def convertFunc(argsNamespace):
    convertHighlights(argsNamespace.file, outputFile=argsNamespace.output_file)


def traverseFunc(argsNamespace):
    with open(argsNamespace.file) as f:
        # if clip_num_words is specified, then other two are also
        if hasattr(argsNamespace, "clip_num_words"):
            clipObj = ClipHighlights(
                json.load(f),
                clipDelimiter=argsNamespace.delimiter,
                clipNumWords=argsNamespace.clip_num_words,
                clipLength=argsNamespace.clip_length,
                clipOffset=argsNamespace.clip_offset,
            )
        else:
            clipObj = ClipHighlights(
                json.load(f), clipDelimiter=argsNamespace.delimiter
            )

    clipObj.traverseHighlights(argsNamespace.traversalType)

    return clipObj


def downloadFunc(argsNamespace):
    setattr(argsNamespace, "traversalType", TraversalType.CREATE_DIRS)
    clipObj = traverseFunc(argsNamespace)
    clipObj.traverseHighlights(
        TraversalType.DOWNLOAD_FULL_GAMES, threading=not argsNamespace.no_threading
    )

    return clipObj


def allFunc(argsNamespace):
    if argsNamespace.save_storage:
        setattr(argsNamespace, "traversalType", TraversalType.SAVE_STORAGE)
        traverseFunc(argsNamespace)
    else:
        clipObj = downloadFunc(argsNamespace)
        clipObj.traverseHighlights(TraversalType.CLIP_HIGHLIGHTS)


def addClipOptions(subparser, justDelimiter=False):
    subparser.add_argument(
        "-d",
        "--delimiter",
        help='Delimiter between timestamp and description of each highlight (default "%(default)s")',
        default=CLIP_DELIMITER,
    )
    if not justDelimiter:
        subparser.add_argument(
            "-n",
            "--clip-num-words",
            type=int,
            help="Number of words to take from beginning of highlight description to"
            " make name of file (default %(default)s)",
            default=CLIP_NUM_WORDS,
        )
        subparser.add_argument(
            "-l",
            "--clip-length",
            type=int,
            help="Length of each highlight clip in seconds (default %(default)s)",
            default=HIGHLIGHT_CLIP_LENGTH,
        )
        subparser.add_argument(
            "-o",
            "--clip-offset",
            type=int,
            help="Offset of each highlight clip from marked timestamp in seconds (default %(default)s)",
            default=HIGHLIGHT_CLIP_OFFSET,
        )


def parserSetup():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and clip timestamps from them by writing Markdown",
    )
    subparsers = parser.add_subparsers(title="subcommands")

    fileCommand = {"dest": "file", "help": "path to JSON file"}

    # convert subcommand
    convert = subparsers.add_parser("convert", help="Convert Markdown file to JSON")
    convert.add_argument("file", help="path to Markdown file to convert")
    convert.add_argument(
        "-o",
        "--output-file",
        help="name of JSON file to store highlights in",
    )
    convert.set_defaults(func=convertFunc)

    # makedirs subcommand
    makeDirs = subparsers.add_parser(
        "makedirs", help="Make directory structure representing JSON"
    )
    makeDirs.add_argument(**fileCommand)
    addClipOptions(makeDirs, justDelimiter=True)
    makeDirs.set_defaults(traversalType=TraversalType.CREATE_DIRS, func=traverseFunc)

    # download subcommand
    download = subparsers.add_parser(
        "download",
        help="Download YouTube videos from JSON and put them in appropriate directories",
    )
    download.add_argument(**fileCommand)
    download.add_argument(
        "-t",
        "--no-threading",
        help="Specify to avoid using multithreading to download YouTube videos."
        " This may decrease performance drastically.",
        action="store_true",
    )
    addClipOptions(download, justDelimiter=True)
    download.set_defaults(func=downloadFunc)

    # clip subcommand
    clip = subparsers.add_parser(
        "clip",
        help="Clip highlights from already-downloaded videos present in directories"
        " corresponding to JSON structure",
    )
    clip.add_argument(**fileCommand)
    addClipOptions(clip)
    clip.set_defaults(traversalType=TraversalType.CLIP_HIGHLIGHTS, func=traverseFunc)

    # all subcommand
    all = subparsers.add_parser(
        "all",
        help="Make directories, download YouTube videos, and clip highlights from JSON file",
    )
    all.add_argument(**fileCommand)
    all.add_argument(
        "-t",
        "--no-threading",
        help="Avoid using multithreading to download YouTube videos."
        " This may decrease performance drastically",
        action="store_true",
    )
    all.add_argument(
        "-s",
        "--save-storage",
        help="Download YouTube videos sequentially, deleting each one after clipping"
        " its highlights in order to save storage. This may decrease performance"
        " drastically and implies --no-threading",
        action="store_true",
    )
    addClipOptions(all)
    all.set_defaults(func=allFunc)

    # delete subcommand
    delete = subparsers.add_parser(
        "delete", help="Delete full game film files listed in JSON"
    )
    delete.add_argument(**fileCommand)
    addClipOptions(delete, justDelimiter=True)
    delete.set_defaults(
        traversalType=TraversalType.DELETE_FULL_GAMES, func=traverseFunc
    )

    return parser


def main():
    parser = parserSetup()
    args = parser.parse_args()

    # call appropriate function based on subcommand
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
