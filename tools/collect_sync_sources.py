"""NET34 bounded primary-source capture; reused older PDFs stay unchanged."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'references/net34'
URLS={'sn74lvc1g132.pdf':'https://www.ti.com/lit/ds/symlink/sn74lvc1g132.pdf',
      'tps731.pdf':'https://www.ti.com/lit/ds/symlink/tps731.pdf'}

def main():
    OUT.mkdir(parents=True,exist_ok=True);rows=[]
    for name,url in URLS.items():
        target=OUT/name;assert not target.exists()
        row={'path':target.relative_to(ROOT).as_posix(),'requested_url':url,'date':'2026-11-27'}
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:
                content=response.read(8*1024**2+1)
                assert content.startswith(b'%PDF-') and len(content)<=8*1024**2
                row.update(final_url=response.geturl(),status=response.status)
            target.write_bytes(content);row.update(downloaded=True,sha256=hashlib.sha256(content).hexdigest(),bytes=len(content))
            text=target.with_suffix('.pdf.txt')
            result=subprocess.run(['pdftotext','-layout',str(target),str(text)],capture_output=True,text=True,timeout=30)
            row.update(extraction_exit=result.returncode,extraction_stderr=result.stderr)
            assert result.returncode==0
            row.update(extraction=text.relative_to(ROOT).as_posix(),extraction_sha256=hashlib.sha256(text.read_bytes()).hexdigest())
        except Exception as error:row.update(downloaded=target.exists(),error=repr(error))
        rows.append(row)
        (OUT/'sources.json').write_text(json.dumps({'date':'2026-11-27','scope':'Candidate source capture, not BOM adoption',
            'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'limits':'25s network timeout,8MiB per PDF,30s pdftotext',
            'rows':rows},indent=2)+'\n',newline='\n')
        print(json.dumps({'file':name,'downloaded':row['downloaded'],'error':row.get('error')}),flush=True)

if __name__=='__main__':main()
