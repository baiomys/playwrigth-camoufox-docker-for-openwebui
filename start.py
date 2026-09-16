import base64
import os
import signal
import subprocess
from pathlib import Path

import orjson

from camoufox.server import get_nodejs, to_camel_case_dict
from camoufox.pkgman import LOCAL_DATA
from camoufox.utils import launch_options


PORT = int(os.environ.get("CAMOUFOX_PORT", "9222"))
WS_PATH = os.environ.get("CAMOUFOX_WS_PATH", "")
LAUNCH_SCRIPT = LOCAL_DATA / "launchServer.js"


def strip_nulls(value):
    if isinstance(value, dict):
        return {
            key: strip_nulls(val)
            for key, val in value.items()
            if val is not None
        }

    if isinstance(value, list):
        return [strip_nulls(item) for item in value]

    return value


def main():
    signal.signal(signal.SIGTERM, lambda *_: os._exit(0))

    print(
        f"Starting Camoufox Playwright server "
        f"on 0.0.0.0:{PORT} (headless=True)",
        flush=True,
    )

    config = launch_options(
        headless=True,
        port=PORT,
    )

    config = strip_nulls(config)
    config = to_camel_case_dict(config)

    if WS_PATH:
        config["wsPath"] = (
            WS_PATH
            if WS_PATH.startswith("/")
            else f"/{WS_PATH}"
        )

    nodejs = get_nodejs()

    # IMPORTANT:
    # Current Camoufox launchServer.js expects the
    # Playwright driver package as argv[2].
    driver_package = Path(nodejs).parent / "package"

    if not driver_package.exists():
        raise RuntimeError(
            f"Playwright driver package not found: {driver_package}"
        )

    if not LAUNCH_SCRIPT.exists():
        raise RuntimeError(
            f"Camoufox launchServer.js not found: {LAUNCH_SCRIPT}"
        )

    data = orjson.dumps(config)

    print(f"Node.js: {nodejs}", flush=True)
    print(f"Driver package: {driver_package}", flush=True)
    print(f"Launch script: {LAUNCH_SCRIPT}", flush=True)

    process = subprocess.Popen(
        [
            nodejs,
            str(LAUNCH_SCRIPT),
            str(driver_package),
        ],
        cwd=driver_package,
        stdin=subprocess.PIPE,
        text=True,
    )

    encoded_config = base64.b64encode(data).decode()

    try:
        process.stdin.write(encoded_config)
        process.stdin.close()
    except BrokenPipeError:
        pass

    return_code = process.wait()

    raise RuntimeError(
        f"Camoufox server terminated unexpectedly "
        f"with exit code {return_code}"
    )


if __name__ == "__main__":
    main()
