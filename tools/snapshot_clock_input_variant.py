"""Preserve the tested intermediate AHC125 CPU receiver before Schmitt reuse."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'verification/net23/development/pre-cpu-schmitt'


def main():
    assert not DEST.exists(),'Snapshot is immutable'
    paths=[ROOT/'tools/build_clocked_reset.py',ROOT/'tools/check_clock_source_loads.py',ROOT/'docs/engineering/NET23.md']
    paths += [p for p in (ROOT/'hardware/clocked_reset').rglob('*') if p.is_file() and p.suffix!='.kicad_prl']
    paths += [p for p in (ROOT/'verification/net23').rglob('*') if p.is_file() and 'development' not in p.relative_to(ROOT/'verification/net23').parts]
    records=[]
    for path in paths:
        name=path.relative_to(ROOT)
        target=DEST/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
        records.append({'original_path':name.as_posix(),'snapshot':target.relative_to(ROOT).as_posix(),
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'copied_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    report={'date':'2026-11-26','scope':'Intermediate NET23 configuration with standard AHC125 CPU receiver. Preserved before change to two idle AHC14 gates; do not attribute these results to the subsequent circuit.',
            'source':{'path':'tools/snapshot_clock_input_variant.py','sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'files':records,'failures':[r['original_path'] for r in records if r['sha256']!=r['copied_sha256']]}
    (DEST/'snapshot.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'preserved_files':len(records),'failures':report['failures']}))


if __name__=='__main__':main()
