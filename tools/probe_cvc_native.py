"""Four-state CVC interpreter versus Icarus on identical native probe inputs."""
import hashlib
import json
from pathlib import Path
import re
import tempfile
from run_rtl import run
from run_local_phase_probe import MODELS
from limited_process import run_limited

ROOT=Path(__file__).resolve().parents[1]
EXE=Path('/home/gabri/.local/opt/isa1-cvc-source/build64/cvc64')
OUT=ROOT/'verification/net26/tool-research'

def main():
    source='sim/net26/tb_local_phase_probe.sv'
    models=['sim/net26/cvc_clock_restricted.sv' if n=='sim/net23/clock_models.sv' else n for n in MODELS if n!=source]
    compatible=ROOT/'sim/net26/cvc_compatible';compatible.mkdir(parents=True,exist_ok=True)
    transformed={};transforms=[]
    for n in models+['sim/net26/revert_clock.sv','sim/net26/revert_local.sv','sim/net26/revert_keyboard.sv']:
        original=(ROOT/n).read_text()
        def wrap(match):
            module=match[0]
            found=re.search(r'(?m)^[ \t]{0,1}if\(TIMED\)[ \t]*(.*)$',module)
            if not found:return module
            if found[1].startswith('begin'):
                end=module.rfind('endmodule')
                return module[:found.start()]+'generate\n'+module[found.start():end]+'endgenerate\n'+module[end:]
            if found[1].startswith('always '):
                end=module.rfind('endmodule')
                return module[:found.start()]+'generate if(TIMED) begin : cvc_conditional_guard\n'+found[1]+module[found.end():end]+'end endgenerate\n'+module[end:]
            count=[0]
            def statement(m):
                assert m[1].endswith(';'),m[0]
                count[0]+=1
                return f'generate if(TIMED) begin : cvc_guard_{count[0]}\n'+m[1]+'\nend endgenerate'
            return re.sub(r'(?m)^[ \t]{0,1}if\(TIMED\)[ \t]*(.*)$',statement,module)
        changed=re.sub(r'(?ms)^module\b.*?^endmodule\b',wrap,original)
        if changed!=original:
            p=compatible/n.replace('/','__');p.write_text('// Syntax-only explicit generate regions for CVC; guards and instances unchanged.\n'+changed)
            transformed[n]=p.relative_to(ROOT).as_posix()
            transforms.append({'original':n,'original_sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),'adapted':transformed[n],'adapted_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'transformation':'Replace formerly implicit module-level TIMED generate with explicit generate/if/begin/end/endgenerate, named guard scope only. No changed predicates, state or electrical connections.'})
    report={'date':'2026-11-26','scope':'Tool evaluation only: CVC+interp with explicit generate syntax versus Icarus with original syntax, same native graph/guards. Restricted source projection requires constant qualified VDD/enable; original cancelable model intact. Not compiled-engine adoption or analog proof.',
       'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in list(dict.fromkeys(models+[source,'tools/probe_cvc_native.py','tools/limited_process.py','sim/net26/revert_clock.sv','sim/net26/revert_local.sv','sim/net26/revert_keyboard.sv']))],
       'executable':{'path':str(EXE),'sha256':hashlib.sha256(EXE.read_bytes()).hexdigest()},'syntax_transforms':transforms,'runs':[],'failures':[],'adopted_for_full_program':False}
    configs=[('positive',p,phase,release,low) for p in [0,1] for phase in [-1,4] for release in [60000,12000000] for low in [50,100000]]
    configs +=[(name,0,4 if name!='revert_local' else -1,60000,50) for name in ['revert_clock','revert_local','revert_keyboard']]
    expected={'revert_clock':'DFF clock pulse violation','revert_local':'AHC74 reset recovery violation','revert_keyboard':'DFF clock pulse violation'}
    replace={'revert_clock':'sim/net26/local_reset_probe.sv','revert_local':'sim/net26/local_video_probe.sv','revert_keyboard':'sim/net26/local_keyboard_probe.sv'}
    with tempfile.TemporaryDirectory(prefix='isa1-cvc-native-') as tmp:
        parent=Path(tmp)
        for index,(name,policy,phase,release,low) in enumerate(configs):
            work=parent/str(index);work.mkdir();params={'PROFILE':1,'POLICY':policy,'INITIAL_PHASE':phase,'RAW_RELEASE_NS':release,'RAW_LOW_NS':low,'OFFSET_NS':39}
            text=(ROOT/source).read_text()
            for k,v in params.items():text,count=re.subn(r'\b'+k+r'=[-0-9.]+',k+'='+str(v),text,count=1);assert count==1,k
            bench=work/'probe.sv';bench.write_text(text)
            names=[f'sim/net26/{name}.sv' if n==replace.get(name) else n for n in models]
            cvc=[str(EXE),'-sv','+interp',str(bench)]
            for n in names:cvc +=['-v',str(ROOT/transformed.get(n,n))]
            row={'name':name,'parameters':params,'bench_sha256':hashlib.sha256(bench.read_bytes()).hexdigest(),'cvc':run_limited(cvc,work)}
            iv=['iverilog','-g2012','-Wall','-s','tb_drain_pulse','-o',str(work/'icarus.vvp'),*[str(ROOT/n) for n in names],str(bench)]
            row['compile_icarus']=run(iv,work)
            if row['compile_icarus']['exit']==0:row['icarus']=run(['vvp',str(work/'icarus.vvp')],work,timeout=120)
            cv=row['cvc'];ir=row.get('icarus',{});a=cv.get('stdout','');b=ir.get('stdout','')
            if name=='positive':
                ar=re.findall(r'^(?:RESULT |KEY_CLOCK ).*$',a,re.M);br=re.findall(r'^(?:RESULT |KEY_CLOCK ).*$',b,re.M)
                row['passed']=cv['exit']==0 and ir.get('exit')==0 and len(ar)==2 and ar==br and '$fatal[' not in a and 'failures=0' in a
            else:row['passed']='$fatal[' in a and expected[name] in a and 'RESULT ' not in a and ir.get('exit') not in (None,0) and expected[name] in b
            report['runs'].append(row)
            if not row['passed']:report['failures'].append(index)
            (OUT/'cvc-native-probe.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({'index':index+1,'name':name,'passed':row['passed'],'cvc':cv if not row['passed'] else {'seconds':cv['seconds']},'icarus':ir if not row['passed'] else {'seconds':ir.get('seconds')}}),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
