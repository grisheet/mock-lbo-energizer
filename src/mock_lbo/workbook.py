"""Read saved OOXML values and formulas. Does not claim to recalculate Excel."""
import posixpath
from pathlib import Path
from typing import Any
from zipfile import ZipFile
import xml.etree.ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def read_workbook(file: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, str]]]:
    values: dict[str, dict[str, Any]] = {}
    formulas: dict[str, dict[str, str]] = {}
    with ZipFile(file) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            doc = ET.fromstring(z.read('xl/sharedStrings.xml'))
            shared = [''.join(n.itertext()) for n in doc.findall('m:si', NS)]
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target', '') for r in rels}
        doc = ET.fromstring(z.read('xl/workbook.xml'))
        for sheet in doc.findall('m:sheets/m:sheet', NS):
            name = sheet.get('name', '')
            target = targets[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            cells = ET.fromstring(z.read(member)).findall('.//m:c', NS)
            values[name], formulas[name] = {}, {}
            for cell in cells:
                address = cell.get('r', '')
                v = cell.find('m:v', NS)
                f = cell.find('m:f', NS)
                if f is not None:
                    formulas[name][address] = f.text or ('DATA_TABLE' if f.get('t') == 'dataTable' else '')
                if cell.get('t') == 'inlineStr':
                    inline = cell.find('m:is', NS)
                    if inline is None:
                        raise ValueError(f'Missing inline string: {name}!{address}')
                    values[name][address] = ''.join(inline.itertext())
                elif v is not None and v.text is not None:
                    if cell.get('t') == 's':
                        values[name][address] = shared[int(v.text)]
                    elif cell.get('t') in ('str','e'):
                        values[name][address] = v.text
                    else:
                        values[name][address] = float(v.text)
    return values, formulas


def column(n: int) -> str:
    result = ''
    while n:
        n, rem = divmod(n-1,26)
        result = chr(65+rem)+result
    return result
