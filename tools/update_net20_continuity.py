"""Record NET20 scope without rewriting older evidence or approvals."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = 'Atualização NET-20A'


def main():
    updates = {
        'README.md': 'Atualização NET-20A (26/11/2026): domínios de reset ligados à CPU/MMIO/memórias; 48 cortes de escrita observados nos pinos SRAM, inibição em até 80 ns no cenário selecionado, pausas de clocks e raw scan passaram. Supervisor continua forcepoint qualificado: Ci máximo do buffer esgota o CL=10 pF da condição temporal anterior, sem margem de trilha. Ver [evidências e limites](docs/engineering/NET20.md); placa não liberada.',
        'ROADMAP.md': 'Atualização NET-20A (26/11/2026): sequência digital global candidata ligada à CPU/teclado/memórias, reset rápido da CPU com payload retido e bancos atrasados, distribuição parcial de clocks/cargas e testes diretos nos pinos WE/endereço. Próximo: fechar interface de carga/limiares do supervisor, energia/clock/DAC e união elétrica; firmware de eventos, PCB e protótipo continuam pendentes. Ver docs/engineering/NET20.md.',
        'PROVENANCE.md': 'Atualização NET-20A, 26/11/2026: variante nova de hardware/power_reset e adaptador separado de NET-19A, base 8af86e361e6eb510ff32c5f4c45cabc7ae633c85. Grafos KiCad conferidos, projeção digital e transformações com hashes; relatórios/negativos/fonte do primeiro ensaio preservados em verification/net20. PDFs TI originais em references/net20 são pesquisa, não BOM adotada. Manifesto da etapa registra origens e limitações. Nenhum original histórico foi corrigido ou substituído.',
        'CHANGELOG.md': 'Atualização NET-20A, 26/11/2026: oito CIs de reset/distribuição, integração digital de domínios, monitores SRAM independentes de SAFE, 48 cortes em RAM/VRAM, CPU/relógios/teclado e hold-up condicional revisado. Registrada lacuna de CL do supervisor; nenhuma aprovação física inferida. Ver docs/engineering/NET20.md.',
        'docs/engineering/VALIDATION_STATUS.md': 'Atualização NET-20A, 26/11/2026: [reset integrado](NET20.md) por pinos, CPU rápida e bancos atrasados; 48 cortes ativos, dois negativos e raw scan ideal/com atrasos, com parada de clocks. WE bloqueado em até 80 ns nos cenários executados. A condição CL=10 pF do supervisor não comporta Ci máximo do AHC125 mais trilhas; hold-up permanece condicional. ERC parcial: 12 violações. Energia analógica, clock/skew/PVT global, DAC, firmware de eventos, PCB/protótipo abertos.',
        'docs/engineering/PRODUCTION_GATES.md': 'Atualização NET-20A, 26/11/2026: a ordem digital WE/bancos está ligada aos blocos e observada nos pinos SRAM. Não encerra o gate de alimentação: a entrada AHC125 pode ocupar todos os 10 pF da condição temporal do TPS3703. Fechar carga, transições, limiares, POR/hold-up e consumo antes de aprovação física; 12 violações ERC parciais continuam sem exceções. Ver NET20.md.',
    }
    for name, text in updates.items():
        path = ROOT / name
        old = path.read_text(encoding='utf-8')
        if MARK in old:
            raise ValueError('Already recorded ' + name)
        path.write_text(text + '\n\n' + old, encoding='utf-8')
    path = ROOT / 'DECISIONS.md'
    path.write_text(path.read_text(encoding='utf-8') + '''

## ADR E25 — Separar reset rápido da CPU e bancos que afetam SRAM

26/11/2026. Base NET-19A/NET-18; variante NET-20A, não liberação física.
Decisão: afirmar reset da CPU por RAW_BUFFERED, liberar após bancos e duas
bordas de CPU; manter reset de controlador/decoder/MMIO/posse atrás do RC,
com inibidor rápido e buffers separados. RUN preservado. A CPU não dirige mais
endereço/dado SRAM diretamente: os HC377 sem clear retêm o payload capturado.
Alternativas: limpar todos os bancos imediatamente arrisca mudança de endereço
antes de WE; atrasar também a CPU não é necessário para a retenção e prolonga
atividade arquitetural em falha. Um novo gate assíncrono em RUN criaria outra
entrada temporal. Não mudar ISA/X/SP/flags/VGA nem prometer rollback de byte.

Evidência/aceitação: XML exato de 22 componentes/oito CIs/132 pinos; 48 cortes
ativos com WE alto em até 80 ns antes de bancos, payload retido, nenhum endereço
físico mudando enquanto WE baixo; dois negativos calibram a rejeição. Pausas das
fontes retêm SAFE baixo até ambas retomarem. Raw scan na CPU usa domínios reais.
Orçamento até bancos/decoder sobe a 20 us; hold-up repetido, 64+3 cenários
condicionais. Critério de produção permanece aberto: CL do supervisor, fontes,
transições, cargas/clock/skew/PVT/MTBF, ERC global, PCB e protótipo. Em particular
Ci máximo AHC125=10 pF não deixa margem para trilhas no teste CL=10 pF do
TPS3703; não promover o prazo analógico anterior a garantia. Alternativas de
datasheet preservadas são pesquisa e exigem novo cálculo/circuito/ADR.
Detalhes e comandos: docs/engineering/NET20.md.
''', encoding='utf-8')
    path = ROOT / 'AGENTS.md'
    path.write_text('''## Continuidade NET-20A

- Leia docs/engineering/NET20.md. hardware/system_reset e sim/net20 são variantes separadas; CPU usa cpu_core_clk/cpu_reset_n, memórias/decoder/MMIO usam resets atrasados distintos. Não voltar a ligar SRAM ao endereço vivo da CPU.
- Reset rápido da CPU pode preceder WE alto porque payload HC377 não tem clear; reset dos bancos/posse/endereço físico precisa ocorrer depois do bloqueio. RUN não é gated assíncrono. Monitorar SRAM mesmo após SAFE cair.
- run_reset_memory.py cruza dois extremos RC e duas políticas binárias: 48 cortes ativos, não milhares de cortes herdados. Negativo de endereço acontece 60 ns após RAW, com SAFE interno baixo; deve cair no monitor independente.
- Supervisor é forcepoint, não modelo analógico. Ci máximo do AHC125 esgota CL=10 pF do TPS3703; zero margem para trilhas, interface não qualificada. Não apresentar hold-up condicional como garantia física. Alternativas em references/net20 são apenas pesquisa.
- Distribuição selecionada tem até quatro entradas/saída no orçamento 10pF/entrada+10pF/trilhas; não fecha cargas extraídas, clock físico, skew/PVT/MTBF ou consumo global. ERC parcial tem 12 violações, sem exceções. Programa completo temporizado, energia, DAC, firmware de eventos e PCB/protótipo continuam abertos.

''' + path.read_text(encoding='utf-8'), encoding='utf-8')
    print('Recorded NET20 scope and ADR E25')


if __name__ == '__main__':
    main()
