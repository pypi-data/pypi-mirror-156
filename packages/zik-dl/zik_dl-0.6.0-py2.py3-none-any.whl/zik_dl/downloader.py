import shutil
from .arguments import Arguments
from yt_dlp import main as ytdlp
from .settings import TMP_DIR
from glob import glob
from os import remove


class Downloader:
    def __init__(self, args: Arguments):
        self.args = args

    def download(self):
        shutil.rmtree(TMP_DIR, ignore_errors=True)
        ytdlp_args = ["-x"]
        if self.args.split:
            ytdlp_args += [
                "-o",
                f"{TMP_DIR}to_delete.%(ext)s",
                "--split-chapters",
                "-o",
                f"chapter:{TMP_DIR}%(section_number)s_%(section_title)s.%(ext)s",
            ]
        else:
            ytdlp_args += ["-o", f"{TMP_DIR}%(playlist_index)s_%(title)s.%(ext)s"]

        ytdlp_args.append(self.args.url)
        try:
            ytdlp(ytdlp_args)
        except SystemExit as e:
            if e.code != 0:
                raise e
        if self.args.split:
            remove(glob(f"{TMP_DIR}to_delete.*")[0])
