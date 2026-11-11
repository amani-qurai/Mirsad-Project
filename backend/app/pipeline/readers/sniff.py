"""Decide what a file is from its bytes, never from its name (M-008).

One branch sends a semicolon CSV named ``.xls``; a name is a claim, the content
is the evidence.
"""

from __future__ import annotations

import io
import zipfile

from app.errors import ErrorCode, MirsadError

from .table import Format

_ZIP_MAGIC = b"PK\x03\x04"
_OLE2_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # legacy .xls / .doc
_UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")


def sniff_format(data: bytes, name: str) -> Format:
    if not data:
        raise MirsadError(ErrorCode.FILE_EMPTY, {"file": name})

    if data.startswith(_ZIP_MAGIC):
        return _sniff_zip(data, name)

    if data.startswith(_OLE2_MAGIC):
        # A real binary .xls. None of the eleven branches send one today; if
        # one starts to, that is a change worth stopping on, not guessing at.
        raise MirsadError(ErrorCode.FILE_FORMAT_UNSUPPORTED, {"file": name, "detected": "ole2"})

    if b"\x00" in data[:4096] and not data.startswith(_UTF16_BOMS):
        raise MirsadError(ErrorCode.FILE_FORMAT_UNSUPPORTED, {"file": name, "detected": "binary"})

    return "csv"


def _sniff_zip(data: bytes, name: str) -> Format:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = set(archive.namelist())
    except zipfile.BadZipFile:
        raise MirsadError(ErrorCode.FILE_FORMAT_UNSUPPORTED, {"file": name, "detected": "corrupt-zip"}) from None

    if "xl/workbook.xml" in members:
        return "xlsx"
    if "word/document.xml" in members:
        return "docx"
    raise MirsadError(ErrorCode.FILE_FORMAT_UNSUPPORTED, {"file": name, "detected": "zip"})
