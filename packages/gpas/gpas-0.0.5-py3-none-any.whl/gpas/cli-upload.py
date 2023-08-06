import logging
from pathlib import Path

import argparse

from gpas.misc import jsonify_exceptions

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

from gpas import lib
from gpas.lib import logging
from gpas.misc import (
    DEFAULT_ENVIRONMENT,
    ENVIRONMENTS,
)


def upload(
    upload_csv: Path,
    *,
    token: Path | None = None,
    working_dir: Path = Path("/tmp"),
    out_dir: Path = Path(),
    processes: int = 0,
    dry_run: bool = False,
    debug: bool = False,
    environment: ENVIRONMENTS = DEFAULT_ENVIRONMENT,
    json_messages: bool = False,
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    batch = lib.Batch(
        upload_csv,
        token=token,
        working_dir=working_dir,
        out_dir=out_dir,
        processes=processes,
        environment=environment,
        json_messages=json_messages,
    )
    batch.upload(dry_run=dry_run)


def upload_wrapper(
    upload_csv: Path,
    token: Path | None = None,
    working_dir: Path = Path("/tmp"),
    out_dir: Path = Path(),
    processes: int = 0,
    dry_run: bool = False,
    debug: bool = False,
    environment: ENVIRONMENTS = DEFAULT_ENVIRONMENT,
    json_messages: bool = False,
):
    """
    Validate, decontaminate and upload reads to the GPAS platform

    :arg upload_csv: Path of upload csv
    :arg token: Path of auth token available from GPAS Portal
    :arg working_dir: Path of directory in which to make intermediate files
    :arg out_dir: Path of directory in which to save mapping CSV
    :arg processes: Number of tasks to execute in parallel. 0 = auto
    :arg dry_run: Exit before submitting files
    :arg debug: Print verbose debug messages
    :arg json_over_stdout: Emit JSON messages over stdout
    :arg environment: GPAS environment to use

    """
    jsonify_exceptions(
        upload,
        upload_csv=upload_csv,
        token=token,
        working_dir=working_dir,
        out_dir=out_dir,
        processes=processes,
        dry_run=dry_run,
        debug=debug,
        environment=environment,
        json_messages=json_messages,
    )


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--upload-csv', type=Path, help='path of upload csv')
    args = parser.parse_args()
    print(args.upload_csv)


if __name__ == "__main__":
    main()
