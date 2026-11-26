# ISA-1 — Revisão 3.5 — Expansão conservadora de ciclos de memória

**Estado: modelo intermediário, não microcódigo binário nem circuito validado.**

## Base
A revisão 3.4 escolheu famílias candidatas de CIs. Esta revisão lê diretamente `isa1_rev33_microcode.json` e expande os passos simbólicos em fases de acesso à memória.

## Regra de expansão
- FETCH: ADDRESS_CAPTURE (MAR recebe PC).
- READ: READ_ACCESS (OE ativo), READ_CAPTURE (captura em registrador), READ_RELEASE (OE inativo).
- WRITE: WRITE_SETUP (driver de dados ativo), WRITE_PULSE (WE ativo), WRITE_HOLD (WE inativo com driver mantido), WRITE_RELEASE (driver desligado).
- INTERNAL: mantém uma etapa simbólica, ainda sem multiplexação de fontes e destinos.

O sinal lógico `mem_oe` representa **saída habilitada**, e `mem_we` representa **escrita habilitada**, portanto NÃO é a polaridade elétrica dos pinos `/OE` e `/WE`.

## Resultado executado
19 instruções, 183 estados expandidos, maior instrução com 25 estados, nenhuma violação das regras estáticas codificadas. O verificador detecta leitura e escrita simultâneas, escrita sem driver, captura sem leitura e falta de setup/hold textual. **Não comprova que o circuito real é livre de contenção.**

## Correção arquitetural importante
Não ligar saída permanente do SN74HC377 diretamente ao barramento comum; escolher uma topologia com multiplexação ou buffers tri-state. Os registradores de endereço e dados precisam de fontes físicas explícitas. A ROM assíncrona não pode comandar `/WE` diretamente sem sincronização ou intertravamento. Na CPU, os sinais `MAR_LOAD`, `PC_LOAD`, `SP_LOAD`, `ALU_OP`, `REG_LOAD`, `MEM_READ`, `MEM_WRITE` devem ser gerados por estados registrados.

## Bloqueios para a revisão 3.6
1. Definir quais registros de 16 bits têm incrementadores/decrementadores próprios ou compartilham a ALU.
2. Expandir as operações INTERNAL em microtransferências fisicamente executáveis; confirmar CALL/RET.
3. Desenhar fontes e destinos com muxes/tri-state, fanout e níveis lógicos.
4. Selecionar componente exato de ROM de microcódigo, largura e profundidade, e programador de bootstrap.
5. Construir uma simulação digital independente com estados de transição, reset e sinais de memória.
6. Confirmar pinagens, timing e alimentação nas fichas técnicas antes do esquemático final.
7. Integrar vídeo RCA, teclado, SRAM, firmware e gravador ZIF, depois ERC/DRC e protótipo.

## Reprodução
`python3 isa1_rev35_control_audit.py` gera `isa1_rev35_states.json` e `isa1_rev35_results.json`.
