"""Record the Schmitt/supervisor candidate and keep physical gates explicit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    updates = {
        'README.md': 'Atualização NET-21A (26/11/2026): supervisor candidato TPS3808 e recepção Schmitt resolvem o conflito do orçamento de carga anterior: 20 pF previstos contra condição de teste de 50 pF. Oito CIs preservados; 48 cortes de escrita, quatro com CPU real, raw scan temporizado e reservas condicionais passaram. Nova janela interna proposta de 5,392 V exige qualificação da fonte. Ver [circuito, resultados e limites](docs/engineering/NET21.md); produção continua bloqueada.',
        'ROADMAP.md': 'Atualização NET-21A (26/11/2026): variante candidata de supervisor/Schmitt montada por pinos, com orçamento de entrada, janela DC/hold-up e resets da CPU/teclado/memórias testados condicionalmente. Próximo: fontes físicas de clock, fechamento de fonte/proteções/consumo, DAC e união global; firmware de eventos, PCB e protótipo seguem abertos. Ver docs/engineering/NET21.md.',
        'PROVENANCE.md': 'Atualização NET-21A, 26/11/2026: base 5c8eba51346be08b5f2ed53da111aef970f71133; hardware/schmitt_reset e sim/net21 separados de NET20. TPS3808 SBVS050N e AHC14 SCLS238P são referências primárias preservadas; pinagem DBV conferida por XML, transformações/testes e falhas intermediárias com hashes. Projeção digital mantém RAW externo e SPICE da linha é proxy condicional, sem modelo analógico do supervisor. Originais e snapshots anteriores permanecem intactos.',
        'CHANGELOG.md': 'Atualização NET-21A, 26/11/2026: TPS3808G01DBVR, pull-up 100 kohm, dois Schmitt em portas livres, divisor de sense 1120/100 ohm e proposta de feedback 57,4k/10k para 5,392 V internos. Oito CIs/132 pinos; 48 cortes do mestre de teste, quatro escritas reais da CPU interrompidas e retomadas, scan, 64 cenários de hold-up e 24 de linha RC. Hipóteses, negativos e ERC parcial não aprovado em docs/engineering/NET21.md.',
        'docs/engineering/VALIDATION_STATUS.md': 'Atualização NET-21A, 26/11/2026: [supervisor/Schmitt candidato](NET21.md) acomoda orçamento de 20 pF contra CL=50 pF especificado, preservando oito CIs. 48 cortes ativos, quatro com CPU real, scan temporizado em políticas 0/1 e SPICE condicional passaram. A janela DC proposta de 5,392 V tem margens pequenas; consumo, regulador/isolamento/POR e circuito físico não qualificados. Próximo: fontes de clock e fechamento global de energia/DAC/cargas, firmware de eventos, ERC/PCB/protótipo.',
        'docs/engineering/PRODUCTION_GATES.md': 'Atualização NET-21A, 26/11/2026: o conflito aritmético CL/Ci da NET20 tem alternativa em hardware/schmitt_reset, com TPS3808/Schmitt e orçamento 20 pF/condição 50 pF. A proposta depende de novo trilho nominal 5,392 V e qualificação de ripple/regulação/isolamento/corrente/POR. Não confundir fechamento desse orçamento com aprovação analógica. ERC parcial continua com 12 violações, sem exceções; esquema global/PCB/DRC e ensaio físico seguem obrigatórios. Ver NET21.md.',
    }
    for name, note in updates.items():
        path = ROOT / name
        text = path.read_text(encoding='utf-8')
        if 'Atualização NET-21A' in text:
            raise ValueError('Already recorded ' + name)
        path.write_text(note + '\n\n' + text, encoding='utf-8')
    path = ROOT / 'DECISIONS.md'
    path.write_text(path.read_text(encoding='utf-8') + '''

## ADR E26 — Supervisor com CL50pF e recepção Schmitt em portas livres

26/11/2026. Base NET-20A, variante NET-21A candidata, sem liberação física.
Decisão: TPS3808G01DBVR com CT aberto/MR alto, pull-up100k, sense1120/100 ohm,
dois inversores AHC14 antes de RAW_BUFFERED. Mesmos oito pacotes de reset;
reutilizar U2 e desabilitar o canal antigo U1. Pinagem DBV explícita; preservar
payload/CPU/ISA/X/SP/flags/VGA e sequência rápida/demorada anterior.
Alternativas: AHC1G125 também tem Ci máximo10pF e não deixa margem no teste do
TPS3703; capacitância típica LVC não demonstra limite garantido menor. Aumento
arbitrário de atraso analógico ou declaração de trilha zero foram rejeitados.
O TPS3808 admite orçamento20pF contra CL50pF e Schmitt recebe subida lenta.

Impacto elétrico: dispersão/histerese do supervisor exige proposta de feedback
TPS63070 57,4k/10k, saída nominal5,392V interna; USB preservado5V. Margens DC de
retomada20,179mV e teto19,049mV dependem dos orçamentos de referência/resistores,
carga/ripple/caminho, ainda não qualificados. Não reutilizar o valor5,232V de
NET18 como se tivesse passado nesta variante. Não alterar o modelo oficial
anterior para declarar uma simulação do regulador aprovada.

Aceitação no escopo executado: XML22componentes/8CIs/132pinos/9NC, 48 cortes
ativos com WE até94ns, quatro cortes de escrita da CPU com reinício completo,
rawscan em duas políticas binárias, 64+3 reservas condicionais, 24+1 cenários
da linha RC e quatro negativos de janela. Proxy Ron/leakage não é modelo do
supervisor. ERC parcial12 violações, sem exceções. Produção exige fonte/POR e
transientes reais, capacitâncias extraídas, consumo, clocks/PVT/CDC/MTBF, DAC,
esquema global/footprints, PCB/DRC e protótipo. Ver docs/engineering/NET21.md.
''', encoding='utf-8')
    path = ROOT / 'AGENTS.md'
    path.write_text('''## Continuidade NET-21A

- Leia docs/engineering/NET21.md. hardware/schmitt_reset é variante separada de NET20: TPS3808G01DBVR (pinagem DBV), pull-up100k, sense1120/100, duas portas Schmitt antes de RAW_BUFFERED, oito CIs/132pinos/9NC. Não misturar pinagem DRV/TPS3703.
- Proposta de regulação muda para5,392V, feedback57,4k/10k; USB continua5V. Janela antiga5,232V não atende o novo pior limiar de retomada. Margens DC pequenas/condicionais; modelo oficial do regulador segue sem execução completa.
- Orçamento RAW20pF (Ci máximo10pF a5V +trilha10pF) cabe no testeCL50pF, mas não é extraçãoPCB nem garantia completa de supervisor/POR. SPICE da linha é proxy Ron400ohm/leakage, não modelo vendor. Fuga para VDD deve ser passiva, sem fonte ideal elevando RAW acima da alimentação.
- Há48 cortes do mestre de teste com WE até94ns e quatro de CPU real com epoch da SRAM preservado durante a falha, firmware reiniciando seus resultados. Não prometer rollback nem somar escopos distintos. Vetores/boot NET20 não foram novamente executados como NET21.
- União candidata458CIs/30famílias não inclui fonte/USB-C/isolador/osciladores/DAC e não tem consumo fechado. ERC parcial12 violações sem exceções; fontes de clocks, energia/POR/cargas/skew/PVT/MTBF, firmware de eventos e PCB/protótipo abertos.

''' + path.read_text(encoding='utf-8'), encoding='utf-8')
    print('Recorded NET21 scope and ADR E26')


if __name__ == '__main__':
    main()
