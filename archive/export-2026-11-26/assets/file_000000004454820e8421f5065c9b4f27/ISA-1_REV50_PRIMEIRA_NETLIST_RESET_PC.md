# ISA-1 — Revisão 5.0 — Primeira netlist parcial PC/reset

## Escopo e proveniência
Integra a lista de pinos da Rev 4.5 (`isa1_rev45_nets.json`) com o contrato da Rev 4.9 (`ISA-1_REV49_VALIDACAO_RESET_CLOCK.md`). **Não é um esquemático KiCad, não é um circuito completo e não é uma simulação elétrica.**

## Componentes mapeados
- U_PC0..3: quatro SN74HC163D SOIC-16, PC de 16 bits.
- U_MUX0..3: quatro SN74HC157D SOIC-16, seleção de EA/RET para carga do PC.
- U_RST1 e U_RST2: dois SN74HC74D SOIC-14, três FF usados e um sobressalente.
- U_AND: um SN74HC08D SOIC-14, duas portas usadas e duas com entradas aterradas.
- TPS3808G50DBVR e oscilador: **ainda não conectados**. SUP_RESET_N e SYS_CLK são interfaces externas não resolvidas.

## Ligações críticas
- Todos os contadores PC: pino 2 = SYS_CLK; pino 1 = PC_CLR_N; pino 9 = PC_LOAD_N; ENP/ENT conforme Rev 4.5.
- U_RST1 FF1: /CLR p1 SUP_RESET_N, D p2 VCC, CLK p3 SYS_CLK, /PRE p4 VCC, Q p5 RST_Q1.
- U_RST1 FF2: /CLR p13 SUP_RESET_N, D p12 RST_Q1, CLK p11 SYS_CLK, /PRE p10 VCC, Q p9 RST_Q2.
- U_RST2 FF1: /CLR p1 SUP_RESET_N, D p2 RST_Q2, CLK p3 SYS_CLK, /PRE p4 VCC, Q p5 RST_Q3.
- U_AND gate 1: p1 SUP_RESET_N, p2 RST_Q2, p3 PC_CLR_N.
- U_AND gate 2: p4 SUP_RESET_N, p5 RST_Q3, p6 CPU_RUN.
- U_RST2 FF2 sobressalente: /CLR e /PRE em VCC; D e CLK em GND; saídas sem conexão.

## Observações importantes de segurança
1. CPU_RUN é uma autorização lógica, **não é uma proteção elétrica de /WE**. Ainda não conectamos nenhum driver de escrita.
2. Desassertar SUP_RESET_N assincronamente perto de uma borda do clock pode causar problemas de recuperação/remoção ou metastabilidade. Necessária análise com datasheets e circuito de liberação apropriado.
3. O teste considera PC_COUNT ativo na quarta borda, mas a geração real de PC_COUNT e PC_LOAD_N pelo sequenciador ainda não foi projetada. Portanto não foi validada a execução da primeira instrução.
4. A rede 'NC' no JSON lista terminais intencionalmente não conectados, **não representa uma rede elétrica comum**.
5. O supervisor open-drain exige pull-up e CT conforme datasheet; pinagem exata e comportamento de power-down permanecem pendentes. Oscilador e alimentação não especificados.
6. O arquivo JSON é uma netlist de intenção com pinagem física de CIs candidatos; não é compatível diretamente com ferramentas EDA, não passou por ERC/DRC, e não tem footprints ou PCB.
7. Os dados da Rev 4.5 são herdados; sua correspondência com as variantes de compra deve ser revalidada contra as fichas oficiais antes de fabricar.

## Teste reproduzível
`python isa1_rev50_reset_netlist.py`

Resultado: 170 atribuições únicas de pinos; 262.144 verificações de transições abstratas aprovadas. Cobertura: inicialização de PC para todos os valores, três bordas de reset e quarta borda de incremento; **sem temporização elétrica**.

## Próximo gate
Escolher supervisor e oscilador com part numbers e documentação oficial, revisar os limiares de tensão, implementar reset assíncrono e sincronização de liberação, proteger /WE em condições de brownout, integrar EA/RET e microsequenciador. Depois gerar esquemático EDA real e rodar ERC.
