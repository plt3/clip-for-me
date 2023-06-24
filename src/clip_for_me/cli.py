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
from .utils import convert_highlights


def convert_func(args_namespace):
    convert_highlights(args_namespace.file, output_file=args_namespace.output_file)


def traverse_func(args_namespace):
    with open(args_namespace.file) as f:
        # if clip_num_words is specified, then other two are also
        if hasattr(args_namespace, "clip_num_words"):
            clip_obj = ClipHighlights(
                json.load(f),
                clip_delimiter=args_namespace.delimiter,
                clip_num_words=args_namespace.clip_num_words,
                clip_length=args_namespace.clip_length,
                clip_offset=args_namespace.clip_offset,
            )
        else:
            clip_obj = ClipHighlights(
                json.load(f), clip_delimiter=args_namespace.delimiter
            )

    clip_obj.traverse_highlights(args_namespace.traversal_type)

    return clip_obj


def download_func(args_namespace):
    setattr(args_namespace, "traversal_type", TraversalType.CREATE_DIRS)
    clipObj = traverse_func(args_namespace)
    clipObj.traverse_highlights(
        TraversalType.DOWNLOAD_FULL_GAMES, threading=not args_namespace.no_threading
    )

    return clipObj


def allFunc(args_namespace):
    if args_namespace.save_storage:
        setattr(args_namespace, "traversal_type", TraversalType.SAVE_STORAGE)
        traverse_func(args_namespace)
    else:
        clipObj = download_func(args_namespace)
        clipObj.traverse_highlights(TraversalType.CLIP_HIGHLIGHTS)


def add_clip_options(subparser, just_delimiter=False):
    subparser.add_argument(
        "-d",
        "--delimiter",
        help='Delimiter between timestamp and description of each highlight (default "%(default)s")',
        default=CLIP_DELIMITER,
    )
    if not just_delimiter:
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


def parser_setup():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and clip timestamps from them by writing Markdown",
    )
    subparsers = parser.add_subparsers(title="subcommands")

    file_command = {"dest": "file", "help": "path to JSON file"}

    # convert subcommand
    convert = subparsers.add_parser("convert", help="Convert Markdown file to JSON")
    convert.add_argument("file", help="path to Markdown file to convert")
    convert.add_argument(
        "-o",
        "--output-file",
        help="name of JSON file to store highlights in",
    )
    convert.set_defaults(func=convert_func)

    # makedirs subcommand
    make_dirs = subparsers.add_parser(
        "makedirs", help="Make directory structure representing JSON"
    )
    make_dirs.add_argument(**file_command)
    add_clip_options(make_dirs, just_delimiter=True)
    make_dirs.set_defaults(traversal_type=TraversalType.CREATE_DIRS, func=traverse_func)

    # download subcommand
    download = subparsers.add_parser(
        "download",
        help="Download YouTube videos from JSON and put them in appropriate directories",
    )
    download.add_argument(**file_command)
    download.add_argument(
        "-t",
        "--no-threading",
        help="Specify to avoid using multithreading to download YouTube videos."
        " This may decrease performance drastically.",
        action="store_true",
    )
    add_clip_options(download, just_delimiter=True)
    download.set_defaults(func=download_func)

    # clip subcommand
    clip = subparsers.add_parser(
        "clip",
        help="Clip highlights from already-downloaded videos present in directories"
        " corresponding to JSON structure",
    )
    clip.add_argument(**file_command)
    add_clip_options(clip)
    clip.set_defaults(traversal_type=TraversalType.CLIP_HIGHLIGHTS, func=traverse_func)

    # all subcommand
    all = subparsers.add_parser(
        "all",
        help="Make directories, download YouTube videos, and clip highlights from JSON file",
    )
    all.add_argument(**file_command)
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
    add_clip_options(all)
    all.set_defaults(func=allFunc)

    # delete subcommand
    delete = subparsers.add_parser(
        "delete", help="Delete full game film files listed in JSON"
    )
    delete.add_argument(**file_command)
    add_clip_options(delete, just_delimiter=True)
    delete.set_defaults(
        traversal_type=TraversalType.DELETE_FULL_GAMES, func=traverse_func
    )

    return parser


def main():
    parser = parser_setup()
    args = parser.parse_args()

    # call appropriate function based on subcommand
    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()
