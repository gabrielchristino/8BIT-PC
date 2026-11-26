# ISA-1 — Rev. 1.4 — Simulação funcional de blocos da CPU
Data: 2026-11-23

## Escopo realmente executado
Comando: `python3 isa1_rev14_logic_sim.py`.
Resultado: PASS em **786.432** casos exaustivos da ALU (ADD, ADC, SUB, SBC, AND, OR, XOR), seleção de barramento com detecção de contenção injetada, e **100.000** transições pseudoaleatórias determinísticas de registradores/flags.

### Semântica adotada apenas para o protótipo
- CPU de dados 8 bits; operandos A e B.
- ADD/ADC: Carry=1 quando a soma excede 255.
- SUB/SBC: Carry=1 significa *sem empréstimo*; SBC calcula A-B-(1-C).
- Zero=1 se o resultado de 8 bits for zero.
- AND/OR/XOR preservam Carry (decisão provisória de ISA).
- Modelo de caminho aritmético: dois somadores de 4 bits em cascata, funcionalmente equivalentes à função do 74HC283, com inversão de B para subtração.
- Modelo de barramento: quatro fontes hipotéticas A, B, ALU e RAM; seleção one-hot, uma fonte por vez.

## O que foi comprovado
As equações de aritmética e a convenção das flags são consistentes com uma implementação por dois somadores de 4 bits em cascata. Um verificador funcional identifica uma condição deliberada de duas saídas ativas no mesmo barramento.

## O que NÃO foi comprovado
Não há circuito real de CIs com pinos, não há esquema KiCad, modelos temporais de fabricante, Verilog em simulador HDL, SPICE, avaliação de fan-out, tempos de setup/hold, alimentação, clock, reset assíncrono, SRAM, ROM, vídeo ou placa pronta para fabricação. O teste de contenção verifica o *detector*, não prova que um futuro decodificador físico seja seguro. A seleção e a quantidade de CIs ainda estão abertas.

## Próxima entrega técnica
1. Definir a especificação mínima das instruções, registradores, ciclos e flags, com casos de borda.
2. Desenhar um bloco real por CI e pino, incluindo /OE, /WE, /CS, clock e reset.
3. Escolher códigos de peça e encapsulamentos SOIC com datasheets, extrair limites temporais e orçar o caminho crítico.
4. Modelar transições de controle e testes de conflito entre saídas, inclusive durante reset.
5. Somente então integrar memória e periféricos; revisar ERC/DRC antes de cotar PCB.

## Política de aprovação
**Estado: protótipo lógico aprovado somente no escopo acima; hardware não validado.**
