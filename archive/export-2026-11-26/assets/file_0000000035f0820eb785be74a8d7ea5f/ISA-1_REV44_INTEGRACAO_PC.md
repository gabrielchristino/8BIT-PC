# ISA-1 — Revisão 4.4 — Integração lógica do PC de 16 bits

## Resultado
O modelo de quatro contadores síncronos de 4 bits passou 752.281 asserções comportamentais, incluindo retenção sem borda, LOAD de EA e RET, prioridade do CLEAR, incremento com wrap-around, chamadas aninhadas abstratas e teste negativo de carry. **Não é simulação de portas, circuito elétrico ou CPU completa.**

## Contrato proposto para o esquemático
- `PC_Q[15:0]`: saídas dos quatro contadores, nibble 0 menos significativo.
- `PC_LOAD_D[15:0]`: saída de um mux 2:1 de 16 bits, escolhendo `EA_Q[15:0]` ou `RET_Q[15:0]`. Quatro 74HC157 quádruplos são uma candidata de implementação; verificar polaridade de seleção e pinagem da variante real.
- `PC_SEL_RET`: seleciona RET no mux, deve estabilizar antes da borda que ativa carga.
- `PC_LOAD_N`: carga paralela simultânea nos quatro nibbles.
- `PC_CLR_N`: limpeza síncrona simultânea nos quatro nibbles; **não é reset assíncrono de alimentação**.
- `PC_COUNT`: habilitação geral de incremento; a habilitação efetiva de cada nibble é `PC_COUNT` AND (todos os nibbles inferiores == 0xF). Mesmo clock nos quatro CIs.
- `PC_CLK`: clock comum; não usar saída de carry como clock do próximo contador.
- `PC_HOLD`: estado lógico com carga e limpeza inativas e contagem desabilitada.

## Regras de controle
1. RESET tem prioridade sobre LOAD e COUNT na borda de clock, segundo hipótese da revisão 4.3 (confirmar no datasheet exato).
2. LOAD tem prioridade sobre COUNT; os 16 bits devem vir de **uma única fonte selecionada**, não de duas saídas dirigindo os mesmos fios.
3. Sem borda de clock, o PC mantém o valor, inclusive com CLEAR solicitado (modelo síncrono).
4. Durante CALL, o PC de retorno precisa estar preservado antes de carregar o destino. Durante RET, os dois bytes recuperados da pilha devem ser reunidos em `RET_Q` antes de LOAD.
5. O modelo de chamadas aninhadas desta revisão utiliza uma pilha Python abstrata, **não comprova a escrita/leitura da SRAM**.

## Descobertas e riscos
- O modelo de carry está correto para incremento simultâneo, mas falta escolher se o hardware usa saída de terminal count do CI ou portas AND dedicadas; **não misturar saídas de carry com clocks**.
- A contagem de 8 CIs (quatro contadores + quatro 74HC157) exclui portas de carry, decodificação, buffers e supervisão.
- O relatório Rev3.3 tem 19 instruções, mas a presença de etapas simbólicas não demonstra execução em microcódigo binário. Necessário reconciliar fonte de verdade, opcode e temporização.
- A solução com 74HC163 segue **candidata preferida**, não aprovada para PCB.

## Critérios para a revisão 4.5
1. Escolher fabricante e part number completo do contador; validar pinagem, prioridades, alimentação e setup/hold no datasheet oficial.
2. Gerar conexões pino a pino do PC, incluindo alimentação, desacoplamento, sinais de controle e seleção EA/RET.
3. Executar simulação digital em nível de portas/HDL com transições de clock e, quando disponível, simulação com atrasos de propagação.
4. Integrar MAR, memória e pilha com CALL/RET real, sem usar lista Python como substituto da SRAM.
5. Registrar condições de reset e clock de partida antes de qualquer liberação de escrita.

## Reprodução
`python3 isa1_rev44_pc_integration.py` produz `isa1_rev44_results.json`.
