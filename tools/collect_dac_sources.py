"""Preserve bounded primary-source downloads for VGA architecture review."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'references/net31'
URLS={
 'ths8136.pdf':'https://www.ti.com/lit/ds/symlink/ths8136.pdf',
 'sn74lvc8t245.pdf':'https://www.ti.com/lit/ds/symlink/sn74lvc8t245.pdf',
 'tlv755p.pdf':'https://www.ti.com/lit/ds/symlink/tlv755p.pdf',
 'tmux1133.pdf':'https://www.ti.com/lit/ds/symlink/tmux1133.pdf',
 'ref33.pdf':'https://www.ti.com/lit/ds/symlink/ref33.pdf',
 'opa350.pdf':'https://www.ti.com/lit/ds/symlink/opa350.pdf',
 'adv7125.pdf':'https://www.analog.com/media/en/technical-documentation/data-sheets/adv7125.pdf'}

def main():
    OUT.mkdir(parents=True,exist_ok=True);rows=[]
    for name,url in URLS.items():
        path=OUT/name;assert not path.exists(),'Preserve previous download'
        row={'file':path.relative_to(ROOT).as_posix(),'requested_url':url,'access_date':'2026-11-27'}
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 ISA1-engineering-source-audit'})
            with urllib.request.urlopen(request,timeout=25) as response:
                data=response.read(8*1024**2+1)
                assert len(data)<=8*1024**2 and data.startswith(b'%PDF-')
                row.update(final_url=response.geturl(),status=response.status,content_type=response.headers.get('Content-Type'))
            path.write_bytes(data);row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),downloaded=True)
            target=OUT/(name+'.txt')
            result=subprocess.run(['pdftotext','-layout',str(path),str(target)],capture_output=True,text=True,timeout=30)
            row.update(extraction_exit=result.returncode,extraction_stderr=result.stderr)
            assert result.returncode==0
            row.update(extraction=target.relative_to(ROOT).as_posix(),extraction_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        except Exception as error:row.update(downloaded=path.exists(),error=repr(error))
        rows.append(row)
        (OUT/'sources.json').write_text(json.dumps({'date':'2026-11-27','scope':'Candidate-source research, not BOM adoption or validation.',
            'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'limits':'25s network timeout per request,8MiB per PDF,30s extraction; no historical sources overwritten.',
            'pdftotext':subprocess.run(['pdftotext','-v'],capture_output=True,text=True).stderr,'rows':rows},indent=2)+'\n')
        print(json.dumps({'source':name,'downloaded':row['downloaded'],'error':row.get('error')}),flush=True)

if __name__=='__main__':main()
