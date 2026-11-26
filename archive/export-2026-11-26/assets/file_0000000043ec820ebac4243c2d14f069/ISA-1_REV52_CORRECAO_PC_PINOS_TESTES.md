# ISA-1 — Revisão 5.2 — Correção física proposta para /LOAD e COUNT

## Origem
Base: netlist parcial da Rev 5.0 e contraexemplo reproduzível da Rev 5.1. A falha ocorria quando `/LOAD=0` na terceira borda, após a liberação de `/CLR` e antes de `CPU_RUN=1`.

## Alteração de lógica e pinagem
- `PC_LOAD_N_SAFE = PC_LOAD_N_REQ OR NOT_CPU_RUN`.
  - U_INV = SN74HC04D, pino 1 `CPU_RUN`, pino 2 `NOT_CPU_RUN`, pino 14 VCC, pino 7 GND.
  - U_OR = SN74HC32D, pino 1 `PC_LOAD_N_REQ`, pino 2 `NOT_CPU_RUN`, pino 3 `PC_LOAD_N_SAFE`, pino 14 VCC, pino 7 GND.
  - U_OR.3 ligado aos pinos 9 dos quatro U_PC0..3 (SN74HC163D).
- `PC_COUNT_SAFE = PC_COUNT_REQ AND CPU_RUN`.
  - Reaproveita a terceira porta do U_AND = SN74HC08D, pino 9 `PC_COUNT_REQ`, pino 10 `CPU_RUN`, pino 8 `PC_COUNT_SAFE`.
  - U_AND.8 alimenta ENP (pino 7) de U_PC0..3 e ENT (pino 10) de U_PC0. ENT dos demais continua em cascata RCO.
- Portas não utilizadas dos novos chips: entradas aterradas e saídas desconectadas, conforme JSON; `NC` é uma coleção de pinos isolados, não uma rede condutora.
- O circuito agora totaliza 13 CIs no bloco parcial (11 existentes + 2 novos).

## Teste realizado
Executar `python isa1_rev52_build_verify.py` na pasta. Gera a netlist corrigida e os resultados JSON. Foram 1.048.576 transições abstratas (65.536 valores iniciais × 2 cargas × 2 contagens × 4 bordas), 198 pinos únicos, 84 rótulos de redes. Nenhum pino duplicado ou não atribuído nos 13 CIs. Tabela verdade de 8 casos incluída nos resultados.

## Limitações / próximos gates
1. **Não é esquemático KiCad nem ERC.** A netlist JSON registra intenção de conectividade; não inclui footprints, valores de desacoplamento, fonte, supervisor ou oscilador.
2. `CPU_RUN` deve estar estável antes da borda do clock e respeitar setup/hold dos HC163; a liberação do estágio RST_Q3 no mesmo clock não substitui uma análise temporal.
3. A cadeia de RCO precisa de orçamento temporal de propagação e margem em frequência, tensão e temperatura.
4. É necessário verificar com datasheets oficiais o pinout de cada variante específica dos SN74HC04D, SN74HC32D e SN74HC08D antes de PCB.
5. O supervisor, brownout e proteção independente de `/WE` da SRAM/EEPROM continuam **não implementados**. Não é seguro fabricar.
6. A sequência de busca real e os sinais `PC_LOAD_N_REQ` / `PC_COUNT_REQ` permanecem interfaces do microsequenciador não projetado.
7. A expressão de bloqueio lógico não prova ausência de glitches em alimentação instável; a rede de reset e proteção de escrita requerem análise elétrica separada.

## Próxima revisão proposta (5.3)
Selecionar e conferir os componentes de supervisor e oscilador; especificar alimentação, reset e inibição independente de escritas; preparar esquemático EDA e ERC assim que a ferramenta estiver disponível.
