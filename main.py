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
    "https://opendata.praha.eu/dataset/86b98145-2d8a-46b9-8d24-cafb7c4ece20/resource/ac5664d7-caa8-4dce-8f75-906aea178ffd/download/d79d4145-bcf0-4bb3-b9de-92408e75ffb0-mhmp_dopravni_prestupky_2015.csv",
    "https://opendata.praha.eu/dataset/df4b4faa-7a79-4b96-82f8-c855623ea3e0/resource/392c6bd4-daaa-4aa6-97d5-fc3e544f2f66/download/7736a486-36b3-47c1-8fc4-65ef1ffabf61-mhmp_dopravni_prestupky_2016.csv",
    "https://opendata.praha.eu/dataset/d1c43e25-11d4-49ec-a4df-43c1821b2f88/resource/f2b80aff-7864-49c4-859c-893242bf6713/download/b1801060-b54f-4fbf-a9ae-215df2f6b3a6-mhmp_dopravni_prestupky_2017.csv",
    "https://opendata.praha.eu/dataset/0d285576-1863-4725-9f81-f8490e066eb3/resource/fd3eecac-3594-45a8-a0ed-b8ca392bf7ca/download/1199d54b-4421-4d5d-bc53-8e23d4aeb1d5-mhmp_dopravni_prestupky_2018.csv",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2019.zip",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2020.zip",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2021.zip",
    "https://storage.golemio.cz/ckan/mporga/MHMP_dopravni_prestupky_2022.zip",
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
            fn = url_as_local_file(url)
            fw.write(f"cat {fn} | psql -c 'COPY {table} FROM STDIN CSV HEADER'\n")
