def emit(defs,parts):
    prepared={k:package_symbol(k,v) for k,v in defs.items()};sheet=uid('sheet')
    (OUT/'bus_packages.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+' '.join(v[0].replace('(symbol "NET33:','(symbol "') for v in prepared.values())+')\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "NET33") (type "KiCad") (uri "${KIPRJMOD}/bus_packages.kicad_sym") (options "") (descr "ISA-1 memory package pins")))\n')
    project=OUT/'dac_packet_video.kicad_pro'
    if not project.exists():project.write_text(json.dumps({'meta':{'filename':project.name,'version':1}},indent=2)+'\n')
    lines=[f'(kicad_sch (version 20230121) (generator eeschema) (uuid {sheet}) (paper "A1")','(title_block (title "ISA-1 VGA packet adapter - experimental") (date "2026-11-27") (rev "NET-33") (comment 1 "CANDIDATE - LOAD / PCB / ANALOG VALIDATION PENDING - NOT FOR PRODUCTION"))','(lib_symbols '+' '.join(v[0] for v in prepared.values())+')'];rows=[]
    for p in parts:
        ref,kind,x,y=p['reference'],p['part'],p['x'],p['y'];value='100nF' if kind=='C' else '3.3k' if kind=='R' else kind
        ax,ay=(x+5,y-2) if kind in ('C','R') else (x,y-(34.29 if '28' in kind else 25.4))
        props=f'(property "Reference" "{ref}" (at {ax} {ay} 0) (effects (font (size 1 1)))) (property "Value" "{value}" (at {ax} {ay+2.54} 0) (effects (font (size 1 1))))'
        pins=' '.join(f'(pin "{pin}" (uuid {uid(ref+"/"+pin)}))' for pin in p['nets'])
        lines.append(f'(symbol (lib_id "NET33:{kind}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)}) {props} {pins} (instances (project "dac_packet_video" (path "/{sheet}" (reference "{ref}") (unit 1)))))')
        for pin,n in p['nets'].items():
            px,py,angle=prepared[kind][1][pin];px+=x;py=y-py;rows.append({'reference':ref,'part':kind,'pin':pin,'function':defs[kind]['pins'][pin]['name'],'net':n or 'NC'})
            if n is None:lines.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+"/nc/"+pin)}))')
            else:lines.append(f'(label "{n}" (at {px} {py} 0) (effects (font (size 0.65 0.65)) (justify {"right bottom" if angle==0 else "left bottom"})) (uuid {uid(ref+"/label/"+pin)}))')
    lines+=['(sheet_instances (path "/" (page "1")))',')'];(OUT/'dac_packet_video.kicad_sch').write_text('\n'.join(lines)+'\n')
    with (OUT/'pinmap.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    return rows
