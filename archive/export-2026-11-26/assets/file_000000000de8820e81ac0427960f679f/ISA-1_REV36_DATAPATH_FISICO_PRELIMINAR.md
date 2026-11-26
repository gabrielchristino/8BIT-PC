# ISA-1 — Revisão 3.6 — Datapath físico preliminar

**Status: arquitetura candidata e testes de invariantes; NÃO é esquemático, netlist, pinagem validada nem PCB.**

## Fontes inspecionadas
`ISA-1_REV33_MICROOPERACOES.md`, `isa1_rev33_microcode.json`, `ISA-1_REV34_SELECAO_CIS_CPU.md`, `ISA-1_REV35_CONTROLE_BARRAMENTOS.md`.

## Decisões desta revisão
1. **Barramento interno DB[7:0]** com exatamente um driver habilitado por microestado. Q dos 74HC377 não pode ligar diretamente ao DB: cada origem exige buffer tri-state (74HC244) ou seleção por multiplexadores; um único 74HC244 oferece oito canais, mas seus dois grupos de quatro têm habilitações próprias. Contar buffers por fonte e grupos antes de comprar.
2. **Registradores A/B/TMP/TPH/MDR/IR**: candidatos 74HC377, com carga por /CLKEN, desde que cada origem e destino tenha conexão física. Registradores sem reset exigem inicialização explícita antes de habilitar leitura de seus valores.
3. **PC e SP de 16 bits**: pares de 74HC377, mais caminho de carga e caminho aritmético selecionados por multiplexadores 74HC157. A atualização de PC/SP não pode depender de clocks derivados por portas combinacionais.
4. **Incremento PC**: candidato circuito combinacional dedicado de 16 bits com quatro 74HC283; **incremento/decremento SP**: circuito dedicado com controle de sentido, ainda sem implementação fechada. Essa é uma escolha de baixa complexidade de microcódigo, mas de maior custo de CIs; deve ser comparada com ALU compartilhada. Quatro 74HC283 por operação de 16 bits são apenas estimativa de somadores, não BOM final.
5. **MAR[15:0]**: dois registradores de 8 bits; fontes PC, SP e EA por seleção 3:1 (por exemplo cascata de 74HC157). Uma única fonte selecionada e estável antes de /OE ou /WE.
6. **EA[15:0]**: registradores dedicados para preservar destino de CALL durante gravações na pilha. RETADDR pode ser eliminado se PC for mantido estável durante os dois pushes; para simplificar a primeira implementação, manter RETADDR como candidato até provar os ciclos.
7. **ALU**: somadores 74HC283 e lógica 74HC86/08/32, seleção por multiplexadores. Carry de SUB deve significar ausência de empréstimo; SHL/SHR exigem circuitos e flags específicos.
8. **Saída de controle**: /WE de RAM e EEPROM não será comandado diretamente por ROM assíncrona. Exige sequenciador registrado, qualificação de endereço, reset e intertravamento.

## Diagrama de blocos textual
```
  PC[15:0] ----+                 +---> MAR[15:0] ---> decode ---> memória
  SP[15:0] ----+--> mux MAR ----+
  EA[15:0] ----+

  MEM ----[isolamento]----+
  A/B/TMP/TPH/MDR/EA/PC/SP --[buffers/mux]--> DB[7:0] --> registradores
  A,B --> ALU --> [mux/isolamento]---------------------------^

  PC --> incrementador16 --> mux carga PC --> PC
  SP --> inc/dec16 -------> mux carga SP --> SP
```

## CALL e RET — restrição obrigatória
- CALL: buscar destino 16 bits em EA; capturar retorno de PC ou mantê-lo estável; gravar byte alto em MEM[SP], decrementar SP; gravar byte baixo em MEM[SP], decrementar SP; carregar PC de EA. Cada escrita tem SETUP/PULSE/HOLD/RELEASE e SP só muda depois da fase de retenção.
- RET: incrementar SP, ler byte baixo; incrementar SP, ler byte alto; carregar PC; EA não deve ser corrompido durante CALL.
- O modelo Python percorreu 60 cenários de CALL/RET e todos os 65.536 valores de incremento/decremento de 16 bits. **Isso não valida que os CIs implementam esses caminhos.**

## Bloqueios objetivos antes de esquemático pin-to-pin
1. Especificar cada bit de cada mux e de cada buffer, sua habilitação e driver; conferir orçamento de CIs e fanout.
2. Implementar microsequenciador e microcódigo binário que realize todos os 19 opcodes; comparar por execução independente com emulador.
3. Definir fonte de reset e clock, tensões, margens de temporização e os exatos part numbers/encapsulamentos usando datasheets.
4. Fechar ROM/RAM/IO, controlador ZIF, vídeo composto em cores e teclado; executar ERC/DRC em KiCad.
5. Confirmar proteção contra escrita em EEPROM e comandos SDP com datasheet e hardware de teste.

## Reprodução
`python3 isa1_rev36_datapath.py` gera `isa1_rev36_results.json`. Verifica exclusividade abstrata de fontes, um conflito injetado, aritmética 16 bits e preservação de retorno no fluxo de pilha. Não verifica tempos elétricos, pinagem, firmware ou placa.
