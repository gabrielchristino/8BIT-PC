# ISA-1 — Revisão 4.5 — Pinagem e cadeia síncrona do PC

## Fonte de verdade
- TI SN74HC163: https://www.ti.com/lit/ds/symlink/sn74hc163.pdf
- TI SN74HC157: https://www.ti.com/lit/ds/symlink/sn74hc157.pdf

## Escolha provisória
Quatro SN74HC163D SOIC-16 (nibbles 0–3) e quatro SN74HC157D SOIC-16 (seleção EA/RET por grupos de 4 bits). A netlist de **128 pinos** consta de `isa1_rev45_nets.json`. O script verifica atribuição única dos 16 pinos de cada CI e a contagem síncrona para os 65536 estados. Não é um esquemático KiCad nem um modelo elétrico.

## Conexões-chave
- U_PC0..3: pino 2 ao mesmo `PC_CLK`; pino 1 `PC_CLR_N`; pino 9 `PC_LOAD_N`; pino 7 `PC_COUNT`; pino 10 do primeiro `PC_COUNT`, dos demais ao RCO do estágio anterior (pino 15); pino 16 +5V, pino 8 GND.
- PC data A/B/C/D nos pinos 3/4/5/6; QA/QB/QC/QD nos pinos 14/13/12/11.
- U_MUX0..3: seleção comum pino 1 `PC_SEL_RET`; pino 15 `/G` ao GND (saídas sempre válidas); pino 16 +5V, pino 8 GND. A=EA, B=RET. Y conecta a PC_LOAD_D.
- Entradas e saídas completas em JSON.

## Atenções e correções
1. RCO é **combinacional**, dependente de ENT e do estado terminal; não usar como clock. Cadeia de quatro estágios acumula atraso; calcular setup/hold e fmax a partir do datasheet e carga real.
2. `/CLR` é **síncrono**; uma alimentação subindo sem clocks não garante PC=0. Circuito supervisor/clock de partida ainda pendente.
3. A ligação do `/G` do 74HC157 a GND **não é tri-state**: saída permanece dirigida e é forçada a zero quando `/G`=1.
4. Os sinais PC_COUNT, PC_LOAD_N e PC_CLR_N precisam ser mutuamente coerentes no sequenciador. Em especial, reset tem prioridade sobre carga e contagem.
5. Cada CI deve ter desacoplamento local (proposta inicial 100 nF, valor/posição a revisar na PCB); os pinos de controle não podem flutuar.
6. O projeto ainda não cobre EA/RET registradores, alimentação, integridade de sinal, carga de fanout e temporização real.

## Oportunidade de melhoria
O uso de RCO reduz portas externas em comparação com comparar explicitamente todos os nibbles inferiores. Porém **não está demonstrado** que seja mais rápido ou eletricamente melhor. A otimização deve ser confirmada por análise temporal antes da PCB.
