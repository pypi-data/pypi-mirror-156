from pathlib import Path

from .utils import in_container


class PFS:

    @staticmethod
    def get(repo: str, out: bool = False) -> Path:
        if in_container():
            path = Path("/pfs", repo) if not out else Path("/pfs/out")
            if not path.exists():
                raise NotADirectoryError(path)
        else:
            raise NotImplementedError(
                "TODO: Add connection with mount extension for local development"
            )
        return path
