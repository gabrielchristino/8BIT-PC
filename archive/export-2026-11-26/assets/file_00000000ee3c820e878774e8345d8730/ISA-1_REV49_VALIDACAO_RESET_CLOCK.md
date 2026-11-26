# ISA-1 — Revisão 4.9 — Validação do reset e liberação de clock

## Continuidade e correção da Rev 4.8
Fonte inspecionada: `ISA-1_REV48_RESET_CLOCK_CONTRATO.md` e `isa1_rev48_reset_model.py`. A Rev 4.8 exigia uma borda de clock durante a condição de supervisor em reset. Isso criava uma dependência desnecessária: se o oscilador só se tornar válido após a liberação do supervisor, o modelo pode ficar permanentemente impedido de executar. **Correção:** manter o reset síncrono do PC ativo durante os primeiros ciclos de clock *após* a liberação do supervisor. Assim não dependemos de clocks durante o power-bad.

## Componentes candidatos confirmados parcialmente
- **TI SN74HC74D**, SOIC-14, dois flip-flops D por CI, clear e preset assíncronos ativos em nível baixo. Dois CIs oferecem três FFs para a sequência e um FF sobressalente. Pinagem (vista superior): 1=/1CLR, 2=1D, 3=1CLK, 4=/1PRE, 5=1Q, 6=/1Qbar, 7=GND, 8=/2Qbar, 9=2Q, 10=/2PRE, 11=2CLK, 12=2D, 13=/2CLR, 14=VCC. Referência oficial: https://www.ti.com/lit/ds/symlink/sn74hc74.pdf
- **TI TPS3808G50DBVR**, supervisor SOT-23-6, saída RESET open-drain, entrada MR, retardo configurável. **Candidato, NÃO aprovado para conexão**: confirmar pinos exatos, tolerância do limiar, tensão de pull-up, corrente de fuga, tempo mínimo de reset e comportamento na queda da alimentação a partir do datasheet completo. Referência oficial: https://www.ti.com/product/TPS3808/part-details/TPS3808G50DBVR
- Oscilador de 5 V: modelo e frequência ainda não selecionados. Não se deve alegar verificação temporal.

## Proposta lógica de conexões (não é netlist KiCad)
Todos os flip-flops de sequência compartilham `SYS_CLK` e `/CLR=SUP_RESET_N` (saída open-drain do supervisor com pull-up dimensionado). `/PRE` de cada flip-flop ligado a VCC. `FF1.D=1`, `FF2.D=FF1.Q`, `FF3.D=FF2.Q`. `PC_CLR_N=SUP_RESET_N AND FF2.Q`. `CPU_RUN=SUP_RESET_N AND FF3.Q`. `CPU_RUN` também deve bloquear habilitações do PC e do sequenciador; os sinais de escrita devem ser autorizados somente quando `CPU_RUN` estiver ativo e o decodificador estiver válido. **Não ligar /WE diretamente ao sinal combinacional sem uma análise de glitches e temporização.**

## Sequência de referência
| Evento | FF1 | FF2 | FF3 | PC | CPU_RUN |
|---|---:|---:|---:|---|---:|
| Supervisor em reset | 0 | 0 | 0 | desconhecido até uma borda | 0 |
| Supervisor liberado, sem clock | 0 | 0 | 0 | ainda desconhecido | 0 |
| Primeira borda | 1 | 0 | 0 | 0 | 0 |
| Segunda borda | 1 | 1 | 0 | 0 | 0 |
| Terceira borda | 1 | 1 | 1 | 0 (RUN antigo = 0) | 1 |
| Quarta borda | 1 | 1 | 1 | PC pode avançar | 1 |

A condição crítica é que o PC amostre os sinais *anteriores* à borda, como num circuito síncrono real. Durante brownout, `SUP_RESET_N` deve inibir RUN assincronamente, mesmo sem clock. A saída de reset do supervisor não garante segurança quando VCC está abaixo do mínimo especificado dos componentes: ainda falta comprovar a rede de proteção de /WE durante a rampa de tensão.

## Testes realmente executados
`python isa1_rev49_startup_verify.py`: 1.310.736 assertivas passaram. Percorreu os 65.536 valores iniciais do PC, ausência de clock durante reset, três bordas de liberação, quarta borda de execução, brownout sem clock, interrupção do startup e teste negativo de /WE. **É um modelo de eventos em Python**, não simulação gate-level de SN74HC74/163, nem SPICE.

## Pendências antes da PCB
1. Conferir pinagem/limiares completos do supervisor e selecionar pull-up e temporização CT.
2. Definir oscilador e validar a estabilidade antes da sequência de partida.
3. Calcular setup/hold, skew e caminhos de reset, sobretudo desassertar reset perto da borda de clock.
4. Proteger /WE de SRAM e EEPROM em toda a rampa, inclusive abaixo do VCC operacional do supervisor/74HC.
5. Implementar esquemático, ERC, modelo digital com temporizações e ensaios de brownout em bancada.

**Status: contrato de inicialização melhorado e verificado abstratamente. NÃO aprovado eletricamente; NÃO pronto para fabricar.**
