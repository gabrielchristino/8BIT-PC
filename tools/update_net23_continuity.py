"""Record source-driven clock candidate and keep physical acceptance explicit."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def prepend(name,text):
    path=ROOT/name
    old=path.read_text(encoding='utf-8')
    if old.startswith('Atualização NET-23'):
        old=old.split('\n\n',1)[1]
    path.write_text(text+'\n\n'+old,encoding='utf-8')


def main():
    summary=('Atualização NET-23 (26/11/2026): dois osciladores ACH candidatos no esquema e recepção da CPU por duas Schmitt livres, sem CI adicional de lógica. '
             'Partida/falta de clock, pinos SRAM, oito cortes de escrita da CPU e6.886 casos ideais/dois cenários temporizados de1.062 passaram. '
             'Carga15pF exige trilhas até5pF e código completo/BOM, jitter/POR e temporização global continuam abertos. ')
    prepend('README.md',summary+'Ver [circuito e escopos](docs/engineering/NET23.md); placa não liberada.')
    prepend('ROADMAP.md',summary+'Próximo: largura de pulso e ramos da distribuição global, energia/consumo/USB-C/DAC e união de esquema; firmware de eventos, PCB/DRC/protótipo seguem pendentes.')
    prepend('CHANGELOG.md',summary+'Variante intermediária e falhas de fixture preservadas; detalhes em docs/engineering/NET23.md.')
    prepend('PROVENANCE.md','Atualização NET-23, 26/11/2026: base cbb38703c34cf119612f39ecb0255940e670f974. hardware/clocked_reset e sim/net23 separados; ACH configurados L/C/T/A15pF com código completo aberto, não peças ficticiamente homologadas. Reutilização final U2 canais4/5; primeira variante U1 preservada em development/pre-cpu-schmitt com30 arquivos/hash. Metadados distinguem sete CIs digitais, um supervisor e dois módulos osciladores. Fonte LVC2G125 preservada só como pesquisa; erros e correções explícitos em NET23.md.')
    prepend('docs/engineering/PRODUCTION_GATES.md',summary+'12 violações ERC parciais sem exceções. Simulação de oscilador é comportamental e alimentação qualificada é hipótese; não aprova VDD inválido. Ver NET23.md.')
    prepend('docs/engineering/VALIDATION_STATUS.md',summary+'Os números e resultados de instruções são conferidos em [NET23](NET23.md), sem herdar boot NET22 como nova execução.')
    path=ROOT/'docs/engineering/VALIDATION_STATUS.md'
    text=path.read_text(encoding='utf-8')
    rows={
        '| 1. Relógio, raster e captura de vídeo |':'| 1. Relógio, raster e captura de vídeo | NET22 fases/carry; NET23 osciladores candidatos e Schmitt no esquema, modelos de partida/ausência e integração CPU/memória | Código completo/cargas extraídas, slew/jitter/MTBF/PVT e distorção de pulsos global; programa/quadro temporizado completo |',
        '| 6. Temporização global |':'| 6. Temporização global | NET22 matriz de atrasos/pulsos selecionados; NET23 fontes configuradas e corners de frequência. Backend tem vários buffers, ramos CPU/controlador ainda precisam análise | Fechar largura de pulso acumulada, setup/hold/recovery/removal, mínimos/máximos/carga/tensão/temperatura, skew/jitter/slew e MTBF |',
        '| 8. Esquema global e ERC |':'| 8. Esquema global e ERC | Folhas parciais; fonte/reset NET23 tem12 violações, vídeo NET22 tem44, sem exceções | Unir blocos/pinos/alimentações e resolver erros; não mascarar entrada sem fonte ou alimentação não implementada |',
        '| 9. BOM e footprints |':'| 9. BOM e footprints | Configurações candidatas e PDFs por família; ACH L/C/T/A15pF tem código completo aberto e exige até5pF de trilhas na entrada | Conferir códigos reais, pinagem, encapsulamento/faixa/carga/consumo e footprint de cada componente; não tratar típico como limite |',
    }
    text='\n'.join(next((new for prefix,new in rows.items() if line.startswith(prefix)),line) for line in text.splitlines())+'\n'
    path.write_text(text,encoding='utf-8')
    path=ROOT/'DECISIONS.md'
    old=path.read_text(encoding='utf-8')
    if '## ADR E28' not in old:
        path.write_text('''## ADR E28 — Fontes ACH candidatas e recepção Schmitt da CPU

26/11/2026. Base NET22; detalhes em [NET23](docs/engineering/NET23.md).
Construir variante separada com dois módulos configurados ACH25,175MHz/100kHz,
L/C/T/A, carga padrão15pF. Enable em VDD, sem gate por RAW. Uma entrada por
oscilador exige10pF de Ci a5V mais5pF de trilha; confirmar na PCB e na BOM.
Dois Schmitt livres de U2 recebem CPU_OSC e formam CPU_CLK não inversor,
alimentando U7. Oito CIs existentes (sete digitais/um supervisor) preservados,
dois módulos osciladores/capacitores acrescentados; mesma ISA/X/SP/flags/VGA.

Alternativas: dois pinos diretos na fonte da CPU excedem15pF; AHC125 livre
requer qualificar a forma da borda40ns frente ao limite20ns/V. Schmitt evita
essa hipótese sem pacote adicional. Opção ACH50pF não herda automaticamente
tempos da tabela15pF; LVC2G125 tem Ci típico3,5pF em3,3V e não máximo em5V.
Fontes3,3V acrescentam regulação/tradução e outra análise de pulsos. Não se
declara código de compra/carga/jitter/POR homologado por construir o símbolo.

Aceitação digital da etapa: pinos/XML/carga, fonte iniciando desconhecida,
partida interrompida, clock ausente mantendo WE bloqueado, oito cortes/scans
reais nominais/corners, instruções com clocks do circuito, negativos e hashes
conferidos. Não há novo boot completo; os resultados NET22 mantêm seu escopo.
Próxima revisão deve fechar duração de pulsos acumulada, clocks CPU/controlador,
energia/POR/consumo/DAC, firmware de eventos e união/ERC/PCB/protótipo.

'''+old,encoding='utf-8')
    path=ROOT/'AGENTS.md'
    old=path.read_text(encoding='utf-8')
    if '## Continuidade NET-23' not in old:
        path.write_text('''## Continuidade NET-23

- Leia docs/engineering/NET23.md. hardware/clocked_reset tem26 componentes/144pinos/7NC: sete CIs digitais, um supervisor e dois módulos ACH configurados, sem código completo homologado. Não confundir módulo configurado com BOM aprovada.
- CPU_OSC entra em U2A4, passa por dois Schmitt livres4/5 e alimenta U7. U1ch0 permanece desabilitado. AHC125 limita entrada a20ns/V em5V, não100; não supor borda linear do ACH40ns. MASTER recebe uma entrada AHC125. Fonte15pF exige Ci10pF a5V+trilhas5pF, ainda não extraídas.
- Fontes da sim/net23 usam modelo comportamental de startup, X antes de VDD válido/start. Alimentação qualificada do oscilador é distinta de RAW do supervisor; não afirmar POR/VDD inválido/jitter/MTBF aprovados. Enable é VDD; Hi-Z desabilitado não foi caracterizado pelo modelo.
- Oito cortes de escrita da CPU dividem-se em quatro nominais e quatro com frequências opostas±50ppm; não somar resultados da variante intermediária U1, preservada em development/pre-cpu-schmitt. Diagnóstico novo não substitui diagnostic.asm histórico ausente.
- Vetores ideais usam run_clocked_vectors_ideal.py; temporizados usam run_clocked_vectors.py --timed --quick. Ideal altera explicitamente período/startup do modelo, sem frequência física alegada. Não regenerar/modificar entradas durante execuções ativas.
- Depois do builder, annotate_clock_counts.py corrige somente classificação de metadados7digitais/1supervisor, preservando relatório original. Não atribuir essa anotação a uma segunda execução de simulação.
- ERC parcial12 violações sem exceções. Fechar largura de pulso através dos buffers do backend, ramos CPU/controlador, energia/consumo/POR/USB-C/DAC, firmware de eventos e união/ERC/footprints/PCB/DRC/protótipo antes de fabricação.

'''+old,encoding='utf-8')


if __name__=='__main__':main()
