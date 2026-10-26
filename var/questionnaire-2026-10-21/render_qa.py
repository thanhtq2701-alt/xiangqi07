from pathlib import Path
import pypdfium2 as pdfium
import json,sys,re
sys.stdout.reconfigure(encoding='utf-8')
r=Path(__file__).parent
d=pdfium.PdfDocument(r/'qa.pdf')
out=r/'pages';out.mkdir(exist_ok=True)
summ=[]
for i,p in enumerate(d):
    p.render(scale=1.45).to_pil().save(out/f'page-{i+1:02}.png')
    t=p.get_textpage().get_text_range()
    (out/f'page-{i+1:02}.txt').write_text(t,encoding='utf-8')
    lines=[s.strip() for s in t.splitlines() if s.strip()]
    summ.append({'page':i+1,'chars':len(t),'first':lines[1:3],'last':lines[-4:-1]})
(r/'page_summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summ,ensure_ascii=False))
