from pathlib import Path
root=Path(__file__).resolve().parents[3]
for path in [root/'art_source/Condor/README.md',root/'art_source/Brad_Turner/README.md']:
    lines=[]
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if any(marker in line for marker in ['Ã','Â','â€']):
            try:line=line.encode('cp1252').decode('utf-8')
            except (UnicodeEncodeError,UnicodeDecodeError):pass
        lines.append(line.replace('V1–V7','V1–V14'))
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
