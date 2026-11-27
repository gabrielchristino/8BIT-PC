"""Additional primary PDF capture via Windows network; preserve first failures."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'references/net31'
SOURCES={
 'ad9760.pdf':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD9760.pdf',
 'ad9748.pdf':'https://www.analog.com/media/en/technical-documentation/data-sheets/AD9748.pdf',
 'adv7125-retry.pdf':'https://www.analog.com/media/en/technical-documentation/data-sheets/ADV7125.pdf'}

def main():
    rows=[]
    for name,url in SOURCES.items():
        path=OUT/name;assert not path.exists()
        row={'date':'2026-11-27','requested_url':url,'path':path.relative_to(ROOT).as_posix()}
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=20) as response:
                data=response.read(8*1024**2+1);assert len(data)<=8*1024**2 and data.startswith(b'%PDF-')
                row.update(status=response.status,final_url=response.geturl())
            path.write_bytes(data);row.update(downloaded=True,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        except Exception as error:row.update(downloaded=False,error=repr(error))
        rows.append(row)
        (OUT/'supplement.json').write_text(json.dumps({'date':'2026-11-27','scope':'Research only; no BOM adoption.',
            'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rows':rows},indent=2)+'\n',newline='\n')
        print(json.dumps({'source':name,**row}),flush=True)

if __name__=='__main__':main()
