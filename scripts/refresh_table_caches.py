"""Transfer verified recalculation caches, preserving original native Excel tables.

This does not replace formulas with static results. LibreOffice's roundtrip may
rewrite Excel data-table formulas, so only calculated <v> values and cell types
are transferred into the original artifact-authored file. Audit the output next.
"""
import argparse
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def coordinate(s: str) -> tuple[int,int]:
    m=re.fullmatch(r'([A-Z]+)(\d+)',s)
    if m is None:
        raise ValueError(s)
    col=0
    for ch in m[1]:
        col=col*26+ord(ch)-64
    return int(m[2]),col


def refresh(original: Path, recalculated: Path) -> int:
    with ZipFile(original) as z:
        original_files={n:z.read(n) for n in z.namelist()}
    count=0
    with ZipFile(recalculated) as rz:
        for name,raw in list(original_files.items()):
            if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml',name):
                continue
            doc=ET.fromstring(raw)
            ranges=[f.get('ref') for f in doc.findall('.//m:f',NS) if f.get('t')=='dataTable']
            if not ranges:
                continue
            refs=[(coordinate(r.split(':')[0]),coordinate(r.split(':')[1])) for r in ranges]
            recalculated_cells={c.get('r'):c for c in ET.fromstring(rz.read(name)).findall('.//m:c',NS)}
            text=raw.decode()
            for c in doc.findall('.//m:c',NS):
                address=c.get('r','')
                row,col=coordinate(address)
                if not any(r1<=row<=r2 and c1<=col<=c2 for ((r1,c1),(r2,c2)) in refs):
                    continue
                fresh=recalculated_cells[address]
                v=fresh.find('m:v',NS)
                if v is None or fresh.get('t')=='e':
                    raise ValueError((address,'Uncalculated table value'))
                typ=fresh.get('t','n')
                if typ=='s':
                    raise ValueError('Shared-string table cache requires explicit decoding')
                pattern=rf'<(?P<prefix>\w+:)?c\b[^>]*\br="{address}"[^>]*>.*?</(?:\w+:)?c>'
                match=re.search(pattern,text,re.S)
                if match is None:
                    raise ValueError(address)
                cell=match[0]
                start,body=cell.split('>',1)
                start=re.sub(r'\s+t="[^"]*"','',start)+f' t="{typ}">'
                prefix=match.group('prefix') or ''
                body=re.sub(r'<(?:\w+:)?v>.*?</(?:\w+:)?v>','',body,flags=re.S)
                body=body.replace(f'</{prefix}c>',f'<{prefix}v>{html.escape(v.text or "")}</{prefix}v></{prefix}c>')
                text=text[:match.start()]+start+body+text[match.end():]
                count+=1
            original_files[name]=text.encode()
    temporary=original.with_suffix('.recalculated.xlsx')
    with ZipFile(temporary,'w',ZIP_DEFLATED) as z:
        for name,raw in original_files.items():
            z.writestr(name,raw)
    temporary.replace(original)
    return count


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('original',type=Path)
    p.add_argument('recalculated',type=Path)
    a=p.parse_args()
    print(f'Refreshed {refresh(a.original,a.recalculated)} native-table caches; formulas preserved')
