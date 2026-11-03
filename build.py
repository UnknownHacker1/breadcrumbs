# Builds index.html (standalone) from src/src.html + src/samples/samples.json.
# Run from the repo root: python build.py
import os
here = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(here, 'src', 'src.html'), encoding='utf-8').read().replace('/*SAMPLES*/[]', open(os.path.join(here, 'src', 'samples', 'samples.json'), encoding='utf-8').read())
open(os.path.join(here, 'index.html'), 'w', encoding='utf-8').write(s)
print('built', len(s))
