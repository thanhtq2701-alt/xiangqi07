from pathlib import Path
import json
import sys
import pypdfium2 as pdfium

sys.stdout.reconfigure(encoding='utf-8')
work=Path(__file__).resolve().parent
pdf=pdfium.PdfDocument(str(work/'manual.pdf'))
out=work/'pages'
out.mkdir(exist_ok=True)
pages=[]
for i in range(len(pdf)):
    page=pdf[i]
    textpage=page.get_textpage()
    text=textpage.get_text_range()
    png=out/f'page-{i+1:03d}.png'
    page.render(scale=1.6).to_pil().save(png)
    boxes=[]
    for j in range(textpage.count_chars()):
        ch=textpage.get_text_range(j,1)
        if ch.strip():
            l,b,r,t=textpage.get_charbox(j)
            if not (l>=25 and r<=page.get_width()-25 and b>=12 and t<=page.get_height()-12):
                boxes.append({'char':ch,'box':[l,b,r,t]})
    lines=text.splitlines()
    pages.append({'page':i+1,'characters':len(text),'first_lines':lines[:6],'last_lines':lines[-5:],'outside_safe_page':boxes,'image':str(png)})
    textpage.close();page.close()
pdf.close()
(work/'page_report.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(pages),'small_pages':[(p['page'],p['characters']) for p in pages if p['characters']<700],'out_of_bounds':[(p['page'],len(p['outside_safe_page'])) for p in pages if p['outside_safe_page']]},ensure_ascii=False))
