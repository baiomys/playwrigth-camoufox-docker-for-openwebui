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
        host="0.0.0.0",
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
    driver_package = Path(nodejs).parent / "package"

    print(f"Node.js: {nodejs}", flush=True)
    print(f"Driver package: {driver_package}", flush=True)
    print(f"Launch script: {LAUNCH_SCRIPT}", flush=True)

    data = orjson.dumps(config)

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

    assert process.stdin is not None

    # IMPORTANT:
    # Send one newline-delimited config frame.
    # DO NOT close stdin here.
    process.stdin.write(
        base64.b64encode(data).decode() + "\n"
    )
    process.stdin.flush()

    # Keep stdin open while the Node server is running.
    # EOF tells launchServer.js to shut the server down.
    try:
        process.wait()
    except BaseException:
        try:
            process.stdin.close()
        except OSError:
            pass

        if process.poll() is None:
            process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

        raise


if __name__ == "__main__":
    main()
