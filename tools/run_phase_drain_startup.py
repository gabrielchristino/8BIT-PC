"""Cold binary phase alternatives, brief RAW pulses and edge-aligned clock pauses."""
import hashlib
import json
from pathlib import Path
import tempfile
from run_rtl import run
from run_phase_drain_probe import MODELS
from run_request_skew_probe import once

ROOT=Path(__file__).resolve().parents[1]

def main():
    source=ROOT/'sim/net25/tb_drain_pulse.sv'
    text=source.read_text()
    text=once(text,'parameter integer PROFILE=0,POLICY=1,INITIAL_PHASE=-1;','parameter integer PROFILE=0,POLICY=1,INITIAL_PHASE=-1,PAUSE_LEVEL=-1;')
    text=once(text,'   repeat(8)@(negedge backend);', '''   if(PAUSE_LEVEL>=0)begin
     if(PAUSE_LEVEL==0)begin @(negedge master);#0.001;force clocks.n_MASTER=0;end
     else begin @(posedge master);#0.001;force clocks.n_MASTER=1;end
     #20;raw=0;#30000;raw=1;#50000;
     if(bank!==0 || safe!==0)$fatal(1,"stopped master released memory banks");
     // Release on the matching oscillator phase, extending the paused high/low.
     // Arbitrary electrical restart pulses are outside this source hypothesis.
     if(PAUSE_LEVEL==0)@(negedge clocks.X2.phase);else @(posedge clocks.X2.phase);
     release clocks.n_MASTER;wait(safe===1);
   end
   repeat(8)@(negedge backend);''')
    dest=ROOT/'sim/net25/tb_drain_startup.sv';dest.write_text('// GENERATED extended pulse fixture.\n'+text)
    names=[n for n in MODELS if n!='sim/net25/tb_drain_pulse.sv']+['sim/net25/tb_drain_startup.sv']
    # Separate diagnostic projection: retain the strict predecessor failure.
    # A clock pulse under a known asserted local CLR is logged, NOT qualified.
    # The original predicate remains fatal whenever CLR is high or unknown.
    original='sim/net24/package_models_pulse_diagnostic.sv'
    model=(ROOT/original).read_text()
    model=once(model,' reg saw_clear=0,saw_clock=0;',' reg saw_clear=0,saw_clock=0;\n integer reset_clock_events=0;')
    old='$fatal(1,"DFF clock pulse violation measured_ns=%0.3f required_ns=20 clr_n=%b",$realtime-clock_changed,clr_n);'
    new='''begin
     if(clr_n===1'b0)begin
       reset_clock_events=reset_clock_events+1;
       $display("OPEN_RESET_CLOCK scope=%m measured_ns=%0.3f required_ns=20 clr_n=%b",$realtime-clock_changed,clr_n);
     end else $fatal(1,"DFF clock pulse violation measured_ns=%0.3f required_ns=20 clr_n=%b",$realtime-clock_changed,clr_n);
   end'''
    model=once(model,old,new)
    diagnostic='sim/net25/package_models_cold_diagnostic.sv'
    (ROOT/diagnostic).write_text('// INVESTIGATION ONLY: CLR-low short clocks remain OPEN constraints, not physical approvals.\n'+model)
    names=[diagnostic if n==original else n for n in names]
    text=once(text,' initial begin #16000000;', ''' always @(control.genblk1.U4_check_second.reset_clock_events)
   if(control.genblk1.U4_check_second.reset_clock_events>0 &&
      (bmem!==1'b0 || control.n_REQ1!==1'b0 || control.n_REQ2!==1'b0))
     $fatal(1,"cold short pulse escaped known asserted reset");
 initial begin #16000000;''')
    dest.write_text('// GENERATED investigation: CLR-low pulse constraints stay OPEN.\n'+text)
    report={'date':'2026-11-26','scope':'All16 low-four-bit binary phase power states plus unknown; RAW released before/after oscillator startup; selected brief glitches and whole-cycle edge-aligned master pauses. No analog power-up distribution, arbitrary restart slew/jitter or RC pulse-train qualification.',
      'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names+[original,'tools/run_phase_drain_startup.py','sim/net25/tb_drain_pulse.sv','tools/run_phase_drain_probe.py']],
      'strict_cold_clock_envelope_qualified':False,'interpretation':'All OPEN_RESET_CLOCK lines remain unqualified20ns constraints. Only functional startup under known asserted reset is observed here; active/unknown CLR pulses still fatal. Original strict rejection remains archived.',
      'cases':[],'failures':[],'production_released':False}
    configs=[]
    for policy in [0,1]:
        for phase in range(-1,16):
            # Preserve an actual initial reset assertion beyond RC max19us.
            # The12ns investigation is archived, not claimed as a passing POR.
            for release in [60000,12000000]:configs.append({'PROFILE':1,'POLICY':policy,'INITIAL_PHASE':phase,'RAW_RELEASE_NS':release,'OFFSET_NS':39})
        for offset in [0,20,30,39,40,60,100]:
            for low in [5,20,50,100,300,1000]:configs.append({'PROFILE':1,'POLICY':policy,'RAW_LOW_NS':low,'OFFSET_NS':offset})
        for level in [0,1]:configs.append({'PROFILE':1,'POLICY':policy,'PAUSE_LEVEL':level,'OFFSET_NS':39})
    with tempfile.TemporaryDirectory(prefix='isa1-drain-startup-') as tmp:
        work=Path(tmp)
        for index,params in enumerate(configs):
            cmd=['iverilog','-g2012','-Wall','-s','tb_drain_pulse',*[f'-Ptb_drain_pulse.{k}={v}' for k,v in params.items()],'-o',str(work/'test.vvp'),*[str(ROOT/n) for n in names]]
            row={'parameters':params,'compile':run(cmd,work)}
            if row['compile']['exit']==0:row['execution']=run(['vvp',str(work/'test.vvp')],work,timeout=90)
            r=row.get('execution',{});row['passed']=r.get('exit')==0 and 'RESULT ' in r.get('stdout','') and 'failures=0' in r.get('stdout','') and not row['compile']['stderr']
            report['cases'].append(row)
            if not row['passed']:report['failures'].append(params)
            (ROOT/'verification/net25/drain-startup.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps({'index':index+1,'total':len(configs),'parameters':params,'passed':row['passed'],'execution':r if not row['passed'] else None}),flush=True)
            if not row['passed']:return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
