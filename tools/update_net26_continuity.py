"""Publish evidence-scoped continuity only after completed NET26 regressions."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'verification/net26'
    for name,count,key in [('local-phase-probe.json',156,'cases'),('local-phase-matrix.json',128,'cases'),('local-phase-negative.json',3,'runs')]:
        d=json.loads((out/name).read_text());assert not d['failures'] and len(d[key])==count and all(x['passed'] for x in d[key])
    d=json.loads((out/'program/system-program-ideal.json').read_text());assert not d['failures'] and d['runs'][0]['frame_matches_reference']
    updates={
      'README.md':'NET-26 (26/11/2026): reset local emP1, controlador com uma etapa de buffer e AHC174 real no teclado. Passaram156 cenários estritos,128 combinações selecionadas,48 cortes SRAM, oito cortes CPU,6.886 vetores ideais/dois temporizados de1.062 e boot/quadro completo ideal. Candidato460CIs+2osciladores; energia/temporização global/PCB/protótipo continuam abertos. [Circuito, resultados e limites](docs/engineering/NET26.md). Placa não liberada.',
      'ROADMAP.md':'NET-26: correções nativas de clock/reset local e teclado passaram nos cenários selecionados. Próximo: boot inteiro temporizado com limites/progresso, orçamento global de timing/energia/consumo/POR, DAC/firmware; depois união/ERC/footprints/PCB/DRC e protótipo. Estudos NET25 não substituem os resultados NET26; CVC alternativo não foi adotado.',
      'docs/engineering/VALIDATION_STATUS.md':'NET-26:156 cenários estritos com teclado e128 combinações selecionadas passaram, com três reversões negativas;48 cortes SRAM e oito CPU.6.886 vetores ideais, dois1.062 temporizados e132.197 instruções/76.800pixels do boot ideal concluídos. Três folhas nativas têm ERC49/13/25 violações sem waivers. Não é temporização/elétrica/POR/MTBF global nem aprovação física. Ver NET26.md.',
      'docs/engineering/PRODUCTION_GATES.md':'NET-26 fecha somente as rejeições reproduzidas nos cenários selecionados, com circuito novo e guardas estritos. Conta22,72ns/7,72ns é condicional; jitter/trilhas/min-delay/slew/CDC/POR/energia/consumo/global e ensaios físicos continuam abertos. CVC é pesquisa rejeitada, não evidência de produção. Programa completo temporizado ainda pendente.',
      'AGENTS.md':'''## Continuidade NET-26

- Leia docs/engineering/NET26.md. Novas folhas local_phase_video/reset/keyboard; predecessores preservados. Vídeo37CIs, U37 AHC74 reset local clockP1 através de U24.3 ANDbuffer; warm U8 AHC164 e U9 clearVDD permanecem.
- Reset U8ch1 desabilitado; access_clk é alias BACKEND real, três buffers folha do controlador mais resetroot dão quatro cargas50pF condicionais. Teclado U1 AHC174 substitui HC174 sem redes alteradas; CLK continua BUF_1_0, IO_COMMIT autoriza mux de dados. Não relaxar monitor HC174 antigo.
-156cenários estritos/128combinações e três negativos passaram; sem exceção CLR0.48cortes SRAM WE<=94ns, oito CPU/scans WE<=84ns,6.886ideais/dois1.062temporizados e boot ideal132.197/76.800pixels passaram. Não atribuir provas a outro circuito. Setup observado54,888/16,944/26,944ns, não valores antigos.
- Limites de pulse22,72ns controlador/7,72ns teclado são condicionais, sem jitter/trilhas/PVT global. Warm e reset local têm projeções binárias explícitas, não MTBF/POR analógico aprovado. Modelo/ensaios de potências inválidas continuam com seu próprio escopo.
- União candidata460CIs(inclui memórias/supervisor)+2módulos ACH,464capacitores; consumo não fechado. ERC parcial49vídeo/13reset/25teclado sem waivers, não ERC global/PCB.
- CVC alternativo NÃO adotado: compilado crashou, interpretador só passou unidades, tentativa nativa não concluiu e a limitada esgotou768MB. Todos os resultados de engenharia são Icarus. Qualquer pesquisa/processo novo pesado deve ter limites próprios de memória/CPU/tempo/saída e identificação para parada; não repetir avaliação sem limites.
- Congelar fontes/geradores listados enquanto houver execução ativa. Próximo programa completo temporizado requer progresso, limite e retomada; ainda não foi executado. Não marcar produção antes de orçamento global/energia/DAC/firmware/união/ERC/PCB/DRC/protótipo. diagnostic.asm histórico continua ausente.

'''}
    for name,note in updates.items():
        p=ROOT/name;text=p.read_text();assert not text.startswith(note)
        p.write_text(note+'\n\n'+text)
    extras={
      'DECISIONS.md':'''\n\n## ADR E31 — Reset local emP1, clock direto e AHC174 no teclado\n\n26/11/2026. Base64d01218193259dfc3740f71b6af5ecbe154149e. Adotada como variante candidata após regressões selecionadas; sem liberação física.\n\nProblemas: NET25 tem pulso frio7,722ns/20ns e recovery em RAW50ns. Decisão: adicionar dupla AHC74 local emP1 pelo ANDbuffer livre, ligar controlador diretamente a BACKEND conservando uma etapa de folha e trocar U1 do teclado HC174→AHC174 real. Mantém função/ISA/SP/X/ROMs/teclado/VGA, +1CI no vídeo, mesma pinagem/redes da U1. Quatro cargas50pF condicionais no BACKEND; conta selecionada22,72ns/20ns no controlador e7,72ns/5ns no teclado.\n\nAlternativas: máscara SAFE&PHASE_RUN falha em reset breve; três buffers falham em cold; relaxar guardas rejeitado; distribuição Q/QB/inversores é alternativa maior não necessária para estes cenários. Não se usa READY como clear dos bancos antes de WE alto.\n\nEvidência:156cenários estritos,128combinações, três reversões que reproduzem os defeitos,48cortes SRAM, oito CPU/scans, vetores e boot ideal. Compatibilidade funcional/pinagem conferida, porém novo hold0,5ns e caminhos de mux/min-delay entram no futuro STA global. Critérios restantes: fulltimedboot, cargas extraídas/jitter/slew/PVT/CDC/POR/energia, DAC/firmware, união/ERC/footprints/PCB/DRC e protótipo. Ver NET26.md.\n''',
      'PROVENANCE.md':'''\n\nNET-26,26/11/2026, base64d01218193259dfc3740f71b6af5ecbe154149e: três variantes nativas separadas derivam dos JSON NET25/NET17. Builders históricos não são executados nem originais alterados. Pinos/XML/cargas conjuntas e CSV conferidos; novo pacote local e família real do teclado têm modelos e guardas correspondentes. sim/net26 registra projeções warm/reset binárias e atraso selecionado separadamente da netlist estrita. Icarus é a fonte exclusiva das regressões aceitas. Pesquisa opcional CVC preserva fonte/versão/build/falhas/limites e recuperação do ambiente; não foi adotada nem se redistribui seu runtime. Registros intermediários em development não são aprovações finais. Manifesto audita snapshots históricos nos próprios commits.\n''',
      'CHANGELOG.md':'''\n\n## 2026-11-26 — NET-26\n\n- Novas folhas de reset localP1, clock direto do controlador e AHC174 no teclado, com +1CI local e predecessores preservados.\n-156cenários estritos/128combinações, três negativos,48cortes SRAM/oito CPU, vetores ideais/temporizados e boot/quadro ideal passaram.\n- Inventário460CIs+2módulos ACH; ERC parcial49/13/25 violações e fechamento global/produção continuam abertos. CVC pesquisado e não adotado; programa inteiro temporizado permanece pendente.\n'''}
    for name,extra in extras.items():
        p=ROOT/name;p.write_text(p.read_text()+extra)
    p=ROOT/'.gitattributes';p.write_text(p.read_text()+'\n/verification/net26/**/*.sv -whitespace\n/verification/net26/**/*.log -whitespace\n')

if __name__=='__main__':main()
