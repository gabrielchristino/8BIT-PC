# ISA-1 — Revisão 3.7 — MUX físico de endereços para MAR

**Status:** proposta de conectividade lógica testada; não é pinagem de encapsulamento, esquemático elétrico, BOM final nem PCB fabricável.

## Base
Revisões 3.3–3.6: PC, SP, EA e MAR de 16 bits; durante CALL, EA guarda o destino enquanto MAR aponta para SP. Os arquivos anteriores foram consultados antes desta revisão.

## Decisão construtiva
Implementar a escolha entre **PC, SP e EA** com **oito 74HC157** (quatro multiplexadores de 4 bits no primeiro estágio e quatro no segundo) e **dois 74HC377** para MAR[15:0].

- Estágio 1: MUX1[i] = MUX_S1 ? SP[i] : PC[i].
- Estágio 2: MUX2[i] = MUX_S2 ? EA[i] : MUX1[i].
- Entradas `/E` dos oito 74HC157 em nível ativo (baixo), **desde que** confirmado na variante escolhida. Saídas dos multiplexadores dirigem apenas as entradas D do MAR, não o barramento DB.
- MAR_LO D[7:0] recebe MUX2[7:0]; MAR_HI D[7:0] recebe MUX2[15:8]. Os dois registradores compartilham MAR_LOAD como habilitação de captura e o mesmo clock registrado. A habilitação é ativa em nível baixo no 74HC377; a polaridade deve ser convertida corretamente.
- MAR tem saídas Q permanentes e **não possui reset**. Memórias precisam ficar desabilitadas até que MAR tenha sido inicializado e o reset liberado de forma segura.

### Seleção

| MUX_S2 | MUX_S1 | Fonte de MAR |
|---|---|---|
| 0 | 0 | PC |
| 0 | 1 | SP |
| 1 | 0 | EA |
| 1 | 1 | EA (alias; reservar como estado inválido no controle) |

### Lista lógica de conexões
`isa1_rev37_mar_mux_nets.json` contém **32 canais**, com identificador do CI, canal, entrada A, entrada B, saída, seleção e habilitação. É uma *netlist lógica*; faltam os números de pino do part number definitivo. A topologia elimina disputa entre PC/SP/EA na entrada de MAR porque os multiplexadores são push-pull, com somente uma saída por bit.

### Validação executada
`isa1_rev37_mar_mux.py` realizou 400.000 verificações aleatórias de seleção (incluindo alias) e 10.000 verificações de carga/retenção do registrador abstrato. Nenhuma falha. **Não** verificou propagação, setup/hold, fanout, integridade de alimentação, pinagem ou funcionamento dos chips.

## Questões descobertas / não resolvidas
1. **Custo de multiplexação:** só este caminho consome oito 74HC157; a CPU ainda precisa de seleção de dados e de fontes para PC/SP/EA. É possível reduzir o número com outra topologia, mas não substituir sem verificar todas as instruções.
2. **Clock e /CLKEN:** o controle MAR_LOAD deve estar estável antes da borda ativa. Não derivar clock com portas combinacionais.
3. **Endereço durante READ/WRITE:** MAR não pode mudar enquanto /OE ou /WE estiver ativo. O sequenciador deve impor intertravamento e margens temporais.
4. **Inicialização:** sem reset no HC377, os chip selects e /WE devem permanecer inativos durante a partida, independentemente de MAR.
5. **CALL:** endereço EA não deve ser modificado durante os pushes; o teste de equivalência funcional ainda precisa integrar microcódigo binário, RAM e flags.
6. **Escolha de fabricante/encapsulamento:** verificar pinos reais, tensão, velocidade e disponibilidade em fichas técnicas oficiais antes do desenho KiCad.

## Próximo bloco
Fechar a rede de seleção de fontes do barramento de dados DB[7:0] com contagem de drivers e conexões por bit; depois fechar incrementadores de PC/SP e microsequenciador, antes de emitir netlist física.
