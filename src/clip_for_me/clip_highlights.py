import os
from concurrent.futures import ThreadPoolExecutor

import jsonschema
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from .constants import (
    CLIP_DELIMITER,
    CLIP_NUM_WORDS,
    HIGHLIGHT_CLIP_LENGTH,
    HIGHLIGHT_CLIP_OFFSET,
    TraversalType,
)
from .utils import (
    download_video,
    link_to_game_info,
    parse_time_and_description,
    string_to_filename,
)


class ClipHighlights:
    def __init__(
        self,
        highlights,
        clip_delimiter=CLIP_DELIMITER,
        clip_num_words=CLIP_NUM_WORDS,
        clip_length=HIGHLIGHT_CLIP_LENGTH,
        clip_offset=HIGHLIGHT_CLIP_OFFSET,
    ):
        self.highlights = highlights
        self.clip_delimiter = clip_delimiter
        self.clip_num_words = clip_num_words
        self.clip_length = clip_length
        self.clip_offset = clip_offset

        self._validate_json()

    def _validate_json(self):
        # schema describing highlights JSON file
        schema = {
            "type": "object",
            "minProperties": 1,
            "maxProperties": 1,
            "additionalProperties": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "patternProperties": {
                        r"^\[.+?\]\(.+?\)(:)?$": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                # add highlight format that checks that each line
                                # follows format that parseTimeAndDescription looks for
                                "format": "highlight",
                            },
                        }
                    },
                    "additionalProperties": False,
                },
            },
        }
        format_checker = jsonschema.FormatChecker()

        # check that parseTimeAndDescription doesn't raise an error for each highlight
        @format_checker.checks("highlight", raises=ValueError)
        def validate_highlight(value):
            parse_time_and_description(value, self.clip_delimiter)
            return True

        # validate highlights against schema
        jsonschema.validate(self.highlights, schema, format_checker=format_checker)

    def make_clips_from_film(self, output_path, film_filename, timestamps):
        film_full_path = os.path.join(output_path, film_filename)

        for timestamp_str in timestamps:
            seconds, description = parse_time_and_description(
                timestamp_str, self.clip_delimiter
            )
            first_n_description_words = " ".join(
                description.split(" ")[: self.clip_num_words]
            )
            clip_name = string_to_filename(first_n_description_words) + ".mp4"
            clip_full_path = os.path.join(output_path, clip_name)

            # don't clip highlight if it has already been done previously
            if not os.path.exists(clip_full_path):
                print(f"Writing {clip_full_path}")

                ffmpeg_extract_subclip(
                    film_full_path,
                    seconds - self.clip_offset,
                    seconds - self.clip_offset + self.clip_length,
                    targetname=clip_full_path,
                )
            else:
                print(f"Skipping {clip_full_path} because it already exists")

    def traverse_highlights(self, traversal_type, threading=True):
        save_storage = False
        if traversal_type == TraversalType.SAVE_STORAGE:
            save_storage = True
            threading = False

        main_key, tournaments = list(self.highlights.items())[0]
        main_directory = string_to_filename(main_key)

        # to use threading when downloading full games
        with ThreadPoolExecutor() as executor:
            # loop through tournaments
            for tournament, games in tournaments.items():
                tournament_path = os.path.join(
                    main_directory, string_to_filename(tournament)
                )

                # loop through games in tournament
                for game_link, timestamps in games.items():
                    game_name, game_url = link_to_game_info(game_link)

                    game_name = string_to_filename(game_name)
                    game_path = os.path.join(tournament_path, game_name)
                    film_file = f"{game_name}.mp4"
                    full_film_path = os.path.join(game_path, film_file)

                    if traversal_type == TraversalType.CREATE_DIRS or save_storage:
                        if not os.path.exists(game_path):
                            print(f"Creating {game_path} directory.")
                            os.makedirs(game_path)

                    if (
                        traversal_type == TraversalType.DOWNLOAD_FULL_GAMES
                        or save_storage
                    ):
                        # don't try to download video if it has already previously been
                        # downloaded (yt-dlp already has this functionality but best to
                        # avoid starting a new thread altogether)
                        if not os.path.exists(full_film_path):
                            if threading:
                                # create and start thread to download game
                                executor.submit(
                                    download_video,
                                    game_url,
                                    film_file,
                                    output_path=game_path,
                                )
                            else:
                                # download game sequentially (will take much longer)
                                download_video(game_url, film_file, output_path=game_path)
                        else:
                            print(f"{full_film_path} already exists, skipping download")
                    if traversal_type == TraversalType.CLIP_HIGHLIGHTS or save_storage:
                        # don't try to clip highlights if full game film is not in directory
                        # (presumably due to issue with download)
                        if os.path.exists(full_film_path):
                            print(f"Clipping highlights from {full_film_path}:")
                            self.make_clips_from_film(game_path, film_file, timestamps)
                        else:
                            print(
                                f"{full_film_path} not found, skipping clipping highlights..."
                            )

                    if traversal_type == TraversalType.DELETE_FULL_GAMES or save_storage:
                        filmFilePath = os.path.join(game_path, film_file)
                        if os.path.exists(filmFilePath):
                            print(f"Deleting {filmFilePath}.")
                            os.remove(filmFilePath)
