def package_symbol(kind,spec):
    if kind not in ('AS7C256A_28SOJ','AT28C256_28PDIP','R'):return tuple(v.replace('NET02:','NET30B:') if isinstance(v,str) else v for v in old_symbol(kind,spec))
    loc={}
    if kind=='R':
        loc={'1':(0,3.81,270),'2':(0,-3.81,90)};body='(rectangle (start -1.27 2.54) (end 1.27 -2.54) (stroke (width 0.254) (type default)) (fill (type none)))';ref='R'
    else:
        for typ,x,angle in [('input',-17.78,0),('bidirectional',17.78,180)]:
            rows=[(p,s) for p,s in spec['pins'].items() if s['type']==typ]
            for i,(p,s) in enumerate(rows):loc[p]=(x,(len(rows)-1)*1.27-i*2.54,angle)
        loc['28']=(0,27.94,270);loc['14']=(0,-27.94,90);ref='U';body='(rectangle (start -12.7 25.4) (end 12.7 -25.4) (stroke (width 0.254) (type default)) (fill (type background)))'
    text=f'(symbol "NET30B:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "{ref}" (at 0 34 0) (effects (font (size 1 1)))) (property "Value" "{kind}" (at 0 32 0) (effects (font (size 1 1)))) (property "Datasheet" {json.dumps(spec["datasheet"])} (at 0 0 0) (effects (font (size 1 1)) hide)) (symbol "{kind}_0_1" {body}) (symbol "{kind}_1_1" '
    for p,s in spec['pins'].items():
        x,y,angle=loc[p];text+=f'(pin {s["type"]} line (at {x} {y} {angle}) (length {2.54 if kind=="R" else 5.08}) (name "{s["name"]}" (effects (font (size 1 1)))) (number "{p}" (effects (font (size 1 1)))))'
    return text+'))',loc
