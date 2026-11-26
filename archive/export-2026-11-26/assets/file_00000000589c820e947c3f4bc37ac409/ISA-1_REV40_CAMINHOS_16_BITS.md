# ISA-1 — Revisão 4.0 — PC, SP, EA e seleção de circuitos

**Status: contrato de datapath e testes comportamentais; não é esquemático elétrico nem liberação para PCB.**

## Base auditada
Foram consultados os relatórios Rev. 3.6, 3.7 e 3.9 e o arquivo de 19 instruções/101 microetapas da Rev. 3.3. A Rev. 3.9 registra sete classes de rotas faltantes; esta revisão trata especificamente de PC/SP/EA/MAR e da pilha.

## Escolha de arquitetura
**Para o primeiro circuito: incrementador dedicado PC+1 e caminho dedicado SP±1**, com seleção de carga para PC, SP, EA e MAR. A opção de reutilizar a ALU de 8 bits pode reduzir portas aritméticas, mas exige transferências de bytes, carry intermediário e mais microciclos, além de aumentar a pressão sobre DB. Ainda não foi feita comparação elétrica de área/custo/atraso; portanto a escolha é por menor risco de integração, não por alegada otimização absoluta.

### Contratos de carga
| Destino | Fontes necessárias | Observação |
|---|---|---|
| PC[15:0] | PC+1, EA, endereço montado por RET | PC deve capturar os 16 bits na mesma borda lógica |
| SP[15:0] | SP+1, SP−1 | atualização somente após memória liberar leitura/escrita |
| EA[15:0] | TMP:TPH | preservar durante pushes de CALL |
| MAR[15:0] | PC, SP, EA | mux 3:1 da Rev. 3.7, carga antes do acesso |
| MDR[7:0] | MEM, PC_LO, PC_HI, A, TMP | rotas de PC_LO/HI são indispensáveis em CALL |

O caminho `RET_TMP -> PC` deve ter dois bytes retidos até a carga atômica de PC. **Não confundir `TPH:TMP` (endereço de destino) com os bytes temporários de RET**: se reutilizados, a sequência de microcódigo deve comprovar que não há sobrescrita prematura.

## Sequência obrigatória CALL/RET
- CALL: buscar endereço imediato em EA; PC já aponta para a próxima instrução; selecionar PC_HI para MDR, MAR=SP, executar SETUP/PULSE/HOLD/RELEASE, então SP--. Repetir para PC_LO; então PC=EA.
- RET: SP++, MAR=SP, ler byte baixo em temporário; SP++, MAR=SP, ler byte alto em temporário; PC recebe par formado pelos temporários.
- Endereços e dados devem permanecer estáveis durante a janela de memória; sinais /WE e /OE não podem vir diretamente de ROM assíncrona.
- Atenção: se o espaço de pilha atravessar RAM/ROM/I/O, o contrato arquitetural sozinho não impede corrupção; o mapa e proteção ainda precisam ser fechados.

## Comparação preliminar de CIs
| Função | Alternativa | Avaliação |
|---|---|---|
| PC+1 16-bit | cadeia de 74HC283 (4 somadores de 4 bits) | candidata simples, não otimizada |
| PC+1 16-bit | lógica de incremento dedicada por XOR/AND de propagação | potencialmente menos portas, mas exige análise de fanout e atraso |
| SP±1 16-bit | 74HC283 + lógica de seleção de incremento/decremento | candidata, circuito detalhado ainda pendente |
| PC/SP via ALU 8-bit | ALU compartilhada + temporários | menos lógica aritmética potencial, mais microciclos e caminhos |
| MUX MAR 3:1 | 8 × 74HC157 (Rev. 3.7) | mantém-se candidato; pinagem não aprovada |
| MUX PC 3:1 | 8 × 74HC157 (duas camadas de 16 bits) | estimativa topológica, não BOM fechada |

**Correção de interpretação:** o 74HC151 não substitui automaticamente os multiplexadores de 16 bits. Cada HC151 fornece um único bit e não oferece saída tri-state. Para três fontes de 16 bits, o 74HC157 em duas camadas é uma opção direta, mas ainda pode ser otimizado.

## Testes reproduzíveis
`python3 isa1_rev40_address_paths.py` executou 131.072 verificações (incremento e decremento em todos os valores de 16 bits) e 50.000 ciclos abstratos CALL/RET com wrap-around de SP. Verificou também a presença de caminhos declarados para CALL/RET/JMP/JZ. O teste **não** executa os microestados reais da Rev. 3.5, não verifica temporização, não instancia portas, não compara alternativas de BOM nem comprova proteção de escrita.

## Bloqueios para Rev. 4.1
1. Conectar os registradores PC/SP/EA/MAR e temporários aos MUX de carga com pinos e habilitações específicos.
2. Resolver os temporários de RET e os bytes PC_LO/PC_HI para MDR; conferir a ordem de carga.
3. Gerar microcódigo binário e executar em simulador de ciclos independente; só então afirmar cobertura de todas as instruções.
4. Verificar part numbers, níveis de tensão, tempos máximos, fanout e reset em datasheets antes do KiCad.
5. Auditar mapa de memória e limites de pilha, inclusive a interface de EEPROM ZIF.

## Veredito
**Arquitetura de caminhos 16-bit aceita como candidata para detalhamento. Não está aprovada eletricamente nem pronta para fabricar.**
