"""Check exact native delta, cross-sheet clocks and unwaived partial ERC."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_cpu_global import KICAD

ROOT=Path(__file__).resolve().parents[1]

def main():
    graphs={};loads={};ercs={};paths=['tools/check_local_phase_native.py']
    for kind,parent in [('video','phase_drain_video'),('reset','phase_drain_reset'),('keyboard','keyboard_500')]:
        name='local_phase_'+kind;folder=ROOT/'hardware'/name;out=ROOT/'verification/net26/native'/kind
        defs=json.loads((folder/'package-functions.json').read_text());data=json.loads((folder/'design.json').read_text())
        parts={p['reference']:p for p in data['parts']}
        graphs[kind]={ref:{defs[p['part']]['pins'][pin]['name']:net for pin,net in p['nets'].items()} for ref,p in parts.items()}
        old={p['reference']:p for p in json.loads((ROOT/'hardware'/parent/'design.json').read_text())['parts']}
        assert set(parts)==set(old)|({'U37','C37'} if kind=='video' else set())
        changes=[]
        for ref,p in old.items():
            other=parts[ref]
            if other['part']!=p['part']:changes.append((ref,'part',p['part'],other['part']))
            assert set(other['nets'])==set(p['nets'])
            for pin,net in p['nets'].items():
                if other['nets'][pin]!=net:changes.append((ref,pin,net,other['nets'][pin]))
        assert len(changes)==(1 if kind=='keyboard' else 3),(kind,changes)
        if kind=='keyboard':assert changes==[('U1','part','SN74HC174','SN74AHC174')]
        for ref,p in parts.items():
            for pin,net in p['nets'].items():
                if net not in (None,'+5V','GND') and defs[p['part']]['pins'][pin]['type']=='input':loads.setdefault((kind,net),[]).append(ref+'.'+pin)
        cmd=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(out/'erc.json'),str(folder/(name+'.kicad_sch'))]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        raw=json.loads((out/'erc.json').read_text());counts={}
        for sheet in raw.get('sheets',[]):
            for v in sheet.get('violations',[]):counts[v['type']]=counts.get(v['type'],0)+1
        ercs[kind]=counts
        files=[folder/(name+'.kicad_sch'),folder/(name+'.kicad_pro'),*folder.glob('*.kicad_sym'),Path(__file__)]
        report={'date':'2026-11-26','command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'violation_counts':counts,
            'erc_passed':r.returncode==0,'production_released':False,'native_changes':changes,
            'scope':'Unwaived partial sheet ERC, not global board/ERC release.',
            'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
        (out/'erc-summary.json').write_text(json.dumps(report,indent=2)+'\n')
        subprocess.run([KICAD,'sch','export','pdf','-o',str(out/(name+'.pdf')),str(folder/(name+'.kicad_sch'))],check=True,capture_output=True,timeout=120)
        subprocess.run(['pdftoppm','-scale-to','1800','-png','-singlefile',str(out/(name+'.pdf')),str(out/'preview')],check=True,capture_output=True,timeout=120)
        paths+=['hardware/'+name+'/'+p for p in ['design.json','package-functions.json',name+'_netlist.sv']]
    vf,rf,kf=graphs['video'],graphs['reset'],graphs['keyboard']
    assert vf['U24']['A3']=='P1' and vf['U24']['B3']=='+5V' and vf['U24']['Y3']=='LOCAL_RESET_CLK'
    assert all(vf['U37'][f'CLK{i}']=='LOCAL_RESET_CLK' and vf['U37'][f'CLR{i}_N']=='SAFE' for i in range(2))
    assert vf['U37']['D0']=='+5V' and vf['U37']['D1']==vf['U37']['Q0']=='LOCAL_RESET_STAGE1' and vf['U37']['Q1']=='LOCAL_RESET_N'
    assert rf['U8']['A1']=='GND' and rf['U8']['OE1_N']=='+5V' and rf['U8']['Y1'] is None
    reset_sv=(ROOT/'hardware/local_phase_reset/local_phase_reset_netlist.sv').read_text()
    assert 'assign access_clk=n_BACKEND;' in reset_sv
    assert vf['U11']['Q0']=='BACKEND' and vf['U11']['CLR0_N']=='+5V' and vf['U9']['CLR_N']=='+5V'
    assert kf['U1']['CLK']=='BUF_1_0' and kf['U1']['CLR_N']=='BANK_RESET_N'
    control=json.loads((ROOT/'hardware/common_request/design.json').read_text())['parts']
    cdefs=json.loads((ROOT/'hardware/common_request/package-functions.json').read_text())
    cclock=[p['reference']+'.'+pin for p in control for pin,net in p['nets'].items() if net=='CLK' and cdefs[p['part']]['pins'][pin]['type']=='input']
    joins={'backend_Q':loads['reset','BACKEND']+['control/'+p for p in cclock],
        'master':loads['video','BUF_2_2'],'phase1':loads['video','P1'],'local_pair_clock':loads['video','LOCAL_RESET_CLK'],
        'local_reset':loads['video','LOCAL_RESET_N'],'phase_run':loads['video','PHASE_RUN'],
        'phase_init':loads['reset','DELAY_CLEAR_N']+['video/'+p for p in loads['video','PHASE_INIT_N']],
        'bank_sync1':loads['reset','RESET_SYNC1']+['video/'+p for p in loads['video','BANK_SYNC1']],
        'bank_arm':loads['reset','BANK_ARM'],'keyboard_mmio_clock_group':loads['keyboard','BUF_1_0']}
    expected={'backend_Q':4,'master':3,'phase1':3,'local_pair_clock':2,'local_reset':4,'phase_run':1,'phase_init':3,'bank_sync1':2,'bank_arm':1,'keyboard_mmio_clock_group':4}
    assert {n:len(p) for n,p in joins.items()}==expected
    period=39.721946/(1+50e-6)
    report={'date':'2026-11-26','cross_sheet_loads':{n:{'pins':p,'conditional_pf':10*len(p)+10} for n,p in joins.items()},
      'capacitance_assumption':'Ci<=10pF at5V plus10pF trace budget; not extracted/all-VDD qualification.',
      'conditional_pulse_budget':{'master_period_min_ns':period,'backend_cq_spread_ns':9.5,'each_ahc_buffer_spread_ns':7.5,
          'controller_buffer_stages':1,'controller_lower_ns':period-9.5-7.5,'controller_required_ns':20,
          'keyboard_buffer_stages':3,'keyboard_lower_ns':period-9.5-3*7.5,'keyboard_required_ns':5,
          'scope':'Selected datasheet bounds, valid isolated master-clock phase pulses, source ppm only; no jitter/trace skew/global PVT/analog guarantee.'},
      'candidate_video_ics':37,'candidate_keyboard_ics':41,'reset_digital_ics':7,'reset_supervisor_ics':1,'oscillator_modules':2,
      'erc_counts':ercs,'production_released':False,'failures':[],
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in paths+[
        'hardware/common_request/design.json','hardware/common_request/package-functions.json','references/ti/sn74ahc174.pdf','references/ti/sn74ahc125.pdf','references/ti/sn74ahc74.pdf']]}
    (ROOT/'verification/net26/topology.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'erc':ercs,'loads':expected,'controller_pulse_ns':period-17,'keyboard_pulse_ns':period-32}))

if __name__=='__main__':main()
