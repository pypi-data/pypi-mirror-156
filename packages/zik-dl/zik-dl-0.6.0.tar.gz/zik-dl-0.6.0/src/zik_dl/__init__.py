import io
from contextlib import redirect_stderr
from .utils import printc, COLORS
from .arguments import Arguments
from .downloader import Downloader
from .files_manager import FilesManager


def main(argv=None):
    exit_code = 0
    f = io.StringIO()
    try:
        args = Arguments(argv)
        args.check()
        with redirect_stderr(f):
            Downloader(args).download()
    except SystemExit as e:
        stderr = f.getvalue()
        if e.code == 0:
            pass
        if "Private video" in stderr:
            printc(COLORS.WARNING, "Private tracks were not downloaded")
        else:
            printc(COLORS.FAIL, stderr)
            return e.code

    FilesManager(args).manage()

    return exit_code
