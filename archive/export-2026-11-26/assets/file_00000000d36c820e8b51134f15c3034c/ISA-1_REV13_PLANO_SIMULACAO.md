# ISA-1 — Rev. 1.3: Plano de simulação e primeiro teste

## Objetivo
Validar o projeto antes da fabricação de uma PCB principal SMD (SOIC preferencial), sem alegar que simulação substitui protótipo físico.

## Primeiro experimento executado
Modelo lógico comportamental de dois somadores de 4 bits em cascata (função de 74HC283) para ADD, ADC e SUB de 8 bits, com flags carry e zero. Teste exaustivo de todos os 256×256 operandos e dois valores de carry-in para soma, mais subtração. Ver `isa1_rev13_alu_logic_test.py`.

**Limites:** ainda não é um esquema de pinos do CI, nem uma simulação temporal/analógica, nem uma CPU completa. A escolha do 74HC283 é hipótese de estudo, não componente aprovado.

## Estratégia
1. **Especificação funcional:** fixar ISA, estados, mapa de memória, barramentos e interfaces.
2. **Modelo lógico de referência:** testes exaustivos dos blocos pequenos e programas de teste da CPU completa.
3. **Esquema por CI:** ligar pinos reais, incluindo alimentação, reset, OE e polaridades; conferir datasheets.
4. **Simulação de eventos com atrasos:** aplicar atrasos min/max de componentes e tempos de acesso de ROM/RAM; conferir setup/hold, glitches e contenção.
5. **Simulação elétrica:** SPICE para clock/reset, alimentação e vídeo composto, com modelos disponíveis e hipóteses explicitadas.
6. **EDA:** ERC, DRC, checagem de footprints, netlist, pinagem, conectores, BOM e fabricação.
7. **Protótipo físico:** energização com limitação de corrente, medição de clocks, barramentos, memórias e saída de vídeo antes da revisão final.

## Critérios de aprovação antes de encomendar
- Sem erros de lógica conhecidos nos testes previstos.
- Sem conflitos de drivers em qualquer estado de barramento.
- Margens temporais demonstradas para pior caso e tensão/temperatura previstas.
- Consumo e desacoplamento dimensionados; níveis lógicos compatíveis.
- Vídeo RCA testado em nível de forma de onda e, depois, em monitor real.
- Esquema e PCB revisados contra datasheets dos componentes escolhidos.

## Estado atual
Somente o primeiro teste lógico da aritmética foi executado. Ainda não há aprovação da arquitetura elétrica, da CPU completa, da temporização, do vídeo ou da PCB.
