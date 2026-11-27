"""Capture the selected regulator in a separate ledger, preserving first research."""
import hashlib
import inspect
import json
from pathlib import Path
import collect_sync_sources as template

if __name__=='__main__':
    env=dict(template.__dict__)
    env.update(__file__=__file__,URLS={'tps709.pdf':'https://www.ti.com/lit/ds/symlink/tps709.pdf'})
    source=inspect.getsource(template.main).replace("'sources.json'","'regulator-source.json'")
    exec(source,env);env['main']()
    path=template.OUT/'regulator-source.json';record=json.loads(path.read_text())
    record['collector_template_sha256']=hashlib.sha256(Path(template.__file__).read_bytes()).hexdigest()
    path.write_text(json.dumps(record,indent=2)+'\n',newline='\n')
