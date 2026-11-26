# ISA-1 — Revisão 3.1: contrato executável da CPU e auditoria de integração
Data: 2026-11-23
Estado: **modelo comportamental de referência testado; CPU física e circuito completo não aprovados**.

## Base efetivamente inspecionada
- `ISA-1_REV30_INTERFACE_ZIF_AUDITORIA.md`: interface ZIF ainda sem exclusão física do barramento, supervisor e temporização.
- `isa1_rev07_emulator.py` e `isa1_rev09_model.py`: mapa de memória e ISA provisória de software.
- `ISA-1_REV18_RELATORIO.md`: seleção de caminhos de dados ainda candidata, sem netlist.

## Contrato provisório de ISA (ainda não congelado para hardware)
- Dados de 8 bits; PC, SP e X de 16 bits; registradores A e B de 8 bits; flags Z e C.
- Bytes de endereços imediatos em ordem little-endian.
- 1 byte: NOP 00, ADD 20, SUB 21, AND 22, OR 23, XOR 24, SHL 25, SHR 26, LDA[X] 33, STA[X] 34, INX 35, DEX 36, RET 51, PUSH A 52, POP A 53, CMP 54, HALT FF.
- 2 bytes: LDA #imm 10, LDB #imm 11.
- 3 bytes: LDA abs 30, STA abs 31, LDX #imm16 32, JMP abs 40, JZ abs 41, JNZ abs 42, CALL abs 50.
- CALL empilha primeiro byte alto, depois baixo; RET desempilha baixo, depois alto. Pilha decresce na SRAM, SP inicial BFFFh.
- Z é atualizado nas operações que alteram A, e por CMP; C é atualizado por ADD, SUB, SHL, SHR e CMP; operações lógicas preservam C no modelo atual. SUB/CMP: C=1 significa **sem empréstimo**.
- As instruções não definem ainda interrupções, I/O dedicado, instruções de acesso direto ao SP ou manipulação de flags; esses pontos são bloqueadores de firmware completo.

## Teste reproduzível
`python3 isa1_rev31_cpu_regression.py` -> `isa1_rev31_results.json`.
- 1.015.818 verificações comportamentais, incluindo combinações exaustivas A/B em ADD, SUB, AND, OR, XOR e CMP; verificações de Z e C; memória ROM imutável; escrita em RAM e VRAM; CALL aninhado; branches tomados/não tomados; mapeamento de todos os 32768 endereços RAM.
- Oráculo aritmético independente usa operações inteiras do Python, mas execução das instruções ainda usa o mesmo emulador; isso **não** é verificação independente de microcódigo, de portas ou de pinos.
- O teste não mede ciclos, clock, tempo de setup/hold, carga capacitiva, glitches ou tensão.

## Inconsistências de arquitetura a resolver antes de esquemático
1. O modelo anterior de vídeo usa 256×192 pixels **monocromáticos**, 1 bit/pixel e 6144 bytes de VRAM. **Não comprova nem implementa RCA colorido**. Uma placa de vídeo colorida independente exigirá nova definição de pixels, VRAM, temporização e encoder CVBS.
2. O formato removível reserva 30.656 bytes para código/recursos, mas a SRAM de 32 KB também precisa comportar pilha, variáveis e firmware em execução se a CPU não puder executar código de ROM ou de outra região. Não presumir que qualquer imagem de 30.656 bytes carregará e executará sem layout de RAM e relocação.
3. O emulador mapeia ROM 0000–3FFF, RAM 4000–BFFF, VRAM C000–DFFF, I/O E000–E0FF; o gravador ZIF dedicado não possui ainda registradores de I/O definidos, nem mecanismo formal de chamadas de sistema.
4. Não foi definido o modo de bootstrap nem o conjunto mínimo de instruções para editor, assembler, BASIC e chamadas de sistema.
5. A regra de leitura/escrita dos dois 74HC244 ainda depende de um sinal externo `cpu_driver_en` cuja geração real não foi implementada. Os 74HC377 não têm reset; suas saídas precisam permanecer isoladas até inicialização comprovada.
6. Sequência SDP da EEPROM e escrita por byte precisam de confirmação de datasheet e de controle físico para não permitir acesso indevido ao código.

## Decisões propostas para Rev 3.2
- Congelar **primeiro** o contrato de instruções, mapa de memória e mapa de I/O, depois decompor cada instrução em microoperações verificáveis.
- Priorizar protótipo digital de CPU+ROM+SRAM+UART/diagnóstico opcional; integrar vídeo e teclado após validação do clock e do reset, sem abandonar o objetivo de placa única.
- Definir microsequenciador registrado, drivers de barramento e seleção de registradores, gerar tabela de sinais por microestado e testes de exclusão temporal.
- Manter a produção da PCB bloqueada até existir netlist completa, ERC/DRC, orçamento de temporização e plano de teste de bancada.

## Referência técnica
Gigatron permanece referência de organização de datapath e fases de memória, não prova de que a ISA-1 terá mesma frequência ou quantidade de chips.
