"""Independent selected pulse polarity/local reset delay and source corners."""
import hashlib
import itertools
import json
from pathlib import Path
import tempfile
from run_local_phase_probe import MODELS
from run_request_skew_probe import once
from run_rtl import run

ROOT=Path(__file__).resolve().parents[1]

def main():
    mapping={};origins=[]
    for kind in ['video','reset','control','keyboard']:
        n=f'sim/net26/local_{kind}_probe.sv';text=(ROOT/n).read_text();origins.append(n)
        text=once(text,'PROFILE=0)', 'PROFILE=0,POLARITY=0,LOCAL_EARLY=0,parameter realtime LOCAL_DELAY=8.5)') if kind=='video' else once(text,'PROFILE=0,','PROFILE=0,POLARITY=0,') if kind=='reset' else once(text,'PROFILE=0)','PROFILE=0,POLARITY=0)')
        if kind=='video':
            text=once(text,'.RISE_T(10.5),.FALL_T(PROFILE?1:10.5)', '.RISE_T(POLARITY?1:10.5),.FALL_T(POLARITY?10.5:1)')
            text=once(text,'assign #(TIMED?8.5:0) n_LOCAL_RESET_CLK=', 'assign #(TIMED?LOCAL_DELAY:0) n_LOCAL_RESET_CLK=')
            lines=text.splitlines()
            for i in range(2):
                indexes=[j for j,s in enumerate(lines) if f') U37_{i}(' in s];assert len(indexes)==1
                j=indexes[0];assert '.EARLY(0 && EARLY_CAPTURE)' in lines[j]
                lines[j]=lines[j].replace('.EARLY(0 && EARLY_CAPTURE)', '.EARLY(LOCAL_EARLY)')
            text='\n'.join(lines)+'\n'
        else:
            assert text.count('TIMED?(PROFILE?8.5:10):0')==3
            assert text.count('TIMED?(PROFILE?1:10):0')==3
            text=text.replace('TIMED?(PROFILE?8.5:10):0','TIMED?(POLARITY?1:8.5):0')
            text=text.replace('TIMED?(PROFILE?1:10):0','TIMED?(POLARITY?8.5:1):0')
        dest=f'sim/net26/matrix_{kind}.sv';(ROOT/dest).write_text('// GENERATED selected corner projection; strict predicates unchanged.\n'+text);mapping[n]=dest
    n='sim/net26/tb_local_phase_probe.sv';bench=(ROOT/n).read_text();origins.append(n)
    bench=once(bench,'PAUSE_LEVEL=-1;', 'PAUSE_LEVEL=-1,POLARITY=0,LOCAL_EARLY=0,P3_EARLY=1,FREQ_PPM=50;\n parameter realtime LOCAL_DELAY=8.5;\n defparam video.LOCAL_EARLY=LOCAL_EARLY,video.LOCAL_DELAY=LOCAL_DELAY,clocks.MASTER_PERIOD_NS=39.721946/(1+FREQ_PPM*1e-6);')
    assert bench.count('.PROFILE(PROFILE)')==4
    bench=bench.replace('.PROFILE(PROFILE)', '.PROFILE(PROFILE),.POLARITY(POLARITY)')
    bench=once(bench,'.EARLY_CAPTURE(1)', '.EARLY_CAPTURE(P3_EARLY)')
    dest='sim/net26/tb_local_phase_matrix.sv';(ROOT/dest).write_text('// GENERATED selected corner matrix.\n'+bench);mapping[n]=dest
    names=[mapping.get(n,n) for n in MODELS]
    report={'date':'2026-11-26','scope':'128 selected digital corners: both pulse polarities, local AND1/8.5ns, local FF CQ1/10.5ns, P3 CQ1/12.5ns, master source +/-50ppm, two binary policies, two RAW widths. Native graph projections including keyboard; original HC monitors and independent KEY5ns guard unchanged. Other delays fixed; not full PVT/jitter/traces/metastability/analog qualification.',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in list(dict.fromkeys(names+origins+['tools/run_local_phase_matrix.py','tools/run_local_phase_probe.py']))],
      'cases':[],'failures':[],'production_released':False}
    configs=list(itertools.product([0,1],[1,8.5],[0,1],[0,1],[-50,50],[0,1],[50,100000]))
    with tempfile.TemporaryDirectory(prefix='isa1-local-matrix-') as tmp:
        work=Path(tmp)
        for index,(polarity,delay,early,p3,ppm,policy,low) in enumerate(configs):
            params={'PROFILE':1,'INITIAL_PHASE':4,'RAW_RELEASE_NS':60000,'OFFSET_NS':39,'POLARITY':polarity,'LOCAL_DELAY':delay,'LOCAL_EARLY':early,'P3_EARLY':p3,'FREQ_PPM':ppm,'POLICY':policy,'RAW_LOW_NS':low}
            cmd=['iverilog','-g2012','-Wall','-s','tb_drain_pulse',*[f'-Ptb_drain_pulse.{k}={v}' for k,v in params.items()],'-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'parameters':params,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=120)
            r=row.get('execution',{});row['passed']=r.get('exit')==0 and 'RESULT ' in r.get('stdout','') and 'failures=0' in r.get('stdout','') and not row['compile']['stderr']
            report['cases'].append(row)
            if not row['passed']:report['failures'].append(params)
            (ROOT/'verification/net26/local-phase-matrix.json').write_text(json.dumps(report,indent=2)+'\n')
            if not row['passed'] or (index+1)%8==0:print(json.dumps({'completed':index+1,'total':len(configs),'passed':row['passed'],'parameters':params,'execution':r if not row['passed'] else None}),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
