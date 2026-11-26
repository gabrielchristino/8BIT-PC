from itertools import product
T=1000/25.175
# Commands are at pins after a hypothetical independent 0..8 ns control delay.
# Write data pre-staged; CE held low; separate read capture register.
# VGA select/OE at 0, capture at 2T; CPU select at 2T+hold guard (3 ns),
# SRAM OE off at 2T+3; CPU driver on at 3T; WE low at 3T+20;
# WE high at 4T; driver off at 4T+3, next VGA OE delayed -> conflicts.
# Alternative: alternate pixels, full VGA read each even slot, reuse vertical? Not valid.
# Candidate eight phase schedule, pin commands, not clock implementation.
def margins(p,delay,guard,ram):
    # VGA OE/addr at 0, capture 3p, OE off 4p, CPU select 4p,
    # writer on 5p, WE on 6p, WE off 7p, writer off 8p,
    # next VGA OE at next 1p, address select at next 0p.
    # actual control event uncertainty 0..delay; capture uncertainty same.
    aa,oe,hz,wp,dw,aw=ram
    return {'VGA setup':3*p-delay-max(11.5+aa,p+oe)-2.5-guard,
      'VGA hold':p-delay-1-guard,
      'SRAM to CPU':p-delay-hz-guard,
      'write address setup':2*p-delay-11.5-guard,
      'write pulse':p-delay-wp-guard,
      'write data setup':2*p-delay-16-dw-guard,
      'write hold':p-delay-guard,
      'CPU to SRAM':p-delay-16.5-guard,
      'CPU read setup':3*p-delay-max(11.5+aa,p+oe)-2.5-guard}
ramlist={10:(10,5,3,7,5,8),12:(12,6,3,8,6,8),15:(15,7,4,9,8,10),20:(20,8,5,12,10,12)}
for speed,ram in ramlist.items():
    vals=margins(T/2,8,2,ram)
    print(speed, {k:round(v,3) for k,v in vals.items()})
count=passed=0
for speed,delay,guard,duty in product(ramlist,[0,2,4,8,12],[0,2,4],[.45,.5,.55]):
    p=T*min(duty,1-duty)
    m=margins(p,delay,guard,ramlist[speed]);count+=1;passed+=min(m.values())>=0
print('sensitivity cases',count,'pass',passed)
# fallback: CPU in blanking plus horizontal active interleaving only if proven.
# DAC static sensitivity, independent output voltage bounds, no nonlinear model
for rs in ([3240,1620,806],[1380,698]):
    den=1/75+sum(1/r for r in rs)
    for vh,vl in [(5,0),(3.8,.44),(3.76,.44),(5.5,0)]:
        print('DAC',len(rs),vh,vl, 'black',round(sum(vl/r for r in rs)/den,5),'white',round(sum(vh/r for r in rs)/den,5))
    max_i=max((5-(sum(5/r for i,r in enumerate(rs) if code>>i&1)/den))/r for code in range(1,1<<len(rs)) for i,r in enumerate(rs) if code>>i&1)
    print('max nominal pin mA',max_i*1000)
