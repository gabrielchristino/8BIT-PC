def emit(defs,parts):
    OUT.mkdir(parents=True,exist_ok=True);VERIFY.mkdir(parents=True,exist_ok=True)
    prepared={kind:symbol(kind,spec) for kind,spec in defs.items()};sheet=uid('sheet')
    (OUT/'sync_packages.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+' '.join(v[0].replace('(symbol "NET34:','(symbol "') for v in prepared.values())+')\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "NET34") (type "KiCad") (uri "${KIPRJMOD}/sync_packages.kicad_sym") (options "") (descr "Experimental DAC leaf, not production")))\n')
    save(OUT/(NAME+'.kicad_pro'),{'meta':{'filename':NAME+'.kicad_pro','version':1}})
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A3")',
        '(title_block (title "ISA-1 supervised 3.3V sync - experimental") (date "2026-11-27") (rev "NET34") (comment 1 "VGA PROTECTION / POWER TRANSIENTS / PCB UNQUALIFIED"))',
        '(lib_symbols '+' '.join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];height=25 if ref.startswith('U') else 7
        props=f'(property "Reference" "{ref}" (at {x} {y-height} 0) (effects (font (size 1 1)))) (property "Value" "{p["value"]}" (at {x} {y-height+2.54} 0) (effects (font (size 1 1))))'
        pin_ids=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET34:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props} {pin_ids} (instances (project "{NAME}" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,net in p['nets'].items():
            dx,dy,angle=prepared[kind][1][pin];px,py=x+dx,y-dy
            rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':net or 'NC'})
            if net is None:lines.append(f'(no_connect (at {px:.3f} {py:.3f}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{net}" (at {px:.3f} {py:.3f} 0) (effects (font (size 0.65 0.65)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')']
    (OUT/(NAME+'.kicad_sch')).write_text('\n'.join(lines)+'\n')
    with (OUT/'pinmap.csv').open('w',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    save(OUT/'package-functions.json',defs)
    save(OUT/'design.json',{'date':'2026-11-27','base_git_commit':BASE,'status':'standalone diagnostic experiment, not integrated or calibrated','parts':parts})
