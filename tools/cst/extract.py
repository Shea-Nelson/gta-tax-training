#!/usr/bin/env python3
"""Extract text from every downloaded CST source into source/text/<sub>/<name>.txt (idempotent). PDF via pdftotext -layout,
DOCX via python-docx, XLSX via openpyxl (one TSV block per sheet)."""
import os, subprocess
ROOT = '/workspace/gta/cst-training/source'
for sub in ('forms', 'brochures', 'tips', 'tutorials', 'documents', 'law'):
    d = f'{ROOT}/{sub}'
    if not os.path.isdir(d): continue
    os.makedirs(f'{ROOT}/text/{sub}', exist_ok=True)
    for f in sorted(os.listdir(d)):
        out = f'{ROOT}/text/{sub}/{f}.txt'
        if os.path.exists(out): continue
        p = f'{d}/{f}'; low = f.lower()
        try:
            if low.endswith('.pdf'): subprocess.run(['pdftotext', '-layout', p, out], timeout=90, check=False)
            elif low.endswith('.docx'):
                import docx; open(out, 'w').write('\n'.join(x.text for x in docx.Document(p).paragraphs))
            elif low.endswith('.xlsx'):
                import openpyxl; wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
                with open(out, 'w') as o:
                    for ws in wb.worksheets:
                        o.write(f'## SHEET {ws.title}\n')
                        for row in ws.iter_rows(values_only=True):
                            if any(c is not None for c in row): o.write('\t'.join('' if c is None else str(c) for c in row) + '\n')
        except Exception as e: print('ERR', f, e)
print('done')
