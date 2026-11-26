# ISA-1 — Revisão 3.2 — Primeiro contrato de microciclos de memória

**Estado:** investigação arquitetural. NÃO é esquemático completo, simulação de portas, netlist ou placa fabricável.

## Evidência examinada
- `ISA-1_REV31_CPU_CONTRATO_E_REGRESSAO.md` define a ISA provisória e lacunas.
- `isa1_rev07_emulator.py` é a implementação de referência efetivamente executada.
- O relatório 3.1 menciona opcodes 32, 33, 34, 35, 36, 42 e 54, mas **o emulador rev07 não os implementa**. A presente regressão cobre somente a interseção implementada e não congela esses opcodes.

## Resultado reproduzível
`python3 isa1_rev32_microcycles.py` executa casos aleatórios determinísticos de uma instrução comparando estado e memória entre o emulador original e um segundo executor que registra explicitamente transações READ/WRITE. O resultado está em `isa1_rev32_results.json`. O teste não prova independência completa dos modelos: ambos derivam da mesma especificação comportamental e não modelam os sinais de chip enable, setup/hold ou atrasos.

## Contrato provisório de acesso
1. O PC fornece o endereço para busca de opcode; READ entrega um byte e só depois o PC avança.
2. Operandos imediatos são buscados em microciclos READ separados.
3. Instruções de leitura de RAM fazem READ adicional após compor endereço de 16 bits.
4. Escritas e PUSH usam WRITE com endereço e dados estabilizados antes do pulso /WE.
5. POP/RET fazem READ e atualizam SP na ordem definida pela ISA.
6. Nenhuma transação abstrata é simultaneamente READ e WRITE. **A exclusão física de drivers permanece não implementada**.

## Bloqueadores para esquemático
- Resolver discrepância entre conjunto de instruções relatado e emulador de referência.
- Selecionar ALU e datapath com contagem real de portas, registradores e multiplexadores.
- Definir controle registrado, reset, estados de barramento, decodificação ROM/SRAM/VRAM/I/O e interrupções.
- Projetar vídeo CVBS colorido real, VRAM e arbitragem.
- Completar teclado, ZIF/SDP, fonte, supervisão e conectores.
- Gerar esquemático elétrico e netlist, executar ERC/DRC e análise de temporização antes de encomendar PCB.

## Próximo entregável verificável
Uma tabela de microoperações por opcode **congelado**, com origem/destino, habilitações mutuamente exclusivas e temporização; somente depois converter em pinagem de componentes específicos.
