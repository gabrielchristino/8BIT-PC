def emit(defs,parts):
    # Reuse the tested complete-package emitter in a separate environment.
    env=dict(common.__dict__);env.update(OUT=OUT,VERIFY=VERIFY,NAME=NAME,BASE=BASE,uid=uid,symbol=symbol)
    source=inspect.getsource(common.emit).replace('NET32','NET35')
    source=source.replace('dac_packages.kicad_sym','sync_packages.kicad_sym')
    source=source.replace('ISA-1 DAC experiment - interface protection pending','ISA-1 supervised 3.51V sync window - experimental')
    source=source.replace('DIAGNOSTIC RSET - UNCALIBRATED WHITE - NOT FOR PRODUCTION','VGA PROTECTION / POWER TRANSIENTS / PCB UNQUALIFIED')
    exec(source,env);env['emit'](defs,parts)
    (VERIFY/'adapted-emitter.py').write_text(source)
    save(OUT/'design.json',{'date':'2026-11-27','base_git_commit':BASE,'status':'standalone candidate, no connector/ESD or analog POR qualification','parts':parts})
