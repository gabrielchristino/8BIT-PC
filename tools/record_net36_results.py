"""Validate and record NET36 evidence without changing frozen simulation inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/net36'
BASE='2a7fbab2a34c678e15bdde94d1073e52818125d4'


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def prepend(name,text):
    path=ROOT/name
    old=path.read_text()
    if not old.startswith(text):
        path.write_text(text+'\n\n'+old)


def main():
    audit=json.loads((OUT/'full-timed-audit-final.json').read_text())
    net27,net30=audit['attempts']
    assert net27['simulation_accepted'] and not net27['errors']
    assert net30['classification']=='running' and not net30['errors']
    assert net30['identity']['matches_recorded_identity'] and not net30['simulation_accepted']
    assert len(net27['report_sources'])==49 and all(r['resolution'] for r in net27['report_sources'])
    assert all(r['matches'] for row in audit['attempts'] for r in row['source_checks'])
    assert len(net27['acceptance_negatives'])==6 and all(r['rejected'] for r in net27['acceptance_negatives'])
    assert all(r['identical'] for r in audit['regenerated_input_comparisons'])
    # Reverse later additions, accepting only an exact match to the source
    # hash recorded by the first audit. This is an identified reconstruction.
    initial_audit=json.loads((OUT/'full-timed-audit.json').read_text())
    initial_source=(ROOT/'tools/audit_full_timed_attempts.py').read_text()
    begin=initial_source.index("    bench = (attempt/'compiler-inputs/generated-bench.sv').read_text()")
    end=initial_source.index('    identity = process_identity(state)',begin)
    initial_source=initial_source[:begin]+initial_source[end:]
    begin=initial_source.index("        if identity['matches_recorded_identity']:")
    end=initial_source.index('        return result',begin)
    initial_source=initial_source[:begin]+initial_source[end:]
    assert hashlib.sha256(initial_source.encode()).hexdigest()==initial_audit['auditor_sha256']
    development=OUT/'development'
    development.mkdir(exist_ok=True)
    (development/'auditor-initial-reconstructed.py').write_text(initial_source)
    save(development/'source-reconstruction.json',dict(transformation='Reverse two bench/resource-limit additions; reconstructed source, not contemporaneous capture.',
        source='tools/audit_full_timed_attempts.py',result='verification/net36/development/auditor-initial-reconstructed.py',
        matches_original_report_sha256=initial_audit['auditor_sha256']))
    power=json.loads((OUT/'hold-up-review.json').read_text())
    assert not power['failures'] and len(power['sweep'])==120 and len(power['passive_proxies'])==5
    assert all(p['classified_as_expected'] for p in power['passive_proxies'])
    assert not power['hardware_changed'] and not power['physical_power_qualified']
    assert power['proposed_requirement']['at_disable_v']>3.005
    for record in power['sources']:
        assert hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()==record['sha256']
    assert not git('diff','--name-only',BASE,'--','hardware','sim','firmware','archive','revisions')
    review=dict(date='2026-11-27',classification='Manual engineering paraphrase of primary web reading; not original local PDF bytes',
        primary_sources=[dict(url='https://www.analog.com/media/en/technical-documentation/data-sheets/lt3042.pdf',revision='C',
            pages=[19,22],facts=['Overshoot recovery discharges output when OUTS exceeds SET; about4mA is typical.',
                'Protection application text describes up to15mA recovery sink during output-held/input-collapse conditions and a SET-resistor path.',
                'Reverse input blocking does not eliminate output-to-ground discharge. Activation depends on SET/VIN dynamics.']),
            dict(url='https://www.ti.com/lit/ds/symlink/tps3808.pdf',revision='SBVS050N',pages=[6,7],
                local_path='references/net20/tps3808.pdf',facts=['Timing conditions include100k RESET pullup and50pF; NET35 uses4.7k.',
                    'Qualification of20.1us total inhibition remains open; POR also has supply-ramp and load conditions.'])],
        additional_candidates_examined=[
            dict(url='https://industrial.panasonic.com/ww/products/pt/OS-CON/models/6SEPC220M',decision='Not adopted; official page labels NRFND.'),
            dict(url='https://industrial.panasonic.com/ww/products/pt/os-con/models/6SVPC220M',decision='Not adopted; nominal220uF/27milliohm listing does not establish150uF/50milliohm over all required conditions.')],
        original_local_lt3042_pdf=False,new_hardware_or_bom_adopted=False)
    save(ROOT/'references/net36/review.json',review)
    doc='''# NET36 — auditoria do boot temporizado e revisão da reserva H/V

27/11/2026. Base `2a7fbab2a34c678e15bdde94d1073e52818125d4`.
**NET27 aceita no escopo digital NET26; NET30 ainda ativa na coleta.
Nenhum circuito novo adotado ou projeto liberado para fabricação.**

## Resultado das execuções completas

`tools/audit_full_timed_attempts.py` só lê as tentativas e regenera a referência
em diretório temporário Linux. Não inicia simulador, altera entradas ou retoma
processo. A primeira coleta e a coleta final permanecem separadas em
`verification/net36/full-timed-audit*.json`, com identidade, limites e hashes.

NET27 `attempt-001` terminou com saída zero em 56.155,678 s de parede,
sem timeout: 132.197 instruções, 232.576 transações, 32.771 transações VRAM,
258.492 verificações WAIT e 17.395 observações de pausa. Foram 337 escritas
RAM e 32.770 escritas VRAM válidas, zero abortos e FIXTURE_DEFAULTS=0.
O quadro PPM tem 230.415 bytes e 76.800 pixels, exatamente iguais à referência
regenerada, SHA256 `152c217f59e4a6f05b8c75f8c17e66c1b4e01b5369e37b913f034e97d6903665`.

A bancada compara cada retirada e transação, todos os 32.768 bytes de VRAM,
um sentinela RAM, pixels e geometria. Não há dump exaustivo final da RAM.
Há 49 conferências de runners/snapshots/fontes congeladas por tentativa e
49 fontes do relatório final NET27 resolvidas. As três imagens de entrada
(estados, barramento, ROM) de cada tentativa coincidem com a regeneração.
Seis negativos adulteram contagem, pixel, aborto, término, aprovação e timeout;
todos são rejeitados. Nada foi alterado nas evidências para esses negativos.

CPU nominal 100 kHz, master nominal 25,175 MHz (meio período19,860973 ns),
startup10 ms e atrasos digitais selecionados. A impressão `video_half=20` é
arredondada; o auditor confere o parâmetro fonte. RESET_BOUNDARY registra zero
eventos warm nesta execução, mantendo hipótese binária explícita e nenhuma
aprovação de metastabilidade/MTBF/PVT/POR analógico. NET27 usa NET26: não
transferir este sucesso à redistribuição de cargas NET30 nem às NET33–35.

NET30 permanece no mesmo boot WSL/PID1656, comando e cwd esperados. Limites
reais do processo conferidos:1GiB,72000sCPU,8MiB/arquivo,sem core; watchdog
do executor24h. As entradas congeladas conferem. Não há RESULT, relatório
final ou comparação final de imagem nessa coleta; não está aprovada.
O progresso exato e a data UTC estão nos checkpoints, não são conclusão.

## Descarga H/V: hipótese que precisa ser revista

LT3042 Rev.C p19 descreve recuperação de sobretensão; p22 descreve até15mA
de drenagem nessa função, além do caminho pelo SET. Bloqueio reverso de IN
não elimina descarga para terra. Cerca de4mA é típico, não máximo. A ativação
depende de OUTS/SET/VIN: a soma a seguir é estresse condicional, não simulação
do comportamento real nem prova de que todos os caminhos conduzem juntos.

O ledger parcial de resistores/carga, com3,6V e sem queda favorável no driver,
chega a5,714481mA em estado ativo. Somando15mA e o caminho resistivo SET,
o estresse parcial chega a20,817148mA, antes de ICC/DeltaICC, comutação,
fugas e transientes. Não é máximo global garantido. No proxy47uF/50mohm/
20,1us, sobra somente0,890826mV acima3V. O orçamento10mA NET35 permanece
uma hipótese não demonstrada; não declarar defeito físico por essa soma.

O novo cálculo racional reproduz exatamente3,006057740V da NET35 sob10mA.
Para os mesmos47uF/50mohm/20,1us, a fronteira matemática é22,682129mA
para alcançar3V, sem margem. O caso25mA já cai abaixo3V.
Uma **proposta de requisito**, ainda sem peça/BOM ou esquema novo, é
25mA totais,150uF efetivos mínimos,50mohm máximos e20,1us máximos:
resulta3,006234336V. Para margem5mV seriam necessários109,612385uF nesse
mesmo modelo.150uF é reserva adicional, não capacitância nominal adotada.

Foram classificadas120 combinações C/I/t/ESR e cinco proxies ngspice:
três acima3V e dois abaixo, incluindo negativo25mA/47uF. Todos coincidem
com a equação de carga dentro da tolerância numérica. Proxies não contêm
modelos vendor do regulador ou supervisor. O caso150uF/25mA/50us fica
acima3V, mas não atende margem5mV; não confundir critérios.

## Critérios para a próxima revisão

Qualificar o tempo SENSE→RESET com pullup4,7k e carga real (tabelaTPS3808
usa100k/50pF), NAND/buffer e rampa; não herdar20,1us como garantia.
Fechar corrente integrada de descarga e dinâmica SET/OUTS em falha de IN,
passivos reais/temperatura/bias/frequência/envelhecimento/ESR/ESL e estabilidade
com o bulk. Avaliar isolamento da reserva ou outra arquitetura se necessário.
Maior bulk não resolve a margem superior4,2198mV, retomada, overshoot,
curto/clamp abrupto, receptor/proteção, partida ou POR.

6SEPC220M foi descartado nesta pesquisa por indicação NRFND;6SVPC220M
permanece apenas pesquisa: valores nominais não qualificam os requisitos.
Novo download LT3042 terminou em timeout; registro emreferences/net36,
sem PDF inventado. Leitura web primária, revisão/páginas e fontes locais
reutilizadas estão identificadas. Falhas/limitações da NET35 preservadas.

## Reprodução e continuidade

```
timeout120 python3 tools/audit_full_timed_attempts.py --output verification/net36/full-timed-audit-final.json
timeout180 python3 tools/check_sync_hold_up_review.py
python3 tools/record_net36_results.py
```

Nos comandos acima, usar espaço em `timeout 120` e `timeout 180`.
Python3.12.3/ngspice42 no UbuntuWSL; proxies limitados a256MiB/10sCPU/
20swall/2MiB por arquivo, cinco execuções. Icarus12.0 é a ferramenta do
resultado NET27 já encerrado. Nenhuma nova execução CPU/quadro foi feita
pela NET36. Fontes hardware/sim/firmware earchive/revisions não mudaram.
NET30 continua candidato digital460CIs+dois osciladores; energia global,
RGB/SLEEP/proteção, timing/CDC/cargas, firmware, esquema unido/ERC,
footprints/PCB/DRC e protótipo continuam abertos.

A primeira chamada verify_archive falhou por um cachePython preexistente de
26/11 emrev983, ausente dos ZIPs/Git. Seus6.124bytes/metadados foram
preservados emdevelopment, e somente esse artefato gerado foi retirado da
extração. A repetição passou159arquivos/55entradas ZIP. Fontes originais
intactas; primeira falha e transformação emdevelopment/archive-first-failure.json
e cache-quarantine.json. verify_recovered não foi repetido nesta mudança:
a ausência histórica diagnostic.asm continua sendo falha conhecida.
'''
    # Literal commands remain directly runnable in the published document.
    doc=doc.replace('timeout120','timeout 120').replace('timeout180','timeout 180')
    doc=doc.replace('\nNos comandos acima, usar espaço em `timeout 120` e `timeout 180`.','')
    (ROOT/'docs/engineering/NET36_REVIEW.md').write_text(doc)
    note='NET36,27/11/2026: NET27 completo temporizado aceito no circuito NET26 (132.197instruções/232.576transações/32.771VRAM/76.800pixels idênticos); NET30 ainda ativa e não aprovada nesta coleta. Revisão H/V inclui caminhos LT3042 até15mA descritos no datasheet;10mA totais continuam não qualificados.120casos/five proxies condicionais, proposta25mA/150uF efetivos sem adoção de BOM. Ver docs/engineering/NET36_REVIEW.md; fabricação não liberada.'
    note=note.replace('/five proxies','/cinco proxies')
    for name in ['AGENTS.md','PROVENANCE.md','ROADMAP.md','CHANGELOG.md']:
        prepend(name,note)
    prepend('README.md','NET36 (27/11/2026): [boot temporizado auditado e revisão H/V](docs/engineering/NET36_REVIEW.md). NET27 passou no circuito NET26 com132.197instruções e76.800pixels exatos; NET30 continua ativa nesta coleta. Caminhos internos do LT3042 exigem rever a hipótese10mA. Novo requisito25mA/150uF é apenas proposta condicional, sem alteração de hardware ou liberação física. Registros anteriores abaixo preservam seus checkpoints; o estado corrente é o desta atualização e de VALIDATION_STATUS.')
    prepend('docs/LACUNAS.md','NET36,27/11/2026: boot completo temporizado NET27/NET26 agora auditado e aceito; NET30 permanece pendente. Corrente de descarga LT3042/SET, timing real TPS3808 a4,7k e capacitância efetiva/ESR continuam sem qualificação. Proposta25mA/150uF não é BOM. Novo download LT3042 também terminou em timeout; sem PDF local. Ver engineering/NET36_REVIEW.md.')
    prepend('docs/engineering/NET27_PLAN.md','Atualização27/11/2026: tentativa001 concluída e auditada independentemente; programa completo temporizado NET26 aceito nas condições selecionadas.132.197instruções/232.576transações/32.771VRAM/76.800pixels exatos, zero abortos. Evidências em verification/net27/full-timed/attempt-001 e verification/net36; detalhes emNET36_REVIEW.md. O plano original abaixo registra a preparação, não o estado final. NET30 continua separada/pendente; sem liberação física.')
    prepend('docs/engineering/VALIDATION_STATUS.md','''## Atualização NET36 — 27/11/2026

NET27 `attempt-001` concluída e aceita pela auditoria independente:132.197
instruções/232.576transações/32.771VRAM,76.800pixels idênticos,zero abortos.
49fontes do relatório final e entradas congeladas conferidas; referência
regenerada,seis negativos rejeitados. É circuitoNET26, sem herança paraNET30.
NET30 permanece ativa/pendente no checkpoint; identidade e limites conferidos.

NET35 permanece experimental: limite10mA total não qualificado frente aos
caminhos internos LT3042; estresse parcial20,817mA deixa0,891mV no proxy47uF.
Proposta25mA/150uF efetivos/50mohm/20,1us resulta3,006234V condicionalmente;
nenhuma peça/BOM/esquema adotada.120combinações e cinco proxies conferidos.
TimingTPS3808 em4,7k,passivos reais,estabilidade/POR/transientes ainda abertos.
**Fabricação não liberada.** [Evidências e critérios NET36](NET36_REVIEW.md).
Os estados anteriores abaixo conservam o escopo das respectivas etapas.''')
    prepend('DECISIONS.md','''## ADR E40 — Rever a reserva H/V antes de promover NET35

27/11/2026,base2a7fbab. Estado: requisito proposto em investigação,sem
adoção de BOM ou mudança de circuito. LT3042RevC descreve caminhos de
descarga OUTS/SET/recuperação até15mA em condições de falha; bloqueio
reverso deIN não qualifica10mA totais. Ledger parcial com essa hipótese
chega20,817mA e margem0,891mV no proxy47uF,sem provar simultaneidade real.

Decisão: conservar NET35 e testar separadamente requisitos25mA totais,
150uF efetivos,ESR50mohm e inibição20,1us.120combinações e cinco proxies
conferidos; caso25mA/47uF é negativo,150uF/25mA resulta3,006234V.
Alternativas: qualificar10mA com todos os caminhos,isolação da reserva,
outro regulador/supervisor ou arquitetura H/V; maior capacitor sozinho
não fecha transientes/POR e não é adoção automática de nominal220uF.

Compatibilidade: CPU/ISA/X/SP/flags/VGA/WAIT/COMMIT e todas as fontes
NET27/NET30 preservadas. Nenhuma integração ou economia deCI alegada.
Aceitação: corrente integrada/dinâmica SET reais,tempoTPS3808 na carga
4,7k real,passivos completos/deriva/ESR/ESL,estabilidade/Kelvin/térmica,
partida/receptor/proteção e margens superior/retomada antes de promover.
Resultado NET27 aceito pertence àNET26;NET30 segue pendente no checkpoint.
Detalhes em docs/engineering/NET36_REVIEW.md.''')
    attributes='''# Preserve exact completed NET27 compiler/image/log evidence and NET36 proxy tables.
/verification/net27/full-timed/** -text -whitespace
/verification/net36/**/values.dat -text -whitespace
/references/net36/** -text -whitespace'''
    path=ROOT/'.gitattributes'
    if attributes not in path.read_text():
        path.write_text(path.read_text()+'\n'+attributes+'\n')
    # Run archive integrity, preserve its previous report byte-for-byte and
    # retain this invocation's report/output separately. Historical sources
    # are never executed here or changed.
    integrity=ROOT/'verification/integrity.json'
    before=integrity.read_bytes() if integrity.exists() else None
    try:
        run=subprocess.run([sys.executable,'scripts/verify_archive.py'],cwd=ROOT,capture_output=True,text=True,timeout=120)
        first_report=json.loads(integrity.read_text())
        extra="Unexpected/missing extracted files in rev983: ['__pycache__/keyboard.cpython-312.pyc']"
        if run.returncode!=0 and first_report['failures']==[extra]:
            save(development/'archive-first-failure.json',dict(command=[sys.executable,'scripts/verify_archive.py'],
                exit=run.returncode,stdout=run.stdout,stderr=run.stderr,report=first_report))
            cache=ROOT/'revisions/rev983/__pycache__/keyboard.cpython-312.pyc'
            assert cache.resolve().is_relative_to((ROOT/'revisions/rev983').resolve()) and not cache.is_symlink()
            assert not git('ls-files','--',cache.relative_to(ROOT).as_posix())
            # The artifact is not an original package entry. Preserve its
            # bytes/metadata before removing only this generated extra file.
            for package in (ROOT/'archive/packages').glob('*.zip'):
                with zipfile.ZipFile(package) as bundle:
                    assert '__pycache__/keyboard.cpython-312.pyc' not in bundle.namelist()
            data=cache.read_bytes()
            stat=cache.stat()
            evidence=development/'keyboard.cpython-312.pyc.evidence'
            evidence.write_bytes(data)
            save(development/'cache-quarantine.json',dict(original_path=cache.relative_to(ROOT).as_posix(),
                preserved_path=evidence.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),
                bytes=len(data),mtime_unix=stat.st_mtime,ctime_unix=stat.st_ctime,
                classification='Pre-existing generated bytecode absent from original ZIP entries and Git; original source files untouched.'))
            assert evidence.read_bytes()==data
            cache.unlink()
            run=subprocess.run([sys.executable,'scripts/verify_archive.py'],cwd=ROOT,capture_output=True,text=True,timeout=120)
        save(OUT/'archive-integrity-execution.json',dict(command=[sys.executable,'scripts/verify_archive.py'],exit=run.returncode,
             stdout=run.stdout,stderr=run.stderr,source_sha256=hashlib.sha256((ROOT/'scripts/verify_archive.py').read_bytes()).hexdigest()))
        (OUT/'archive-integrity.json').write_bytes(integrity.read_bytes())
        assert run.returncode==0 and not json.loads(integrity.read_text())['failures']
    finally:
        if before is not None:
            integrity.write_bytes(before)
    # Capture the currently fetched remote tree before publication; live
    # remote SHA is checked again in the separate publishing command.
    tree=git('ls-tree','-r','origin/main')
    save(OUT/'prepublish-remote-tree.json',dict(ref='origin/main',commit=git('rev-parse','origin/main').decode().strip(),
         tree_sha256=hashlib.sha256(tree).hexdigest(),entries=len(tree.splitlines()),
         hardware_sim_archive_unchanged=not bool(git('diff','--name-only',BASE,'--','hardware','sim','firmware','archive','revisions'))))
    names=['.gitattributes','README.md','AGENTS.md','PROVENANCE.md','ROADMAP.md','DECISIONS.md','CHANGELOG.md',
        'docs/LACUNAS.md','docs/engineering/VALIDATION_STATUS.md','docs/engineering/NET27_PLAN.md','docs/engineering/NET36_REVIEW.md',
        'tools/audit_full_timed_attempts.py','tools/check_sync_hold_up_review.py','tools/record_net36_results.py',
        'tools/publish_net36_review.py']
    for folder in ['verification/net27/full-timed/attempt-001','verification/net36','references/net36']:
        names += [p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file()
                  and p.name!='manifest.json' and '__pycache__' not in p.parts]
    manifest=dict(date='2026-11-27',base_commit=BASE,net27_accepted=True,net30_accepted=False,
        net30_status='running-at-audit-checkpoint',physical_power_qualified=False,production_released=False,
        historical_assembler_missing_diagnostic='Known failure unchanged; verify_recovered.py not rerun for this read-only/source-review change.',
        commands=['timeout 120 python3 tools/audit_full_timed_attempts.py --output verification/net36/full-timed-audit-final.json',
            'timeout 180 python3 tools/check_sync_hold_up_review.py','python3 tools/record_net36_results.py'],
        excluded_active_prefix='verification/net30/full-timed/',
        files=[dict(path=n,bytes=(ROOT/n).stat().st_size,sha256=hashlib.sha256((ROOT/n).read_bytes()).hexdigest()) for n in sorted(set(names))])
    save(OUT/'manifest.json',manifest)
    print(json.dumps(dict(files=len(manifest['files']),net27_accepted=True,net30_accepted=False,
                         hold_up_cases=120,passive_proxies=5,physical_power_qualified=False)))


if __name__=='__main__':main()
