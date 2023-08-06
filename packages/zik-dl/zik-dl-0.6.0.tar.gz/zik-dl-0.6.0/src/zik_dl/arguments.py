import os
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import List


@dataclass(init=False)
class Arguments:
    url: str
    artists: List[str]
    album: str
    split: bool

    def __init__(self, argv=None):
        parser = ArgumentParser(
            description="Command-line program to download music from YouTube and other websites."
        )
        parser.add_argument("url", help="URL of the song/album to download")
        parser.add_argument(
            "--artists",
            help="comma-separated artists names"
            ' like "Louis Armstrong,Ella Fitzgerald"',
            type=lambda s: [name for name in s.split(",")],
        )
        parser.add_argument("--album", help="album name")
        parser.add_argument(
            "--split",
            help="split song in multiple songs based on timestamps (youtube video description)",
            action="store_true",
        )
        parser.add_argument(
            "--cover",
            help='cover path like "~/Images/cover1.jpg"',
        )

        args = parser.parse_args(argv)
        self.url = args.url
        self.artists = args.artists or []
        self.album = args.album
        self.split = args.split
        self.cover = args.cover

    def check(self):
        """
        Checks the value and compatibility of arguments.
        """
        if self.cover and not os.path.isfile(self.cover):
            raise Exception(
                f"Cover not found ! You put '{self.cover}' (current dir is '{os.getcwd()}')"
            )
