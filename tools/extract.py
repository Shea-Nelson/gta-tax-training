#!/usr/bin/env python3
"""Extract text from every downloaded source into source/text/<sub>/<name>.txt (idempotent)."""
import os, subprocess, json
ROOT='/workspace/gta/sut-training/source'
for sub in ('forms','brochures','tips','tutorials','documents'):
    d=f'{ROOT}/{sub}'
    if not os.path.isdir(d): continue
    os.makedirs(f'{ROOT}/text/{sub}',exist_ok=True)
    for f in os.listdir(d):
        out=f'{ROOT}/text/{sub}/{f}.txt'
        if os.path.exists(out): continue
        p=f'{d}/{f}'
        try:
            if f.lower().endswith('.pdf'):
                subprocess.run(['pdftotext','-layout',p,out],timeout=60,check=False)
            elif f.lower().endswith('.docx'):
                import docx; open(out,'w').write('\n'.join(x.text for x in docx.Document(p).paragraphs))
        except Exception as e: print('ERR',f,e)
