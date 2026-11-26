"""Record primary input-limit extracts and distinguish typical capacitance."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    rows=[]
    for stem in ['sn74ahc125','sn74ahc14']:
        pdf=ROOT/f'references/ti/{stem}.pdf'
        txt=ROOT/f'verification/net23/research/{stem}.txt'
        rows.append({'source':pdf.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
                     'extraction':txt.relative_to(ROOT).as_posix(),'extraction_sha256':hashlib.sha256(txt.read_bytes()).hexdigest(),
                     'transformation':'Original PDF unchanged, separate pdftotext -layout',
                     'command':['pdftotext','-layout',pdf.relative_to(ROOT).as_posix(),txt.relative_to(ROOT).as_posix()]})
    paths=[Path(__file__)]
    paths += [ROOT/r[key] for r in rows for key in ['source','extraction']]
    paths += [ROOT/'references/net23/sn74lvc2g125.pdf',ROOT/'verification/net23/research/sn74lvc2g125.txt',ROOT/'references/net22/abracon-ach.pdf']
    report={'date':'2026-11-26','sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
            'extractions':rows,'ahc125_input_transition_ns_per_v_at5v_pm0_5':20,
            'ahc14_recommended_table_has_no_input_transition_rate_row':True,
            'lvc2g125_ci_pf':3.5,'lvc2g125_ci_kind':'typical at3.3V, not maximum at5V',
            'ach_cpu_tr_tf_max_ns':40,'ach_master_tr_tf_max_ns':5,
            'scope':'Primary table interpretation, not waveform simulation or slew qualification. No linear/exponential edge shape assumed. Schmitt pair chosen to avoid inferring local slew from an unspecified40ns waveform.',
            'failures':[],'physical_input_interface_qualified':False}
    (ROOT/'verification/net23/research/input-limits.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'input_rate_ahc125_5v_ns_per_v':20,'cpu_receiver':'two spare Schmitt inverters','physical_input_interface_qualified':False}))


if __name__=='__main__':main()
