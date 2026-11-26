"""Record NET22 engineering decisions without altering historical artifacts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepend(name, text):
    path = ROOT / name
    old = path.read_text(encoding='utf-8')
    if old.startswith('Atualização NET-22'):
        old = old.split('\n\n', 1)[1]
    path.write_text(text + '\n\n' + old, encoding='utf-8')


def main():
    summary = ('Atualização NET-22 (26/11/2026): variante de vídeo corrige sensibilidade do anel de fases a atrasos distintos de buffers. '
               'Shift AHC164/NOR LVC1G27 e carry de linha registrado; 36 CIs, um a mais. '
               '384 combinações de atrasos e256 de assimetria de pulsos, 6.886 casos ideais da CPU, dois cenários temporizados de1.062, boot/quadro completo e cortes de reset passaram; '
               'osciladores físicos e fechamento global continuam pendentes. ')
    prepend('README.md', summary + 'Ver [circuito e evidências](docs/engineering/NET22.md); placa não liberada.')
    prepend('ROADMAP.md', summary + 'Próximo: fontes físicas de clock, outros ramos CPU/controlador e temporização global; depois energia/DAC/firmware/união/ERC/PCB/protótipo. Ver docs/engineering/NET22.md.')
    prepend('CHANGELOG.md', summary + 'Antecessores e falhas intermediárias preservados; detalhes em docs/engineering/NET22.md.')
    prepend('PROVENANCE.md', 'Atualização NET-22, 26/11/2026: base 03e224b48ec1657ea2adfd8330c9d3bf4d262255. hardware/video_common_clock e sim/net22 separados; PDFs originais TI/Abracon/ECS/onsemi, extrações e timeouts de coleta registrados. Rebuild nativo serial precede os testes. Captura tardia do builder e correção somente da data herdada do relatório são explicitamente documentadas em docs/engineering/NET22.md. Não são materiais históricos recuperados nem medições físicas.')
    prepend('docs/engineering/PRODUCTION_GATES.md', summary + '44 violações ERC parciais, sem exceções. Carga é orçamento; matriz digital não testa slew/jitter/MTBF nem todo PVT. Ver NET22.md.')
    prepend('docs/engineering/VALIDATION_STATUS.md', summary + 'Evidências e escopos em [NET22](NET22.md); resultados integrados em verification/net22. Não somar coberturas sobrepostas.')
    path = ROOT / 'docs/engineering/VALIDATION_STATUS.md'
    text = path.read_text(encoding='utf-8')
    replacements = {
        '| 1. Relógio, raster e captura de vídeo |': '| 1. Relógio, raster e captura de vídeo | NET-22: shift de fases comum e carry registrado, dois quadros por cenário, matriz384 e cortes160; sensibilidade anterior a skew reproduzida | Cargas/setup/hold/PVT globais, osciladores e reset/MTBF físico; programa/quadro temporizado completo |',
        '| 6. Temporização global |': '| 6. Temporização global | NET-22 testa extremos selecionados de buffers/CQ/NOR/duty; CPU/controlador ainda têm ramos derivados a analisar, WE até94ns no modelo integrado | Setup/hold/recovery/removal, todos os mínimos/máximos, tensão/temperatura, skew/jitter/slew e MTBF; regressão integrada correspondente |',
        '| 8. Esquema global e ERC |': '| 8. Esquema global e ERC | Folhas parciais; vídeo NET22 tem44 violações sem exceções, demais folhas preservadas | Unir todos os blocos/pinos/alimentações e resolver erros; não inserir exceções para esconder entradas sem fonte |',
    }
    text = '\n'.join(next((new for prefix, new in replacements.items() if line.startswith(prefix)), line) for line in text.splitlines()) + '\n'
    path.write_text(text, encoding='utf-8')
    path = ROOT / 'DECISIONS.md'
    old = path.read_text(encoding='utf-8')
    if '## ADR E27' not in old:
        path.write_text('''## ADR E27 — Compartilhar fases no shift e registrar carry de linha

26/11/2026. Base NET21, decisão e resultados em [NET22](docs/engineering/NET22.md).
O anel anterior falha no modelo com atrasos independentes admissíveis dos
buffers. Adotar variante separada com AHC164, NOR3 LVC1G27 e um novo AHC74:
36 CIs no vídeo, um a mais. Contadores H/RUN/SLOT compartilham ramo, contadores
V compartilham outro; terminais de linha/quadro registrados em P3, clock de
captura exportado depois do buffer. Backend continua sem clear assíncrono.

Alternativas: manter atrasos iguais na simulação não fecha skew; reagrupar só
o anel passou nos ensaios intermediários mas deixa outros caminhos a resolver;
um clock driver diferente exige fonte, carga e condições garantidas próprias.
Preservar CPU/ISA/X/SP/flags/VGA/WAIT/COMMIT e firmware. Fase de reset passa de
P3=1 para quatro zeros, com auto-injeção na primeira borda válida e saídas
inibidas durante partida. Custo de mais um CI aceito por equivalência funcional
e redução da dependência entre ramos. Não remove requisito de análise global.

Aceitação desta etapa: XML/pinos conferidos, fases/raster/SLOT/quadros e reset,
matriz digital selecionada com monitores estritos downstream, regressões
CPU/boot/teclado/WE com marcadores completos e negativos detectados, fontes e
hashes auditados. Não equivale a slew/MTBF/PVT completo ou fabricação. ERC44
sem exceções, oscilador/BOM/energia/DAC/PCB/protótipo permanecem abertos.

''' + old, encoding='utf-8')
    path = ROOT / 'AGENTS.md'
    old = path.read_text(encoding='utf-8')
    if '## Continuidade NET-22' not in old:
        path.write_text('''## Continuidade NET-22

- Leia docs/engineering/NET22.md. hardware/video_common_clock é variante separada com36CIs, +1 sobre vídeo anterior. U9 AHC164/U10 LVC1G27 reais, U36 registra H/V emP3. Não inventar AHC27 nem código comercial completo de oscilador.
- Reset das fases agora0000, auto-injeção pela NOR; saídas inibidas na partida. MASTER quatro pinos comuns; H/RUN/SLOT comuns, V comum, captura após buffer. Backend sem clear assíncrono. Manter V_EN em ENP, sem recadear ENT.
- Matriz384 varia atrasos digitais selecionados/CQ/NOR/duty; não é slew elétrico, jitter, MTBF ou todo PVT. Outros ramos CPU/controlador continuam abertos. Orçamento50pF não é extração de PCB.
- Relatório de quadros teve somente data corrigida, original e anotador preservados. Log tardio missing-et é sucesso após correção, não log do erro original. Não reclassificar evidências.
- Fontes de clock ainda são estímulos. Abracon ACH é pesquisa/configuração candidata, sem código completo homologado/circuito físico. Não adotar ECS2100X direto no trilho5,392V, LVC125A em5V ou CL150pF do AC125 sem resolver conflito do datasheet.
- ERC parcial44 violações sem exceções. Produção exige energia/POR/consumo, DAC, firmware de eventos, união global/ERC, footprints/PCB/DRC e protótipo; manter diagnostic.asm como falha histórica conhecida.

''' + old, encoding='utf-8')


if __name__ == '__main__':
    main()
