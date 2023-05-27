import sys

from ClipForMe import ClipHighlights
from ClipForMe.constants import TraversalType
from ClipForMe.utils import parseHighlights


def main():
    if sys.argv[1] == "--parse-highlights":
        parseHighlights(sys.argv[2])
    else:
        clipper = ClipHighlights.fromFile(sys.argv[1])

        clipper.traverseHighlights(TraversalType.CREATE_DIRS)
        clipper.traverseHighlights(TraversalType.DOWNLOAD_FULL_GAMES)
        clipper.traverseHighlights(TraversalType.CLIP_HIGHLIGHTS)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main()
    else:
        print(
            f"USAGE: python3 {sys.argv[0]} /path/to/highlights.json\n"
            f"or python3 {sys.argv[0]} --parse-highlights /path/to/highlights.md"
        )
