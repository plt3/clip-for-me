# clip-for-me

> Download YouTube videos and clip timestamps from them just by writing Markdown

## What does this do?

This tool was built to automate the process of clipping individual highlights from large amounts of game footage when making (specifically ultimate frisbee) season highlight reels. Having hundreds of clips named appropriately and organized into subdirectories makes it easier to import the best ones into editing software later on. The use case this was written for is a team that posts all of its game footage from each tournament on YouTube and keeps timestamps of highlights from each game. clip-for me will then download the YouTube videos and place all the highlights in individual files in subdirectories arranged by game and by tournament. However, this functionality can be used for any other sport or situation where one needs to clip many small moments from large videos and save them into their own files.

## How does this work?

In order to specify the timestamps of the clips to be cut into their own files, write them in a Markdown file following a specific format (see [the specification](#markdown-specification)). You can then use clip-for-me to convert the Markdown to JSON so that the script can parse it. clip-for-me will then parse the JSON file, create the proper directory hierarchy, (optionally) download all the full-game videos from YouTube, and clip all the specified timestamps from the videos and place the new files in the corresponding subdirectories.

## Installation:

NOTE: only tested on macOS

- install dependencies: Python 3, ffmpeg. Both can be installed using [Homebrew](https://brew.sh/)
  - `brew install python` and `brew install ffmpeg` should work to install both
- clone repository: run `git clone https://github.com/plt3/clip-for-me`
- create a virtual environment for Python packages (recommended); in project directory, run `python3 -m venv venv` then `source venv/bin/activate`
- install Python dependencies: run `pip3 install -r requirements.txt`

## Usage:

- record videos and timestamp highlights in a Markdown file following the specified format (see [the specification](#markdown-specification) for details)
- convert the Markdown file to JSON with `python3 cli.py --parse-highlights /path/to/markdown-file.md`
- verify that the JSON file produced looks accurate
- run `python3 cli.py /path/to/json-file.md` to create the highlight directories, download the videos from YouTube, and clip all the highlights from the videos
  - this may take many minutes to run, especially if it has to download very large videos from YouTube. There should be output printed while it runs to know where the program is at

## Markdown Specification:

The Markdown file should have one heading level one (#) at the top of the file, which is usually the year or season. This will be the top-level directory that will be created.

Below this heading should be a heading level two (##) for each tournament in the season.

Below each of these headings should be a heading level three (###) for each game in the tournament. This heading should be a Markdown link leading to the YouTube URL of the full game film. It should look something like this: `### [some team](https://youtu.be/video-id-here):`.

Below each of these headings should be the timestamps of the highlights you would like to clip from this video. These should be organized as a Markdown list with one highlight per list item. Each list item should have the timestamp (formatted as MM:SS or HH:MM:SS), a hyphen, a space, and the description of the highlight. One of these lines should look like this: `- 5:38- crazy catch by player over two defenders`. It is crucial that the correct delimiter (hyphen + space) is between each timestamp and description, otherwise the script will fail to parse each part.

Repeat this process for as many games and tournaments as needed.

## Examples:

See the examples directory for an example [Markdown file](examples/example.md) and corresponding [JSON file](examples/example.json) (the latter was generated with `python3 cli.py --parse-highlights examples/example.md`). If you run `python3 cli.py examples/example.json`, clip-for-me will download the YouTube videos and clip all the highlights, producing the following directory structure:

![example_results](https://github.com/plt3/clip-for-me/assets/65266160/0b3704bf-28ab-4682-804f-10725b59ac80)

## TODO:

- [x] make CLI
- [ ] write JSON specification in README
- [ ] change print statements to logging
- [ ] use JSON schema to validate highlight JSON ([tutorial](https://json-schema.org/learn/getting-started-step-by-step.html), [arbitrary keys](https://stackoverflow.com/a/69811612/14146321))
- [ ] add type hints
- [ ] add command to move full games into separate directory
