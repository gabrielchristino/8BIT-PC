"""Verify fail-closed bus/port handling and current timed boundary equivalence."""
import hashlib
import json
from pathlib import Path
from audit_system_pin_loads import build,clean,instance

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net29'

def main():
    adapter=ROOT/'sim/net26/isa1_memory_local_phase.sv'
    text=adapter.read_text();report=build()
    assert report['maximum_input_count']==6 and len(report['nets_above_four_inputs'])==4
    assert len(report['resistor_shortcuts_not_joined'])==4
    cases=[]
    for name,old,new,expected in [
        ('wrong_bus_width','.select(select)','.select(saved_data)','Inconsistent bus width'),
        ('duplicate_port','.select(select)','.select(select),.select(select)','Duplicate named port'),
        ('missing_port',',.key_ready(key_ready)','', 'Port inventory mismatch'),
        ('unrecognized_address_concat','video_address={v[8:2],h}','video_address={v[9:3],h}','Unrecognized video address wiring')]:
        assert text.count(old)>=1
        mutated=text.replace(old,new,1)
        try:build(mutated)
        except (AssertionError,ValueError) as error:
            assert expected in str(error),(name,str(error))
            cases.append({'case':name,'expected_rejection':expected,'observed':str(error),'passed':True,
                'mutated_adapter_sha256':hashlib.sha256(mutated.encode()).hexdigest()})
        else:raise AssertionError('Reader accepted malformed input '+name)
    ideal_path=ROOT/'verification/net26/program/system-tb_rtl_program-ideal.sv'
    timed_path=OUT/'boundary-evidence/timed-bench.sv'
    active_bench=ROOT/'verification/net27/full-timed/attempt-001/compiler-inputs/generated-bench.sv'
    if active_bench.is_file():assert active_bench.read_bytes()==timed_path.read_bytes()
    ideal=clean(ideal_path.read_text());timed=clean(timed_path.read_text())
    for module,name in [('isa1_cpu','dut'),('isa1_clocked_memory','memory')]:
        assert instance(ideal,module,name)==instance(timed,module,name),(module,'Boundary pin connections differ')
    result={'date':'2026-11-26','scope':'Structural reader checks only, not hardware regression, ERC, electrical or timed-boot approval.',
        'positive':{'seven_xml_pin_maps_equal_designs':True,'connected_pins':report['connected_pins'],
            'expected_four_over_budget_nets':True,'four_series_resistors_kept_separate':True,
            'ideal_and_running_timed_cpu_memory_connections_equal':True},
        'negative':cases,'passed':True,'production_released':False,
        'timed_bench_origin':{'path':'verification/net27/full-timed/attempt-001/compiler-inputs/generated-bench.sv',
            'run_source_commit':'ba3353f585fff94469d89674a8c1bdfa08ea70f1',
            'transformation':'Byte-for-byte copy of immutable compiled input solely for boundary comparison; no timed program result claimed.'},
        'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [
            Path(__file__),ROOT/'tools/audit_system_pin_loads.py',adapter,ideal_path,timed_path]]}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'reader-checks.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps({'reader_checks_passed':True,'negative_rejections':len(cases),'timed_boundary_matches':True}))

if __name__=='__main__':main()
