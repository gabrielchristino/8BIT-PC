# ISA-1 — Revisão 1.9 — Primeira pinagem real e testes
Data: 2026-11-23. Status: **subsistema candidato; não pronto para PCB**.

## Escopo
Primeiro bloco com pinagem real: U1 registrador SN74HC574 (SOIC-20/DW), U2 e U3 multiplexadores SN74HC157 (SOIC-16/D), U4 transceptor SN74HC245 (SOIC-20/DW). O script associado confere a integridade das tabelas e exercita a lógica de seleção; **não** gera netlist elétrico nem prova os tempos do circuito.

Fontes primárias: https://www.ti.com/lit/ds/symlink/sn74hc574.pdf ; https://www.ti.com/lit/ds/symlink/sn74hc157.pdf ; https://www.ti.com/lit/ds/symlink/sn74hc245.pdf . Conferir a revisão do datasheet e o código exato de compra antes de fixar footprints.

## U1 SN74HC574 — SOIC-20, vista superior
|Pino|Sinal|Pino|Sinal|
|---:|---|---:|---|
|1|/OE|20|VCC|
|2|D0|19|Q0|
|3|D1|18|Q1|
|4|D2|17|Q2|
|5|D3|16|Q3|
|6|D4|15|Q4|
|7|D5|14|Q5|
|8|D6|13|Q6|
|9|D7|12|Q7|
|10|GND|11|CLK|

**Atenção:** /OE só desabilita saídas; não apaga o conteúdo. O 574 não possui pino de reset assíncrono. Se o projeto exigir reset físico de registradores, selecionar outro CI ou implementar inicialização por sequenciamento de carga. As saídas Q alimentam entradas de multiplexadores, sem disputar um barramento compartilhado.

## U2/U3 SN74HC157 — SOIC-16, vista superior
|Pino|Sinal|Pino|Sinal|
|---:|---|---:|---|
|1|SEL|16|VCC|
|2|1A|15|/G|
|3|1B|14|4A|
|4|1Y|13|4B|
|5|2A|12|4Y|
|6|2B|11|3A|
|7|2Y|10|3B|
|8|GND|9|3Y|

U2 canais 1..4 correspondem a bits 0..3; U3 canais 1..4 correspondem a bits 4..7. SEL=0 seleciona A; SEL=1 seleciona B; /G=1 força Y=0 (NÃO alta impedância). Ligações candidatas: A[7:0] e B[7:0] para os dois grupos de entradas, Y[7:0] para uma das entradas da ALU. O segundo operando, funções lógicas e carry ainda precisam de circuitos próprios.

## U4 SN74HC245 — SOIC-20, vista superior
|Pino|Sinal|Pino|Sinal|
|---:|---|---:|---|
|1|DIR|20|VCC|
|2|A0|19|/OE|
|3|A1|18|B0|
|4|A2|17|B1|
|5|A3|16|B2|
|6|A4|15|B3|
|7|A5|14|B4|
|8|A6|13|B5|
|9|A7|12|B6|
|10|GND|11|B7|

DIR=1: A→B; DIR=0: B→A; /OE=1: isolado. Proposta: lado A para barramento CPU, lado B para dados SRAM. Durante leitura, **não** habilitar U4 no sentido A→B enquanto SRAM fornece dados. Durante escrita, primeiro desabilitar SRAM /OE, preparar DIR e dados, depois habilitar U4 e emitir /WE com setup/hold apropriados. Os sinais e a SRAM exata ainda não foram escolhidos.

## Temporização preliminar
Datasheet TI SN74HC245, CL=50pF, VCC=4.5V: tdis máximo na faixa comercial -40..85 °C de **50 ns**; ten máximo de **58 ns**. Não há valor mínimo de ten nessa tabela para provar segurança em comutação simultânea. Um intervalo de guarda de **80 ns após /OE de desabilitação efetivamente aplicado** dá margem aritmética de 30 ns **somente para esse CI e essas condições**. É uma hipótese de engenharia, NÃO valor final do ISA-1. É preciso adicionar atrasos da lógica de controle, skew, capacitância real, saída da SRAM, tempos de setup/hold e variações de temperatura/alimentação. Não se deve inferir clock máximo desses números isoladamente.

## Testes executados
`python3 isa1_rev19_pincheck.py`:
- 72 posições de pinagem em quatro encapsulamentos conferidas quanto à cobertura e unicidade, com checagens de pinos-chave;
- 262.144 combinações de A/B, seleção e habilitação lógica dos dois 74HC157 verificadas contra tabela funcional;
- 16 combinações estáticas de controle examinadas para a condição de conflito definida no modelo;
- 80 ns − 50 ns = 30 ns de margem **ilustrativa** para desligamento do 245.

**Limitação dos testes:** os testes de multiplexação usam uma mesma especificação de referência e não constituem validação independente por portas; não há simulação de propagação real, SPICE, Verilog, nem validação da SRAM. O script verifica apenas uma parte da interface, não a CPU inteira. A escolha do registrador 574 com reset por firmware é uma questão aberta, não aprovada.

## Riscos ainda abertos
1. Escolher registradores com reset real ou circuito de inicialização confiável.
2. Definir 2º operando da ALU, somador, lógica, flags, PC, SP, instruções e sequenciador.
3. Selecionar SRAM/ROM/EEPROM concretas e conferir pinagens, tempos e decodificação.
4. Desenhar esquema KiCad real com alimentação, desacoplamento, pull-ups, conectores, ERC e revisão de footprints.
5. Simular ou medir controle de /OE, /WE e direção com atrasos de todos os componentes.
6. Só liberar fabricação após revisão elétrica, de temporização e protótipo.

## Decisão Rev. 1.9
Arquitetura candidata: seleção interna por multiplexadores + isolamento da SRAM por transceptor controlado. **Não congelar lista de CIs nem footprint ainda**. CPU ISA-1 permanece própria e completa; PCB principal única e SMD preferencialmente SOIC.
