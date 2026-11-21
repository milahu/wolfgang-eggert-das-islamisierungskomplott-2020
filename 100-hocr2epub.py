#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Das Islamisierungskomplott",
    "--doc-subtitle", "Wer spielt gegen Europa?",
    # "--doc-subject", "",
    "--doc-date", "2020-08-07",
    "--doc-edition", "1",
    "--doc-extent", "172 pages",
    "--color-image-pages", "173,174",
    "--doc-author", "Wolfgang Eggert",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "Amazon",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9798617532472",
    "--doc-cover-image", "075-level/173.tiff",
    "--canonical-url-base", "https://milahu.github.io/wolfgang-eggert-das-islamisierungskomplott-2020/",
    "--doc-description", """
Als Angela Merkel 2015 die deutschen Grenzen einriss,
wurde Europa von einer Migrationswelle ungekannten Ausmaßes überrollt.
Die epische, seit dem Ende des Zweiten Weltkriegs
nicht mehr auf unserem Kontinent geschene Völkerwandung
steht heute vor einer Neuauflage,
denn schon wieder staut sich auf dem Balkan der Verkehr nach Norden,
während in Afrika Umfragen zufolge eine Milliarde Menschen abreisebereit sind
- um zu uns zu kommen.

Selbst wenn die Lage halbwegs ruhig bliebe
und sich die Asylzahlen auf dem Niveau von 2018 halten, hieße das,
dass Deutschland jährlich(!) eine neue Stadt
in der Größe von Kassel, Potsdam oder Saarbrücken errichten muss.
Eine afrikanisierte oder islamisierte Metropole.

Wie kam es zu dieser Entwicklung?
Warum brachen die Dämme?
Vor allem: WER ließ sie brechen,
WER sorgte dafür dass sie nicht wieder instandgesetzt wurden?
Fakt ist: Es gibt Kräfte, die an der verhängnisvollen Entwicklung in Europa,
an der Islamisierung, der Umvolkung und einem möglichen Bürgerkrieg Interesse haben.
Es sind sehr mächtige Kräfte, die es gewöhnlich vorziehen, im Dunkeln zu bleiben.
Das vorliegende Buch beleuchtet diese scheuen Strippenzicher
in einer breit gefächerten, profunden Analyse, die seit 2015 überfällig ist.
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
