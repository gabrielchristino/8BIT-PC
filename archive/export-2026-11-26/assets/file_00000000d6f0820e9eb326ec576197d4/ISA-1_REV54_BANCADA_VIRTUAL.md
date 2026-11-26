# ISA-1 — Revisão 5.4 — Primeira bancada virtual reproduzível

## Base examinada
Foram reabertos o relatório da revisão 5.3, o relatório 5.2 e a netlist `isa1_rev52_corrected_nets.json`. Esta revisão **não modifica** a netlist física e não inventa um supervisor ou oscilador que ainda não foram escolhidos.

## Entrega
`isa1_rev54_bench.py` implementa um modelo independente por borda do bloco de PC de 16 bits e três estágios de inicialização. Testa precedência do clear síncrono do HC163, carga paralela, contagem e o bloqueio das duas solicitações enquanto CPU_RUN=0. Produz `isa1_rev54_waveform.csv` e `isa1_rev54_results.json`.

## Resultado reproduzido
577.702 verificações sem divergência: 22 verificações estruturais mínimas, 327.680 verificações sistemáticas de partida/primeira carga/brownout para todos os 65.536 estados iniciais, e 250.000 transições pseudoaleatórias comparadas com uma função de referência separada.

## Limitações importantes
1. Este é um modelo de transição ideal por borda. Não é uma simulação de componentes com atrasos, não é ERC/DRC nem SPICE.
2. O reset assíncrono dos 74HC74 é representado na sequência demonstrativa por zerar explicitamente os estágios quando o supervisor é acionado; o PC HC163 continua com reset síncrono e requer clock para zerar.
3. A liberação de CPU_RUN e o seu efeito sobre a lógica combinacional no mesmo ciclo dependem de propagação real; o modelo usa valores **anteriores à borda**. Não comprova setup/hold, recovery/removal ou ausência de glitches.
4. `SUP_RESET_N` e `SYS_CLK` continuam redes externas sem componentes físicos. `EA_Q`, `RET_Q`, `PC_LOAD_N_REQ`, `PC_COUNT_REQ` ainda não têm seus circuitos completos.
5. Bloqueio físico independente de /WE da SRAM e EEPROM, especialmente durante queda de VCC, **não está implementado**. Não é seguro fabricar.
6. Uma auditoria de contagem de pinos e redes não garante que a pinagem seja eletricamente correta nem que todas as entradas tenham polarização válida.

## Próximas validações prioritárias
- Conferir pinagem e comportamento de um supervisor de 5 V específico, incluindo limiar e atraso, e escolher oscilador de saída CMOS de 5 V com tempo de partida e frequência.
- Desenhar o caminho de /WE com estado inativo garantido durante brownout, inclusive quando 74HC não está dentro da faixa de VCC garantida.
- Montar arquivo de esquemático EDA mínimo e fazer ERC numa instalação com KiCad disponível.
- Construir orçamento temporal com limites de datasheet para RCO, entradas ENP/ENT, clock e lógica de reset.

## Execução
Na pasta `/mnt/data/isa1`: `python isa1_rev54_bench.py`.
