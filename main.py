import csv
import os
import shutil
import zipfile
from urllib.request import urlopen
from urllib.parse import urlparse

cachedir = "tmp"  # TODO: smazat

HEADER = [
    "DATSK",
    "CASSK",
    "MISTOSK",
    "PRAHA",
    "OZNAM",
    "MPZ",
    "TOVZN",
    "OSOBA",
    "FIRMA",
    "PRAVFOR",
]

URLS = [
    "https://storage.golemio.cz/lkod/mhp/1e4da486-0229-44df-b3de-29a307a3e025/d79d4145-bcf0-4bb3-b9de-92408e75ffb0-mhmp_dopravni_prestupky_2015.csv",
    "https://storage.golemio.cz/lkod/mhp/13d0d2b0-63e4-4f6a-adf3-12448300261e/7736a486-36b3-47c1-8fc4-65ef1ffabf61-mhmp_dopravni_prestupky_2016.csv",
    "https://storage.golemio.cz/lkod/mhp/70c0712c-7252-45f7-88dd-ad63899f9eef/b1801060-b54f-4fbf-a9ae-215df2f6b3a6-mhmp_dopravni_prestupky_2017.csv",
    "https://storage.golemio.cz/lkod/mhp/a8e902f2-325c-431c-ac84-1983c5bae130/1199d54b-4421-4d5d-bc53-8e23d4aeb1d5-mhmp_dopravni_prestupky_2018.csv",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2019.zip",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2020.zip",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2021.zip",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2022.zip",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2023.zip",
]

table = "dopravni_prestupky"
schema = f"""
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
    datum_skutku DATE NOT NULL,
    cas_skutku TEXT,
    misto_skutku TEXT,
    praha TEXT,
    oznamovatel TEXT NOT NULL, -- TODO: enum?
    mpz TEXT, -- TODO: bool?
    tovarni_znacka TEXT,
    osoba TEXT NOT NULL, -- TODO: bool?
    firma TEXT NOT NULL, -- TODO: bool?
    pravni_kvalifikace TEXT NOT NULL
)
"""


def url_as_local_file(url: str) -> str:
    fn = os.path.join(
        cachedir,
        os.path.basename(urlparse(url).path),
    )
    if not os.path.isfile(fn):
        with open(fn, "wb") as fw, urlopen(url, timeout=5) as r:
            shutil.copyfileobj(r, fw)

    if fn.endswith(".zip"):
        with zipfile.ZipFile(fn) as zf:
            assert len(zf.filelist) == 1, len(zf.filelist)
            fn = zf.filelist[0].filename
            tfn = os.path.join(cachedir, fn)
            if not os.path.isfile(tfn):
                zf.extract(zf.filelist[0], cachedir)
            fn = tfn

    return fn


if __name__ == "__main__":
    os.makedirs(cachedir, exist_ok=True)

    with open("schema.sql", "wt") as fw:
        fw.write(schema)

    with open("load.sh", "wt") as fw:
        fw.write("set -eux\n")
        fw.write("psql < schema.sql\n")
        for url in URLS:
            print(url)
            fn = url_as_local_file(url)
            fw.write(f"cat {fn} | psql -c 'COPY {table} FROM STDIN CSV HEADER'\n")
