# ISA-1 — Revisão 3.8 — Auditoria do barramento de dados

**Estado:** topologia lógica candidata; não é circuito elétrico nem netlist pino a pino.

## Base revisada
Rev. 3.5 define acesso de memória em fases; Rev. 3.6 exige um único driver para DB[7:0] e proíbe conectar diretamente saídas Q dos 74HC377; Rev. 3.7 definiu o mux de endereços PC/SP/EA para MAR. O DB precisa de solução independente.

## Decisão para o protótipo lógico
Preferir **MUX combinacional em árvore** a um barramento interno com vários drivers tri-state. Cada saída da árvore é exclusiva por construção. Oito fontes de 8 bits são selecionadas em 3 níveis (4 + 2 + 1 multiplexadores de 8 bits = 7 unidades, cada uma feita com **2 × 74HC157**, total **14 CIs**):

| Seleção | Fonte de DB | Condição |
|---|---|---|
| 000 | A | saída de registrador |
| 001 | B | saída de registrador |
| 010 | ALU | saída combinacional estabilizada |
| 011 | MEM | buffer de leitura da memória, isolado e válido |
| 100 | MDR | saída de registrador |
| 101 | TMP | saída de registrador |
| 110 | ADDR_BYTE | seleção auxiliar de PC_LO/HI, SP_LO/HI, EA_LO/HI |
| 111 | CONST | constantes/entrada de dados ainda a detalhar |

`ADDR_BYTE` precisa selecionar seis bytes distintos. Uma segunda árvore 8:1, com duas entradas reservadas em zero, exige mais **14 × 74HC157** se implementada literalmente. Assim, **28 CIs 74HC157** são necessários *apenas para esses dois caminhos*, além dos oito 74HC157 já propostos para o MAR na Rev. 3.7. Isso é grande e merece otimização, não deve virar BOM definitiva.

## Correção importante
O multiplexador **não** garante que a memória externa esteja isolada: a saída `MEM` precisa vir de uma interface cuja direção e habilitação sejam corretas. Tampouco garante ausência de glitches durante troca dos seletores; **nunca** usar saída de mux ou ROM assíncrona diretamente como `/WE` ou clock. Capturas e escritas somente depois de propagação e setup comprovados.

## Sinais provisórios
- `DB_SEL[2:0]`: fonte principal.
- `AB_SEL[2:0]`: seleção do byte de endereço (6 e 7 proibidos em microcódigo).
- `REG_LOAD_*`: enables individuais, estáveis antes da borda de clock.
- `MEM_READ_VALID`: condição de uso da fonte MEM, com /OE e tempos confirmados.
- `MEM_WRITE_SETUP/PULSE/HOLD/RELEASE`: sequência já modelada na Rev. 3.5.

## Teste executado
`isa1_rev38_bus.py` compara todas as seleções da árvore com os valores esperados, inclusive valores aleatórios, e testa captura/retenção abstrata de registradores. Resultado em `isa1_rev38_results.json`. Os testes **não** demonstram que os 19 opcodes tenham caminhos completos nem verificam chips reais.

## Bloqueios para Rev. 3.9
1. Construir matriz **cada microoperação → origem DB → destino → seleção** e detectar fontes ausentes (por exemplo IR, TPH, bytes de retorno, imediatos).
2. Reduzir custo do mux: avaliar 74HC151 (8:1, um por bit) com disponibilidade/pinagem/temporização, ou buffers tri-state com exclusividade física e transição segura.
3. Definir interface da RAM: barramento bidirecional externo e separação CPU/VRAM/ZIF; impedir contenção na troca READ↔WRITE.
4. Definir exatamente as constantes e a rota de entrada de teclado/IO, sem substituir silenciosamente uma fonte necessária.
5. Validar part numbers, pinagem e tempos nas fichas oficiais antes do KiCad.

**Conclusão:** topologia testável e sem múltiplos drivers no DB interno por construção, mas **ainda não é um barramento de CPU completo**.
