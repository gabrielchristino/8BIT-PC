# ISA-1 — Revisão 5.7 — Integração de EA/RET e teste de CALL/RET

## Objetivo
Retomar o datapath do PC após a decisão de alimentação da revisão 5.6. Testar a preservação do endereço de retorno durante CALL e o desempilhamento durante RET, além de examinar uma otimização de multiplexadores sem comprometer recursos da CPU.

## Arquitetura candidata mantida
- PC: 4 × SN74HC163D, 16 bits, clock comum e carga paralela síncrona.
- EA: 2 × SN74HC377D, 16 bits de endereço efetivo/destino.
- RET: 2 × SN74HC377D, 16 bits de endereço recuperado da pilha.
- Seleção EA/RET para PC: 4 × SN74HC157D (16 canais 2:1).
- `PC_SEL_RET=0`: seleciona EA; `PC_SEL_RET=1`: seleciona RET.
- `PC_LOAD_N_SAFE` e `PC_COUNT_SAFE` permanecem condicionados a `CPU_RUN`, conforme Rev. 5.2.
- As entradas de EA e RET, os enables de carga dos 74HC377 e as fontes de dados de 8 bits ainda precisam ser ligadas ao barramento real.

## Contrato de CALL
1. Após decodificar o operando, `PC` aponta para a próxima instrução (endereço de retorno).
2. Capturar destino em `EA` antes de sobrescrever o endereço efetivo com acessos à pilha.
3. Empilhar byte alto do PC e depois byte baixo, com SP decrementando antes de cada escrita. Isso é uma **convenção proposta**, ainda a reconciliar com a ISA formal.
4. Carregar PC a partir de EA usando `PC_SEL_RET=0` e `PC_LOAD_N_SAFE=0` na borda apropriada.

## Contrato de RET
1. Desempilhar byte baixo e depois alto, incrementando SP após cada leitura.
2. Formar `RET[15:0]` e carregar os dois HC377 em borda válida, sem habilitar escrita de memória.
3. Carregar PC de RET com `PC_SEL_RET=1` e `PC_LOAD_N_SAFE=0`.

## Comparação de otimização
**Proposta A (atual):** EA 2×377, RET 2×377 e quatro HC157 de seleção direta, além dos contadores.

**Proposta B (registrador TARGET):** transferir EA ou RET para um terceiro registrador de 16 bits antes da carga do PC. Isso acrescenta dois HC377 e ainda exige uma rota de seleção de dados ou lógica de transferência. **Não há economia comprovada de CIs**, e o ciclo extra introduz risco de sobrescrever EA antes da transferência. Portanto, **manter os quatro HC157** por enquanto. Um barramento compartilhado ou reutilização do MAR só poderá ser considerado após a definição das fontes/consumidores e da temporização completa.

## Testes executados
`python3 isa1_rev57_call_ret.py`:
- 65.536 valores possíveis de endereço de retorno em CALL/RET.
- 128 sequências pseudoaleatórias com 32 níveis de chamadas aninhadas e retornos, comparando duas arquiteturas comportamentais.
- Pilha implementada como 65.536 bytes endereçáveis no modelo, não como lista Python abstrata.
- Teste negativo de perda de destino quando EA é sobrescrito antes de transferir para TARGET.
- **159.873 verificações**, todas aprovadas no modelo executado.

## Limites e pendências
- O teste não implementa SRAM física, barramentos tri-state, sinais /OE e /WE, temporização de leitura/escrita ou arbitragem de vídeo.
- A convenção de empilhamento deve ser documentada como parte da ISA e confrontada com microcódigo/opcodes já definidos.
- Os 74HC377 não possuem reset próprio; seus valores não podem ser utilizados antes de carga válida.
- O modelo não é um ERC nem uma simulação de temporização elétrica.
- Próximo passo (5.8): mapear as fontes de dados de EA/RET, construir ciclos de microinstrução com SRAM de 8 bits e testar os sinais de barramento, inclusive casos de contenção e writes durante reset.

**Status:** integração comportamental CALL/RET aprovada no escopo descrito; conexão física EA/RET ainda pendente; não liberar PCB.
