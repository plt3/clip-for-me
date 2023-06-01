import argparse

from ClipForMe import ClipHighlights
from ClipForMe.constants import (
    CLIP_DELIMITER,
    CLIP_NUM_WORDS,
    HIGHLIGHT_CLIP_LENGTH,
    HIGHLIGHT_CLIP_OFFSET,
    TraversalType,
)
from ClipForMe.utils import convertHighlights


def convertFunc(argsNamespace):
    convertHighlights(argsNamespace.file, outputFile=argsNamespace.output_file)


def makeDirsFunc(argsNamespace):
    clipObj = ClipHighlights.fromFile(argsNamespace.file)
    clipObj.traverseHighlights(TraversalType.CREATE_DIRS)

    return clipObj


def downloadFunc(argsNamespace):
    clipObj = makeDirsFunc(argsNamespace)
    clipObj.traverseHighlights(
        TraversalType.DOWNLOAD_FULL_GAMES, threading=not argsNamespace.sequential
    )

    return clipObj


def parserSetup():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and clip timestamps from them by writing Markdown",
    )

    subparsers = parser.add_subparsers(title="subcommands", help="TODO")
    convert = subparsers.add_parser("convert", help="Convert Markdown file to JSON")
    convert.add_argument("file", help="path to Markdown file to convert")
    convert.add_argument(
        "-o",
        "--output-file",
        help="name of JSON file to store highlights in",
    )
    convert.set_defaults(func=convertFunc)

    makeDirs = subparsers.add_parser(
        "makedirs", help="Make directory structure representing JSON"
    )
    makeDirs.add_argument("file", help="path to JSON file")
    makeDirs.set_defaults(func=makeDirsFunc)

    download = subparsers.add_parser(
        "download",
        help="Download YouTube videos from JSON and put them in appropriate directories",
    )
    download.add_argument("file", help="path to JSON file")
    download.add_argument(
        "-s",
        "--sequential",
        help="Specify to avoid using multithreading to download YouTube videos. This may decrease performance drastically.",
        action="store_true",
    )
    download.set_defaults(func=downloadFunc)

    clip = subparsers.add_parser(
        "clip",
        help="Clip highlights from already-downloaded videos present in directories corresponding to JSON structure",
    )
    clip.add_argument("file", help="path to JSON file")
    clip.add_argument(
        "-d",
        "--delimiter",
        help='Delimiter between timestamp and description of each highlight (default "%(default)s")',
        default=CLIP_DELIMITER,
    )
    clip.add_argument(
        "-n",
        "--clip-num-words",
        type=int,
        help="Number of words to take from beginning of highlight description to make name of file (default %(default)s)",
        default=CLIP_NUM_WORDS,
    )
    clip.add_argument(
        "-l",
        "--clip-length",
        type=int,
        help="Length of each highlight clip in seconds (default %(default)s)",
        default=HIGHLIGHT_CLIP_LENGTH,
    )
    clip.add_argument(
        "-o",
        "--clip-offset",
        help="Offset of each highlight clip from marked timestamp in seconds (default %(default)s)",
        default=HIGHLIGHT_CLIP_OFFSET,
    )

    delete = subparsers.add_parser("delete", help="Delete full game film")
    delete.add_argument("file", help="path to thing to delete")

    return parser


def main():
    parser = parserSetup()
    args = parser.parse_args()
    __import__("pprint").pprint(args)
    if hasattr(args, "func"):
        args.func(args)

    # clipper = ClipHighlights.fromFile(sys.argv[1])
    #
    # clipper.traverseHighlights(TraversalType.CREATE_DIRS)
    # clipper.traverseHighlights(TraversalType.DOWNLOAD_FULL_GAMES)
    # clipper.traverseHighlights(TraversalType.CLIP_HIGHLIGHTS)


if __name__ == "__main__":
    main()
