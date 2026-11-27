def symbol(kind,spec):
    if kind in ('R','C'):
        result,loc=common.symbol(kind,spec);return result.replace('NET32:','NET35:'),loc
    count=len(spec['pins']);left=(count+1)//2;loc={}
    for i in range(1,count+1):
        isleft=i<=left;row=i-1 if isleft else count-i
        loc[str(i)]=(-17.78 if isleft else 17.78,((left-1)/2-row)*2.54,0 if isleft else 180)
    text=f'(symbol "NET35:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 16 0) (effects (font (size 1 1)))) (property "Value" "{kind}" (at 0 13 0) (effects (font (size 1 1)))) (property "Datasheet" {json.dumps(spec["datasheet"])} (at 0 0 0) (effects (font (size 1 1)) hide)) (symbol "{kind}_0_1" (rectangle (start -12.7 8.89) (end 12.7 -8.89) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "{kind}_1_1" '
    for pin,s in spec['pins'].items():
        x,y,angle=loc[pin]
        text+=f'(pin {s["type"]} line (at {x:.3f} {y:.3f} {angle}) (length 5.08) (name "{s["name"]}" (effects (font (size 1 1)))) (number "{pin}" (effects (font (size 1 1)))))'
    return text+'))',loc
