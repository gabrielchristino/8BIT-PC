"""Native ERC/export and joined cross-sheet input loads, no waiver."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_cpu_global import KICAD

ROOT=Path(__file__).resolve().parents[1]

def main():
    functions={};loads={};reports=[]
    for kind,name in [('video','phase_drain_video'),('reset','phase_drain_reset')]:
        folder=ROOT/'hardware'/name;out=ROOT/'verification/net25/native'/kind
        defs=json.loads((folder/'package-functions.json').read_text())
        parts=json.loads((folder/'design.json').read_text())['parts']
        functions[kind]={p['reference']:{defs[p['part']]['pins'][pin]['name']:net for pin,net in p['nets'].items()} for p in parts}
        for p in parts:
            for pin,net in p['nets'].items():
                if net not in (None,'+5V','GND') and defs[p['part']]['pins'][pin]['type']=='input':
                    loads.setdefault((kind,net),[]).append(p['reference']+'.'+pin)
        cmd=[KICAD,'sch','erc','--format','json','--severity-all','--exit-code-violations','-o',str(out/'erc.json'),str(folder/(name+'.kicad_sch'))]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        assert (out/'erc.json').is_file(),r.stderr
        native=json.loads((out/'erc.json').read_text());counts={}
        for sheet in native.get('sheets',[]):
            for v in sheet.get('violations',[]):counts[v['type']]=counts.get(v['type'],0)+1
        report={'date':'2026-11-26','command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'violation_counts':counts,'erc_passed':r.returncode==0,'production_released':False,
            'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [Path(__file__),folder/(name+'.kicad_sch'),folder/(name+'.kicad_pro'),folder/'bus_packages.kicad_sym']]}
        (out/'erc-summary.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report)
        subprocess.run([KICAD,'sch','export','pdf','-o',str(out/(name+'.pdf')),str(folder/(name+'.kicad_sch'))],check=True,capture_output=True,timeout=120)
        subprocess.run(['pdftoppm','-scale-to','1800','-png','-singlefile',str(out/(name+'.pdf')),str(out/'preview')],check=True,capture_output=True,timeout=120)
    vf,rf=functions['video'],functions['reset']
    contracts=[(vf['U8']['A'],'SAFE'),(vf['U8']['Q3'],'PHASE_RUN'),(vf['U8']['CLR_N'],'PHASE_INIT_N'),
        (vf['U9']['CLR_N'],'+5V'),(vf['U9']['A'],'PHASE_SHIFT_IN'),(vf['U11']['CLR0_N'],'+5V'),
        (vf['U25']['Y0'],'G_2'),(vf['U25']['A0'],'P1'),(vf['U25']['B0'],'P2'),
        (vf['U24']['Y2'],'PHASE_SHIFT_IN'),(vf['U24']['Y3'],'LOCAL_RESET_N'),
        (vf['U27']['Y1'],'BANK_ARM'),(vf['U27']['A1'],'READY'),(vf['U27']['B1'],'BANK_SYNC1'),
        (rf['U3']['D0'],'BANK_ARM'),(rf['U3']['Q0'],'RESET_SYNC1')]
    assert all(a==b for a,b in contracts),contracts
    clockpins=[f'{ref}.{fn}' for ref,pins in vf.items() for fn,net in pins.items() if fn.startswith('CLK') and net=='BUF_2_2']
    assert sorted(clockpins)==['U11.CLK0','U8.CLK','U9.CLK']
    joins={
        'phase_init_n':loads['reset','DELAY_CLEAR_N']+['video/'+p for p in loads['video','PHASE_INIT_N']],
        'bank_sync1':loads['reset','RESET_SYNC1']+['video/'+p for p in loads['video','BANK_SYNC1']],
        'bank_arm':loads['reset','BANK_ARM'],
        'phase_run':loads['video','PHASE_RUN'],
        'local_reset':loads['video','LOCAL_RESET_N'],
        'common_master':clockpins}
    assert all(len(p)<=4 for p in joins.values())
    source_names=['tools/check_phase_drain_native.py','references/net22/sn74ahc164.pdf','references/ti/sn74ahc08.pdf','references/ti/sn74ahc32.pdf']
    for name in ['phase_drain_video','phase_drain_reset']:
        source_names +=['hardware/'+name+'/'+p for p in ['design.json','package-functions.json',name+'_netlist.sv']]
    report={'date':'2026-11-26','pin_contracts_checked':len(contracts),'clock_pins':clockpins,
        'cross_sheet_loads':{n:{'pins':p,'conditional_pf':10*len(p)+10} for n,p in joins.items()},
        'capacitance_assumption':'10pF maximum Ci at5V plus10pF trace budget, not extracted/global all-VDD qualification.',
        'digital_ics_video':36,'digital_ics_reset':7,'supervisor_ics_reset':1,'oscillator_modules':2,
        'strict_cold_clock_pulses_qualified':False,'power_budget_closed':False,'production_released':False,'failures':[],
        'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in source_names]}
    (ROOT/'verification/net25/topology.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'erc':[r['violation_counts'] for r in reports],'topology':report},ensure_ascii=False))

if __name__=='__main__':main()
