"""Record reviewed tabular allowances; deliberately leave board current open."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net28'
# mA per package at the datasheet test conditions. For older HC tables the
# larger listed temperature/family-column value is deliberately retained.
# These mixed-condition entries do NOT establish an all-VDD board limit.
MA={
 'SN74HC273':'.160','SN74HC157':'.160','CD74HC283':'.160',
 'SN74HC04':'.040','SN74HC125':'.160','SN74HC174':'.160',
 'SN74HC74':'.040','SN74HC377':'.160','SN74HC08':'.040',
 'SN74HC32':'.040','SN74HC161':'.160','SN74HCT377':'.160',
 'AT28HC64B':'40','SN74HC138':'.160','SN74HC139':'.160','SN74HC86':'.040',
 'SN74AHC174':'.040','SN74AHC125':'.040','SN74AHC08':'.020',
 'SN74AHC32':'.020','SN74AHC04':'.020','AS7C256A_28SOJ':'75',
 'AT28C256_28PDIP':'50','SN74AHCT157':'.020','SN74HCT244':'.160',
 'SN74LV161A':'.020','SN74AHC574':'.040','SN74AHC164':'.040',
 'SN74LVC1G27':'.010','SN74AHC74':'.020','SN74AHC14':'.020',
 'TPS3808G01DBVR':'.006','ACH_CPU_CONFIG':'30','ACH_MASTER_CONFIG':'45'}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    evidence_path=OUT/'power-evidence/extractions.json'
    evidence=json.loads(evidence_path.read_text())
    assert set(MA)=={r['family'] for r in evidence['rows']}
    rows=[]
    for r in evidence['rows']:
        p=ROOT/r['extraction'];pdf=ROOT/r['pdf']
        assert digest(p)==r['extraction_sha256'] and digest(pdf)==r['pdf_sha256']
        family=r['family'];allowance=Decimal(MA[family])
        lines=p.read_text().split('\n')
        # Preserve line and PDF page for independent review, including headers.
        marks=[i for i,line in enumerate(lines) if re.search(r'ICC|IDD.*Supply|Input Current',line)]
        if family.startswith('ACH_'):marks=[i for i,line in enumerate(lines) if 'Input Current' in line]
        excerpts=[{'line':i+1,'page':sum(line.count('\f') for line in lines[:i+1])+1,
            'context':'\n'.join(lines[max(0,i-5):i+5])} for i in marks[:6]]
        assert excerpts,family
        group='oscillator' if family.startswith('ACH_') else 'supervisor' if family.startswith('TPS') else 'memory' if family.startswith(('AT28','AS7')) else 'logic'
        condition='Static ICC, inputs at rails and IO=0; datasheet test VCC, not a dynamic/TTL-input or all-rail guarantee.'
        if group=='memory':condition='Active ICC, IO=0; EEPROM f=5MHz; SRAM largest speed-bin current at fMax/VCCmax. Glitch activity/load not qualified.'
        if group=='oscillator':condition='ACH current bin: CPU below24MHz=30mA; master24..49.999MHz=45mA; configured candidate only, exact order code open.'
        if group=='supervisor':condition='IDD=6uA at VDD6.5V, RESET not asserted, MR/RESET/CT open. Other states/rail not qualified.'
        rows.append({'family':family,'count':r['count'],'group':group,'reference_allowance_ma':str(allowance),
            'subtotal_ma':str(allowance*r['count']),'condition':condition,'evidence':r,'review_excerpts':excerpts,
            'operating_board_current_bound_ma':None})
    subtotals={g:sum(Decimal(r['subtotal_ma']) for r in rows if r['group']==g) for g in ['logic','memory','supervisor','oscillator']}
    # Conditional passive-load arithmetic; no resistor/BOM tolerance is adopted.
    v=Decimal('5.48095')
    resistive={
        'assumed_rail_max_v':str(v),
        'memory_pullups_count':24,'nominal_memory_pullup_ohm':3300,
        'source':'tools/build_memory_bus.py and verification/net13/memory_bus.xml specify3.3k; design.json alone omits value.',
        'memory_if_r_min_3267_ohm_ma':str(Decimal(24)*v/Decimal(3267)*1000),
        'keyboard_if_r_min_99_percent_ma':str(v*(Decimal(16)/(Decimal(270000)*Decimal('.99'))+Decimal(4)/(Decimal(120000)*Decimal('.99')))*1000),
        'sense_divider_if_both_min_999_per_mille_ma':str(v/(Decimal(1220)*Decimal('.999'))*1000),
        'supervisor_pullup_if_99k_min_ma':str(v/Decimal(99000)*1000),
        'valid_only_if':'Assumed rail window and stated Rmin hold; nodes within rails; these are separate resistor contributions, not a total supply bound. RC charging and output leakage excluded.'}
    report={'date':'2026-11-26','base_circuit_commit':'f1c6c27d60d921286ed8729cd6f47e90e5948a3b',
        'scope':'Reviewed datasheet-reference current ledger, not a qualified power budget. No circuit change.',
        'rows':rows,'reference_group_subtotals_ma':{k:str(v) for k,v in subtotals.items()},
        'mixed_condition_reference_sum_ma':str(sum(subtotals.values())),
        'conditional_passive_loads':resistive,
        'ttl_input_examples':[{'family':'SN74HCT377','point':'One input0.5V or2.4V, others at rails, VCC5.5V','ma_per_input':3},
            {'family':'SN74HCT244','point':'One input0.5V or2.4V, others at rails, VCC5.5V','ma_per_input':3},
            {'family':'SN74AHCT157','point':'One input3.4V, others at rails, VCC5.5V','ma_per_input':1.5}],
        'ttl_note':'Specified per-input examples are not an all-valid-TTL-range or simultaneous-all-input guarantee. Must resolve actual net voltages and aggregate current, not simply count packages.',
        'board_current_upper_bound_a':None,'dynamic_current_upper_bound_a':None,
        'missing':['Switching/glitches/CPD upper bounds and extracted loads','TTL and nonrail input currents across actual rail/temperature/voltages','Output drive and passive/RC currents in each state','Startup/inrush and capacitor effective values','Converter/USB-C/reverse isolation/DAC consumption and conversion losses','BOM order codes and qualified thermal/rail window'],
        'sources':[{'path':n,'sha256':digest(ROOT/n)} for n in ['tools/record_power_allowances.py','tools/extract_power_evidence.py','verification/net26/load-inventory.json','tools/build_memory_bus.py','verification/net13/memory_bus.xml']],
        'production_released':False}
    assert sum(r['count'] for r in rows)==462 and subtotals['memory']==Decimal(360)
    (OUT/'power-allowances.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'groups_ma':report['reference_group_subtotals_ma'],'reference_sum_ma':report['mixed_condition_reference_sum_ma'],'board_budget_closed':False}))

if __name__=='__main__':main()
