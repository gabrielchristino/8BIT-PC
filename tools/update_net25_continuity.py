"""Document experiment and reproducible remaining failures, not a promoted fix."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    assert len(json.loads((ROOT/'verification/net25/local-sync-hypothesis.json').read_text())['cases'])==156
    p=json.loads((ROOT/'verification/net25/program/system-program-ideal.json').read_text())
    assert not p['failures'] and p['runs'][0]['passed'] and p['runs'][0]['frame_matches_reference']
    timed=[]
    for suffix in ['timed','early-timed']:
        r=json.loads((ROOT/f'verification/net25/vectors/verified-cpu-{suffix}-quick.json').read_text())
        assert not r['failures'] and r['runs'][0]['passed'];timed.append(r)
    doc=ROOT/'docs/engineering/NET25.md'
    old='Relatórios de vetores temporizados e novo boot/quadro são incluídos somente\nquando concluídos; não atribuir resultados da NET24 a esta variante.'
    new='''Os dois cenários temporizados concluíram1.062 instruções/1.821 transações
cada, sem falhas; atrasos padrão e antecipado do controlador. Setup observado
54,888/36,944/46,944ns no cenário padrão. As contagens warm de aberturas são
eventos da projeção binária, não aprovações analógicas.

O novo boot/quadro ideal concluiu132.197 instruções/232.576 transações e
76.800pixels idênticos à referência, SRAM inicialmente desconhecida e
FIXTURE_DEFAULTS=0. Períodos/startup são escalados explicitamente nessa
regressão lógica. Programa inteiro temporizado não foi executado.
Esses resultados pertencem à variante experimental, não à hipóteseP1.'''
    text=doc.read_text();assert old in text;doc.write_text(text.replace(old,new))
    notes={
      'README.md':'Investigação NET-25 (26/11/2026): drenagem síncrona passou32 cortes selecionados e6.886 vetores ideais, mas a variante NÃO foi promovida: partida binária arbitrária ainda rejeita pulso7,722ns/20ns sob CLR0; um reset breve50ns rejeita recovery em U36_1. Uma hipótese somenteHDL com dupla local emP1 passou156 cenários funcionais, conservando clock frio como restrição aberta. Ver [evidências e próximos ensaios](docs/engineering/NET25.md). Placa não liberada.',
      'ROADMAP.md':'NET-25: manter variante experimental sem promoção. Fechar recovery em reset breve e clock frio com monitores estritos; hipótese de dupla local emP1 passou156 projeções funcionais, ainda sem esquema próprio. Estudo de distribuição Q/QB e um buffer por ramo em CLOCK_TREE_STUDY.md requer pinagem/BOM/temporização e regressões. Depois seguir energia/consumo, DAC, firmware, união/ERC/footprints/PCB/DRC e protótipo.',
      'docs/engineering/VALIDATION_STATUS.md':'NET-25:32 cortes selecionados passam na drenagem, mas há falhas abertas de partida sob CLR0 e recovery de reset breve50ns/offset39ns. Não considerar o experimento uma correção global aprovada. Projeção diagnóstica só observa contenção durante reset conhecido; OPEN_RESET_CLOCK permanece não qualificado. Hipótese localP1 passou156 cenários funcionais e ainda não tem esquema próprio. Resultados completos e escopos em NET25.md.',
      'docs/engineering/PRODUCTION_GATES.md':'NET-25 NÃO fecha gate temporal: pulso frio7,722ns<20ns sob CLR0 e recovery de reset breve permanecem rejeições. A hipótese localP1 e a projeção diagnóstica de contenção não são aprovações do esquema. Exigir variante por pinos, guardas estritas, cargas/skew/jitter/PVT, POR/MTBF e todas as verificações físicas antes de fabricação.',
      'AGENTS.md':'## Continuidade NET-25\n\n- Leia docs/engineering/NET25.md. Variante experimental hardware/phase_drain_video/reset não foi promovida. Vídeo36CIs; reset7digitais+1supervisor+2osciladores. Warm U8 AHC164/Q3, clearRC independente, U9 serial condicionado, armamento sticky dos bancos.\n-32 cortes selecionados passam, mas cold pattern4 produz7,722ns sob CLR0 no monitor estrito e RAW50ns/offset39 rejeita recovery em U36_1. Preservar ambas falhas, não transformar coleta em aprovação.\n- package_models_cold_diagnostic só registra CLK curto quando CLR conhecido0; CLR alto/indefinido continua fatal. OPEN_RESET_CLOCK continua restrição não qualificada, mesmo que contenção funcional passe. Não usar esse modelo para aprovar clock ativo ou fabricação.\n- local_sync_hypothesis é SOMENTEHDL com pacote extra AHC74 emP1;156 casos funcionais passaram, ainda incluindo clock frio aberto e sem esquema próprio. CLOCK_TREE_STUDY é proposta não implementada. Não atribuir resultados NET25 à próxima variante.\n- Modelo warm tem default estrito calibrado e fronteiras binárias separadas de dados/clear; não é transistor/MTBF nem limite real de duração de metastabilidade. Hold observado captura a escolha binária antiga; duas políticas não esgotam todas resoluções analógicas.\n- Não alterar fontes/scripts listados enquanto trabalhos estiverem ativos. Registros intermediários de calibração/counters/metadados/partida ficam preservados em development; só rodadas finais com fontes congeladas são regressões aceitas.\n\n',
    }
    for name,note in notes.items():
        p=ROOT/name;text=p.read_text(encoding='utf-8');assert not text.startswith(note)
        p.write_text(note+'\n\n'+text,encoding='utf-8')
    entries={
      'DECISIONS.md':'''\n\n## ADR E30 — Drenagem síncrona experimental, ainda sem promoção\n\n26/11/2026. Base5a871ff3ddc58986ae1fb7998690bb9ec3711d5b. Status: experimento com falhas abertas.\n\nTrocar U8 vídeo AHC74 por AHC164 de quatro estágios, clear RC independente, condicionar serial do shift de fases e armar bancos por READY|BANK_SYNC1. Mantém36CIs de vídeo e não mexe em CPU/ISA/SP/ROMs. Alternativas: apagar fases assincronamente (reproduz runt ativo), aumentar duty (backend já50%), relaxar guardas ativas (rejeitado), sincronizar reset local em fase distante e reduzir distribuição de clocks (próximas hipóteses).\n\nEvidência:32 cortes selecionados passam, mas padrão frio4 rejeita7,722ns/20ns sob CLR0. RAW50ns/offset39 rejeita recovery em U36_1. Projeção cold diagnóstica permite observar apenas contenção conhecida sob CLR0 e conserva restrição aberta. Hipótese de pacote AHC74 extra local emP1 passou156 casos funcionais com essa mesma restrição fria; não tem esquema próprio e não substitui a variante nativa.\n\nImpacto: fronteira warm de dados/clear passa a ter hipótese binária explícita; não é MTBF/POR qualificado. Futuro pacote local aumentaria vídeo para37CIs. Aceitar somente após esquema real, XML/cargas/guardas estritas, glitches/pausas/partidas, pinos SRAM/CPU/teclado, quadros/boot e orçamento completo. Não promover o experimento pelo sucesso nominal. Ver NET25.md e CLOCK_TREE_STUDY.md.\n''',
      'PROVENANCE.md':'''\n\nNET-25 experimental,26/11/2026, base5a871ff3ddc58986ae1fb7998690bb9ec3711d5b: novas variantes separadas partem dos JSON nativos NET22/NET23, sem executar builders históricos. KiCad10/XML conferem todos os pinos. sim/net25 distingue modelos estritos, projeção binária warm, diagnóstico de CLK sob CLR0 e hipótese apenasHDL com duplaP1. Falhas reais do experimento e defeitos de preparação dos ensaios permanecem em verification/net25/development. Não são originais recuperados nem aprovação de produção. Manifesto inclui hashes, ferramentas, saídas e auditoria dos snapshots Git anteriores. Pesquisa de famílias/latch em CLOCK_TREE_STUDY cita fontes primárias e não foi adotada.\n''',
      'CHANGELOG.md':'''\n\n## 2026-11-26 — NET-25 experimental\n\n- Novas folhas de drenagem/armamento e modelo warm calibrado;32 cortes selecionados e vetores ideais passam.\n- Preservadas falhas de clock frio sob CLR0 e recovery de reset breve. Variante não promovida.\n- Hipótese apenasHDL de reset local emP1 passa156 cenários funcionais; clock frio continua aberto. Estudos de próxima variante não contam como implementação.\n'''}
    for name,entry in entries.items():
        p=ROOT/name;p.write_text(p.read_text(encoding='utf-8')+entry,encoding='utf-8')
    p=ROOT/'AGENTS.md'
    note='- Hipótese combinada somenteHDL (dupla localP1 com buffer e controlador diretoBACKEND) passou156 casos com monitor estrito original e dois negativos; não instancia teclado/SRAM/CPU. Teclado U1HC174 recebe CLK BUF_1_0, IO_COMMIT é autorização de dados. Opção seguinte considera U1AHC174 real + controlador sem dois buffers intermediários, um pacote local extra; não confundir com esquema construído ou aprovação global.\n'
    text=p.read_text();text=text.replace('## Continuidade NET-25\n\n','## Continuidade NET-25\n\n'+note,1);p.write_text(text)
    p=ROOT/'.gitattributes';p.write_text(p.read_text()+'\n/verification/net25/**/*.sv -whitespace\n/verification/net25/**/*.log -whitespace\n')

if __name__=='__main__':main()
