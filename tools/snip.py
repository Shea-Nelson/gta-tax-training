#!/usr/bin/env python3
"""snip.py FILE REGEX [LEN] - print text around each match (whitespace collapsed)."""
import re,sys
t=re.sub(r'\s+',' ',open(sys.argv[1],errors='ignore').read()); n=int(sys.argv[3]) if len(sys.argv)>3 else 800
for m in re.finditer(sys.argv[2],t,re.I): print('>>',t[max(0,m.start()-60):m.start()+n],'\n')
