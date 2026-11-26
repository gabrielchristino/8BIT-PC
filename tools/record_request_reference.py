"""Preserve local primary HC74 extraction provenance without fetching new bytes."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    names=['references/ti/sn74hc74.pdf','verification/net24/research/sn74hc74.txt',
           'tools/record_request_reference.py']
    data={'date':'2026-11-26','source_url':'https://www.ti.com/lit/ds/symlink/sn74hc74.pdf',
          'revision':'SCLS094F June2021, preserved original PDF',
          'sources':[{'path':n,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in names],
          'command':['pdftotext','-layout',names[0],names[1]],'transformation':'Original PDF unchanged; separate layout text extraction',
          'selected_condition':'SN74 (not54) table6.7/6.9,4.5V,-40..85C',
          'clock_q_max_ns':44,'clock_q_min_ns':None,'clock_pulse_min_ns':20,
          'data_setup_min_ns':25,'data_hold_min_ns':0,'clear_recovery_min_ns':6,
          'probe_first_cq_ns':[0,1,6,44],
          'interpretation':'No minimum propagation is listed. Values0/1/6 are illustrative admitted models, not guaranteed measured silicon. Common clock removes the selected inter-buffer skew but extracted pin skew and first-stage MTBF remain open.',
          'failures':[]}
    (ROOT/'verification/net24/research/reference.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'revision':data['revision'],'minimum_cq_specified':False,'pulse_ns':20,'setup_ns':25}))


if __name__=='__main__':main()
