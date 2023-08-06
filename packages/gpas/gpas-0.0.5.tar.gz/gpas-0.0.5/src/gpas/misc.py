import hashlib
import json
import logging
import multiprocessing
import os
import shutil
import subprocess
import sys
import traceback
from dataclasses import dataclass
from functools import partial
from enum import Enum
from pathlib import Path

import pandas as pd
import tqdm

import gpas
from gpas import validation


FORMATS = Enum("Formats", dict(table="table", csv="csv", json="json"))
DEFAULT_FORMAT = FORMATS.table
ENVIRONMENTS = Enum("Environment", dict(dev="dev", staging="staging", prod="prod"))
DEFAULT_ENVIRONMENT = ENVIRONMENTS.prod
FILE_TYPES = Enum("FileType", dict(json="json", fasta="fasta", bam="bam", vcf="vcf"))
GOOD_STATUSES = {"Unreleased", "Released"}


class AuthenticationError(Exception):
    pass


class DecontaminationError(Exception):
    pass


class SubmissionError(Exception):
    pass


ENDPOINTS = {
    "dev": {
        "HOST": "https://portal.dev.gpas.ox.ac.uk/",
        "API_PATH": "ords/gpasdevpdb1/gpas_pub/gpasapi/",
        "ORDS_PATH": "ords/gpasdevpdb1/grep/electron/",
        "DASHBOARD_PATH": "ords/gpasdevpdb1/gpas/r/gpas-portal/lineages-voc/",
        "NAME": "DEV",
    },
    "prod": {
        "HOST": "https://portal.gpas.ox.ac.uk/",
        "API_PATH": "ords/gpas_pub/gpasapi/",
        "ORDS_PATH": "ords/grep/electron/",
        "DASHBOARD_PATH": "ords/gpas/r/gpas-portal/lineages-voc/",
        "NAME": "PROD",
    },
    "staging": {
        "HOST": "https://portal.staging.gpas.ox.ac.uk/",
        "API_PATH": "ords/gpasuat/gpas_pub/gpasapi/",
        "ORDS_PATH": "ords/gpasuat/grep/electron/",
        "DASHBOARD_PATH": "ords/gpas/r/gpas-portal/lineages-voc/",
        "NAME": "STAGE",
    },
}


@dataclass
class LoggedShellCommand:
    name: str
    cmd: str
    before_msg: dict
    after_msg: dict


def get_value_traceback(e: Exception) -> tuple[str, str, list]:
    e_type, e_value, e_traceback = sys.exc_info()
    e_t = str(e_type)
    e_v = repr(e_value)
    e_tb = traceback.format_tb(e_traceback)
    return e_t, e_v, e_tb


def jsonify_exceptions(function, **kwargs):
    """Catch exceptions and print JSON"""

    def jsonify(obj, generic=False) -> None:
        if generic:
            output = json.dumps({"error": repr(obj)}, indent=4)
        else:
            output = json.dumps(obj, indent=4)
        print(str(output), flush=True)

    if kwargs["json_messages"]:
        try:
            return function(**kwargs)
        except validation.ValidationError as e:
            jsonify(e.report)
        except Exception as e:
            e_t, e_v, e_tb = get_value_traceback(e)
            jsonify({"exception": e_v, "traceback": e_tb})
    else:
        return function(**kwargs)


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)


def run_logged(
    command: LoggedShellCommand, json_messages: bool = False
) -> subprocess.CompletedProcess:
    def print_json(data):
        print(json.dumps(data, indent=4), flush=True)

    if json_messages:
        logging.basicConfig(format="%(message)s", level=logging.INFO)
        print_json(command.before_msg)
    process = subprocess.run(
        command.cmd, shell=True, check=True, text=True, capture_output=True
    )
    if json_messages:
        print_json(command.after_msg)
    return process


def run_parallel_logged(
    commands: list[LoggedShellCommand],
    processes: int = multiprocessing.cpu_count(),
    participle: str = "processing",
    json_messages: bool = False,
) -> dict[str, subprocess.CompletedProcess]:
    processes = 1 if sys.platform == "win32" else processes
    if processes == 1:
        results = {c.name: run(c.cmd) for c in commands}
    else:
        names = [c.name for c in commands]
        cmds = [c.cmd for c in commands]
        logging.debug(f"Started {participle.lower()} {len(cmds)} sample(s) \n{cmds=}")
        with multiprocessing.get_context("spawn").Pool(processes) as pool:
            results = {
                n: c
                for n, c in zip(
                    names,
                    tqdm.tqdm(
                        pool.imap_unordered(
                            partial(run_logged, json_messages=json_messages),
                            commands,
                        ),
                        total=len(cmds),
                        desc=f"{participle} {len(cmds)} sample(s)",
                        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                        leave=False,
                    ),
                )
            }
            logging.info(f"Finished {participle.lower()} {len(cmds)} sample(s)")
    return results


def check_unicode(data):
    """Returns a Unicode object on success or None on failure"""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


class set_directory(object):
    """
    Context manager for temporarily changing the current working directory
    """

    def __init__(self, path: Path):
        self.path = path
        self.origin = Path().absolute()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, *exc):
        os.chdir(self.origin)


def resolve_paths(df: pd.DataFrame) -> pd.DataFrame:
    """
    Read CSV and resolve relative paths
    """
    resolve = lambda x: Path(x).resolve()
    if "fastq" in df.columns:
        df["fastq"] = df["fastq"].apply(resolve)
    if "fastq1" in df.columns:
        df["fastq1"] = df["fastq1"].apply(resolve)
    if "fastq2" in df.columns:
        df["fastq2"] = df["fastq2"].apply(resolve)
    if "bam" in df.columns:
        df["bam"] = df["bam"].apply(resolve)
    return df


def get_binary_path(filename: str) -> str:
    if shutil.which(filename):  # In $PATH? Conda etc
        path = shutil.which(filename)
    elif os.getenv(f"GPAS_{filename.upper()}_PATH"):  # Check environment variables
        path = os.environ[f"GPAS_{filename.upper()}_PATH"]
    else:
        raise FileNotFoundError(f"Could not find {filename} binary")
    return str(path)


def hash_file(file_path: Path):
    md5 = hashlib.md5()
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def hash_string(string: str):
    return hashlib.md5(string.encode()).hexdigest()


def get_reference_path(organism):
    prefix = gpas.data_dir / Path("refs")
    organisms_paths = {"SARS-CoV-2": "MN908947_no_polyA.fasta"}
    return Path(prefix / organisms_paths[organism]).resolve()
