# clip-for-me

> Download YouTube videos and clip timestamps from them just by writing Markdown

## What does this do?

This tool was built to automate the process of clipping individual highlights from large amounts of game footage when making (specifically ultimate frisbee) season highlight reels. Having hundreds of clips named appropriately and organized into subdirectories makes it easier to import the best ones into editing software later on. The use case this was written for is a team that posts all of its game footage from each tournament on YouTube and keeps timestamps of highlights from each game. clip-for me will then download the YouTube videos and place all the highlights in individual files in subdirectories arranged by game and by tournament. However, this functionality can be used for any other sport or situation where one needs to clip many small moments from large videos and save them into their own files.

## How does this work?

In order to specify the timestamps of the clips to be cut into their own files, write them in a Markdown file following a specific format (see [the specification](#specification)). You can then use clip-for-me to convert the Markdown to JSON so that the script can parse it. clip-for-me will then parse the JSON file, create the proper directory hierarchy, (optionally) download all the full-game videos from YouTube, and clip all the specified timestamps from the videos and place the new files in the corresponding subdirectories.

## Installation

NOTE: only tested on macOS

- install dependencies: Python 3, ffmpeg. Both can be installed using [Homebrew](https://brew.sh/)
  - `brew install python` and `brew install ffmpeg` should work to install both
- create a virtual environment for Python packages (recommended); in project directory, run `python3 -m venv --prompt clip-for-me venv` then `source venv/bin/activate`
- install the package: `pip install git+https://github.com/plt3/clip-for-me.git`

The CLI is now available whenever this virtual environment is active, as `clip-for-me`.

## Quickstart

- record videos and timestamp highlights in a Markdown file following the specified format (see [the Markdown specification](#markdown) for details)
- convert the Markdown file to JSON with `clip-for-me convert /path/to/markdown-file.md`
- verify that the JSON file produced looks accurate (see [the JSON specification](#json) for details)
- run `clip-for-me all /path/to/json-file.json` to create the highlight directories, download the videos from YouTube, and clip all the highlights from the videos
  - this may take many minutes to run, especially if it has to download very large videos from YouTube. There should be output printed while it runs to know where the program is at

## More Detailed Usage

- run `clip-for-me -h` to print help information
- `clip-for-me` has 6 subcommands. View help information for each one with `clip-for-me {subcommand} -h`
  - `clip-for-me convert /path/to/markdown-file.md` converts the Markdown file to JSON
    - `-o OUTPUT_FILE`: specify output file path
  - `clip-for-me makedirs /path/to/json-file.json` only creates the directory structure corresponding to the JSON
    - `-d DELIMITER`: specify delimiter between timestamp and description of each highlight. Default is "- "
  - `clip-for-me download /path/to/json-file.json` creates the directory structure and downloads the videos in the Markdown links from YouTube
    - options include that of `makedirs`, as well as:
    - `-t`: do not use any multithreading when downloading
  - `clip-for-me clip /path/to/json-file.json` clips the highlights from the videos that should be already present in the directories
    - options include that of `makedirs`, as well as:
    - `-n CLIP_NUM_WORDS`: specify number of words to take from the beginning of each highlight's description to make the filename of the highlight clip. Default is 4
    - `-l CLIP_LENGTH`: specify length of each highlight clip in seconds. Default is 10
    - `-o CLIP_OFFSET`: specify offset of each highlight clip from the marked timestamp in seconds. Default is 2
  - `clip-for-me all /path/to/json-file.json` creates the directories, downloads the videos, and clips the highlights from them
    - options include those of `download` and `clip`, as well as:
    - `-s`: download YouTube videos sequentially and delete them after clipping all the highlights from them in order to take as little disk space as possible
  - `clip-for-me delete /path/to/json-file.json` deletes the full game videos (the ones downloaded from YouTube), but keeps all the highlight clips

## Specification

### Markdown

The Markdown file should have one heading level one (#) at the top of the file, which is usually the year or season. This will be the top-level directory that will be created.

Below this heading should be a heading level two (##) for each tournament in the season.

Below each of these headings should be a heading level three (###) for each game in the tournament. This heading should be a Markdown link leading to the YouTube URL of the full game film. It should look something like this: `### [some team](https://youtu.be/video-id-here):`.

Below each of these headings should be the timestamps of the highlights you would like to clip from this video. These should be organized as a Markdown list with one highlight per list item. Each list item should have the timestamp (formatted as MM:SS or HH:MM:SS), the delimiter (default is "- ") and the description of the highlight. One of these lines should look like this: `- 5:38- crazy catch by player over two defenders`. It is crucial that the correct delimiter (hyphen + space) is between each timestamp and description, otherwise the script will fail to parse each part.

Repeat this process for as many games and tournaments as needed.

### JSON

The JSON specification is essentially the same as the Markdown one, since all the `convert` command does is convert the Markdown file into the corresponding JSON object.

The JSON object should have a top-level key, whose value should be an object with keys for each tournament.

The value of each of the tournament keys should be an object with keys for each game, which should still be formatted as a markdown link (e.g. `[some team](https://youtu.be/video-id-here):`). The colon at the end is optional.

The value of each of the game keys should be an array of strings, where each string corresponds to a highlight. Each string must be in the format timestamp-delimiter-description, as described in the Markdown specification (e.g. `5:38- crazy catch by player over two defenders`).

Repeat this process for as many games and tournaments as needed.

## Examples

See the examples directory for an example [Markdown file](examples/example.md) and corresponding [JSON file](examples/example.json) (the latter was generated with `clip-for-me convert examples/example.md`). If you run `clip-for-me all examples/example.json`, clip-for-me will download the YouTube videos and clip all the highlights, producing the following directory structure:

![example_results](https://github.com/plt3/clip-for-me/assets/65266160/0b3704bf-28ab-4682-804f-10725b59ac80)

## TODO

- [x] make CLI
- [x] write JSON specification in README
- [ ] change print statements to logging
- [x] use JSON schema to validate highlight JSON ([tutorial](https://json-schema.org/learn/getting-started-step-by-step.html), [arbitrary keys](https://stackoverflow.com/a/69811612/14146321))
- [ ] add type hints
- [ ] add command to move full games into separate directory
