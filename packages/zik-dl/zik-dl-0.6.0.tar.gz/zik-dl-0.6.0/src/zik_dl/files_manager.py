import os
import re
import shutil
import music_tag
from .arguments import Arguments
from .settings import TMP_DIR, UNKNOWN


class FilesManager:
    def __init__(self, args: Arguments):
        self.args = args

    def manage(self):
        for filename in os.listdir(TMP_DIR):
            filepath = os.path.join(TMP_DIR, filename)
            match = re.search(r"^(\S+)_(.*)(\.\S+)$", filename)
            track_number = (
                int(match.groups()[0]) if match.groups()[0].isdigit() else None
            )
            song_name = match.groups()[1]
            ext = match.groups()[2]
            f = music_tag.load_file(filepath)
            f["title"] = song_name
            for artist in self.args.artists:
                f.append_tag("artist", artist)
            f["album"] = self.args.album
            if track_number:
                f["tracknumber"] = track_number
            if self.args.cover:
                with open(self.args.cover, "rb") as cover_file:
                    f["artwork"] = cover_file.read()
            f.save()
            dest_dir = "./{}/{}".format(
                " X ".join(self.args.artists) or UNKNOWN,
                self.args.album or UNKNOWN,
            )
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(filepath, os.path.join(dest_dir, song_name + ext))
