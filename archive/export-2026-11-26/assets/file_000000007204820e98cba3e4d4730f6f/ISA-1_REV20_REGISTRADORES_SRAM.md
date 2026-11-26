# ISA-1 — Revisão 2.0: reset, SRAM e controle de barramento
Data: 2026-11-23. **Estado: modelo lógico validado parcialmente; NÃO liberar PCB.**

## Decisões candidatas
- U1/U2 registradores com reset: Texas Instruments **SN74HC273DW** (SOIC-20). Pino 1 `/CLR`, 11 `CLK`, 10 GND, 20 VCC. Saídas Q push-pull **sem /OE**: ligá-las às entradas de multiplexadores, **nunca diretamente a um barramento multidriver**. Reset assíncrono zera saídas, mas a desativação do reset precisa ser sincronizada ao clock para evitar problemas de recuperação/remoção; clock deve ficar bloqueado de modo seguro durante power-on.
- U3 transceptor **SN74HC245DW** (SOIC-20): pino 1 DIR, 19 `/OE`, 10 GND, 20 VCC. Lado A = CPU, B = SRAM. DIR=0 para ler da SRAM; DIR=1 para escrever. Desabilitar `/OE` antes de mudar DIR e antes de permitir que a SRAM passe a dirigir o barramento.
- U4 SRAM **Alliance Memory AS6C62256-55SIN** (SOP-28, 32K×8, 55ns, 2.7–5.5V). A variante **-55SIN** é SOP-28, não sTSOP. Verificar código de compra e footprint no CAD.
- Alimentação candidata 5V com 100nF por CI próximo aos pinos e capacitores de reserva por grupo, valores definitivos após análise elétrica. Níveis HC de entrada, corrente, fanout e cargas exigem verificação.

## Pinagem SRAM U4 SOP-28 (vista superior)
|Pino|Sinal|Pino|Sinal|
|---:|---|---:|---|
|1|A14|28|VCC|
|2|A12|27|/WE|
|3|A7|26|A13|
|4|A6|25|A8|
|5|A5|24|A9|
|6|A4|23|A11|
|7|A3|22|/OE|
|8|A2|21|A10|
|9|A1|20|/CE|
|10|A0|19|DQ7|
|11|DQ0|18|DQ6|
|12|DQ1|17|DQ5|
|13|DQ2|16|DQ4|
|14|GND|15|DQ3|

## Pinagem 74HC273 SOIC-20 (vista superior)
|Pino|Sinal|Pino|Sinal|
|---:|---|---:|---|
|1|/CLR|20|VCC|
|2|Q0|19|Q7|
|3|D0|18|D7|
|4|D1|17|D6|
|5|Q1|16|Q6|
|6|Q2|15|Q5|
|7|D2|14|D5|
|8|D3|13|D4|
|9|Q3|12|Q4|
|10|GND|11|CLK|

## Mapeamento de RAM — 16 bits de CPU
- CPU `0x4000..0xBFFF` => 32KB SRAM `0x0000..0x7FFF`.
- SRAM A0..A13 = CPU A0..A13; **SRAM A14 = CPU A15** quando selecionada.
- `/CE` ativo somente para `0x4000..0xBFFF`, isto é, `A15 XOR A14 = 1` (com sinais estáveis e lógica de seleção apropriadamente sincronizada).
- Exemplos: 4000→0000; 7FFF→3FFF; 8000→4000; BFFF→7FFF.
- **Importante:** mapa de ROM, I/O e VRAM continua pendente; esse mapeamento é candidato e depende da ISA final.

## Proposta de controle da SRAM
|Estado|/CE|/OE|/WE|245 /OE|245 DIR|Comentário|
|---|---:|---:|---:|---:|---:|---|
|IDLE|1|1|1|1|1|Nenhum acesso|
|READ|0|0|1|0|0|SRAM→CPU|
|TURNAROUND|1|1|1|1|1|Desabilita SRAM e 245|
|WRITE_SETUP|0|1|1|0|1|CPU→SRAM, dados estáveis antes de /WE|
|WRITE_PULSE|0|1|0|0|1|Pulso de escrita|
|WRITE_HOLD|0|1|1|0|1|Mantém dados após /WE|

Os estados são **alvos estáticos**. Não é seguro aplicar todos os bits de controle simultaneamente sem analisar seus atrasos. A transição READ→WRITE deve primeiro retirar `/OE` da SRAM, desabilitar o 245, esperar os piores atrasos, configurar DIR e somente então habilitar o driver de escrita. A transição inversa requer processo simétrico. O modelo não verifica essa sequência em nanossegundos. WRITE_SETUP/PULSE/HOLD exigem períodos de setup/hold da SRAM conforme datasheet. Um clock de 1 MHz, 2 MHz ou superior **não está aprovado**.

## Resultados executados
`python3 isa1_rev20_sram_controller.py` gerou `isa1_rev20_results.json`:
- 68 posições de pinos com cobertura e unicidade verificadas: HC273 (20), HC245 (20), SRAM (28).
- 32.768 endereços CPU mapeados bijetivamente aos 32.768 endereços da SRAM.
- Seis estados estáticos sem condições de conflito definidas pelo modelo.
- 1.024 casos de dados/modos de leitura/escrita verificados; **não testam propagação física nem o conteúdo da memória**.
- Dois percursos conceituais com TURNAROUND verificados.

## Pontos que impedem fabricação
1. Criar esquema elétrico real com netlist, alimentação, desacoplamento, reset e clock.
2. Resolver seleção de ROM e I/O, temporização de decodificação e glitches de endereço.
3. Projetar o circuito real de sequenciamento, incluindo intervalos de alta impedância e sinais registrados.
4. Calcular tAA, tOE, tHZ, tWC, tWP, setup/hold e atrasos dos buffers e do decodificador, para condições de tensão/temperatura/carga.
5. Verificar carga elétrica, fanout e compatibilidade de níveis, inclusive no reset.
6. Simular com modelos HDL/temporais independentes ou SPICE apropriado e depois validar em protótipo.

## Datasheets
- TI SN74HC273: https://www.ti.com/lit/ds/symlink/sn74hc273.pdf
- TI SN74HC245: https://www.ti.com/lit/ds/symlink/sn74hc245.pdf
- Alliance AS6C62256: https://www.alliancememory.com/wp-content/uploads/AS6C62256-23-March-2016-rev1.2.pdf

## Arquitetura preservada
Uma única PCB SMD preferencialmente SOIC; CPU própria 8-bit, endereçamento 16-bit, flags e pilha, 64 teclas em quatro matrizes, armazenamento persistente e vídeo RCA colorido sob estudo. Nenhuma redução funcional aprovada.
