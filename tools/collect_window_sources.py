"""NET35 primary-source collection using the bounded NET34 capture helper."""
import hashlib
import inspect
import json
from pathlib import Path
import collect_sync_sources as template

if __name__=='__main__':
    out=template.ROOT/'references/net35';out.mkdir(parents=True,exist_ok=True)
    env=dict(template.__dict__);env.update(__file__=__file__,OUT=out,URLS={
        'lt3042.pdf':'https://www.analog.com/media/en/technical-documentation/data-sheets/lt3042.pdf',
        'tps3890.pdf':'https://www.ti.com/lit/ds/symlink/tps3890.pdf',
        'tps3899.pdf':'https://www.ti.com/lit/ds/symlink/tps3899.pdf'})
    exec(inspect.getsource(template.main),env);env['main']()
    p=out/'sources.json';r=json.loads(p.read_text())
    r['template_sha256']=hashlib.sha256(Path(template.__file__).read_bytes()).hexdigest()
    p.write_text(json.dumps(r,indent=2)+'\n',newline='\n')
