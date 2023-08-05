import sys

from base64 import b64decode
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory

from script_to_pipeline.utils import get_entrypoint


if __name__ == "__main__":
    if len(sys.argv) > 1:

        source = b64decode(sys.argv[1])
        with TemporaryDirectory() as tempdir:
            Path(tempdir, "script.py").write_bytes(source)
            sys.path.append(tempdir)

            script = import_module("script")
            try:
                entrypoint = get_entrypoint(script)
                entrypoint()
            except:
                print("WARNING: No entrypoint found.")
    else:
        print("nothing to run")