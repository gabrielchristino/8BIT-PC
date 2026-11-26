# ISA-1 — Rev. 2.8: escrita segura, sequência SDP e SAVE
Status: lógica conceitual testada; proteção física não aprovada.

## Problema descoberto
A proteção de SAVE por comparador simples de endereço é insuficiente para EEPROM com Software Data Protection: a sequência de desbloqueio inclui acessos a 5555h e 2AAAh, que estão na região de código. Um bloqueio absoluto dessas posições impede SAVE. Uma exceção irrestrita nessas posições, por outro lado, permite corrupção.

## Política candidata
A FSM de gravação, fisicamente separada do decodificador comum, autoriza:
1. Em modo SAVE, somente os pares (5555h,AAh), (2AAAh,55h), (5555h,A0h), na ordem e nos estados de desbloqueio, e somente quando os tempos reais do datasheet forem satisfeitos.
2. Em estado PAYLOAD, somente endereços 7800h..7FFFh.
3. Em modo PROGRAM, gravação integral somente após comando explícito de programação e autorização de hardware.
4. Durante reset, VCC inválida, chip ausente ou erro: /WE permanece inativo.

## Questão aberta crítica
O teste de pares endereço/dado em Python **não comprova** que a implementação com portas/flip-flops produzirá a mesma sequência, nem que as janelas temporais de escrita e SDP serão atendidas. Uma sequência inválida não pode liberar WRITE. Exigir circuito com estados registrados e teste de injeção de falhas.

## Integridade de dados
Manter slots A/B, CRC e commit por último. Avaliar vida útil de ciclos, proteção contra perda de energia e a semântica exata da programação da AT28C256. Não prometer recuperação física garantida sem protótipo.

Referência: https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C256-Industrial-Grade-256-Kbit-Paged-Parallel-EEPROM-Data-Sheet-DS20006386.pdf
