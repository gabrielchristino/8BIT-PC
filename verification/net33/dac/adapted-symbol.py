def symbol(kind,spec):
    loc={}
    if kind=='AD9760ARUZ':
        for n in range(1,29):
            left=n<=14;row=n-1 if left else 28-n
            loc[str(n)]=(-17.78 if left else 17.78,(6.5-row)*2.54,0 if left else 180)
        body='(rectangle (start -12.7 19.05) (end 12.7 -19.05) (stroke (width 0.254) (type default)) (fill (type background)))'
    else:
        loc={'1':(-5.08,0,0),'2':(5.08,0,180)}
        body=('(rectangle (start -2.54 1.27) (end 2.54 -1.27) (stroke (width 0.254) (type default)) (fill (type none)))' if kind=='R' else
              '(polyline (pts (xy -1 2) (xy -1 -2)) (stroke (width 0.35) (type default)) (fill (type none))) (polyline (pts (xy 1 2) (xy 1 -2)) (stroke (width 0.35) (type default)) (fill (type none)))')
    ref='U' if kind=='AD9760ARUZ' else kind
    text=f'(symbol "NET33:{kind}" (pin_names (offset 0.508)) (in_bom yes) (on_board yes) (property "Reference" "{ref}" (at 0 25 0) (effects (font (size 1 1)))) (property "Value" "{kind}" (at 0 22 0) (effects (font (size 1 1)))) (property "Datasheet" {json.dumps(spec["datasheet"])} (at 0 0 0) (effects (font (size 1 1)) hide)) (symbol "{kind}_0_1" {body}) (symbol "{kind}_1_1" '
    for pin,s in spec['pins'].items():
        x,y,angle=loc[pin]
        text+=f'(pin {s["type"]} line (at {x:.3f} {y:.3f} {angle}) (length {5.08 if ref=="U" else 2.54}) (name "{s["name"]}" (effects (font (size 1 1)))) (number "{pin}" (effects (font (size 1 1)))))'
    return text+'))',loc
