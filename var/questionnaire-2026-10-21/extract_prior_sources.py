from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json

out = Path(__file__).parent
sources = {
    'V4': Path(r'E:\ThanhTQ\App cờ tướng\10-14\V4.docx'),
    'UX': Path(r'E:\ThanhTQ\App cờ tướng\10-13\UI UX + Luat.docx'),
}
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for key, path in sources.items():
    with ZipFile(path) as z:
        root = etree.fromstring(z.read('word/document.xml'))
        blocks = []
        for p in root.xpath('/w:document/w:body//w:p', namespaces=ns):
            text = ''.join(p.xpath('.//w:t/text()', namespaces=ns))
            if text.strip():
                blocks.append(text)
        (out / f'{key}_fulltext.txt').write_text('\n'.join(f'{i+1:04d} {s}' for i,s in enumerate(blocks)), encoding='utf-8')
        (out / f'{key}_blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding='utf-8')
        print(key, 'paragraphs', len(blocks), 'table paragraphs', len(root.xpath('/w:document/w:body//w:tbl//w:p', namespaces=ns)))
