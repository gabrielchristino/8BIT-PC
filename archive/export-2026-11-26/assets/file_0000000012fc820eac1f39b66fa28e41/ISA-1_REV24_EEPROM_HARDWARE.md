# ISA-1 — Revisão 2.4: interface EEPROM ZIF, pinagem e proteção

Data: 2026-11-23. Status: **candidata tecnicamente documentada, ainda NÃO liberada para PCB**.

## Requisitos preservados
- CPU discreta 74HC/HCT, sem MCU comercial executando o programa.
- Um único CI removível para programa e dados/SAVE, ZIF com alavanca; o ISA-1 grava e verifica a mídia.
- Programa carregado em SRAM, executado nela. Sem troca de chip com alimentação ligada.
- Armazenamento interno independente será estudado posteriormente.

## Componente candidato
Microchip AT28C256-15, 32.768 × 8, alimentação 5 V ±10%, acesso máximo 150 ns, página de até 64 bytes, programação interna máxima de 3 ou 10 ms conforme variante, leitura por /CE e /OE, escrita por /WE. O modelo exato de compra, embalagem PDIP-28, estoque, procedência e endurance de variante **ainda não estão congelados**.

Fonte primária: [Microchip DS20006386B](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C256-Industrial-Grade-256-Kbit-Paged-Parallel-EEPROM-Data-Sheet-DS20006386.pdf), páginas 1, 4, 10–19.

## Pinagem real — PDIP-28, vista superior

| Pino | Sinal | Pino | Sinal |
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
|10|A0|19|I/O7|
|11|I/O0|18|I/O6|
|12|I/O1|17|I/O5|
|13|I/O2|16|I/O4|
|14|GND|15|I/O3|

## Proposta de interface — ainda sem esquemático fechado
- A0..A14: registradores de endereço de 15 bits, carregados por sequências da CPU, com saída estabilizada antes de selecionar o chip. Estudar compartilhamento com barramento de endereços e sua decodificação.
- I/O0..I/O7: transceptor bidirecional com controle explícito da direção e /OE, e isolamento dos outros drivers do barramento da CPU.
- /CE: inativo em reset, power-bad, ausência de operação ou fase de troca de direção.
- /OE: ativo apenas em leitura ou polling, nunca simultâneo com pulso de escrita.
- /WE: pull-up físico para 5 V e porta lógica de autorização combinando reset liberado, alimentação válida, estado WRITE registrado e permissão explícita de gravação; transições assíncronas exigem análise de glitches e supervisão.
- Para programar chips vazios e atualizar SAVE, habilitar proteção SDP da EEPROM; cada transação protegida deve ser precedida de AA@5555, 55@2AAA, A0@5555 (sequência conforme datasheet).
- Não usar a entrada /WE diretamente de ROM de microcódigo ou combinação suscetível a glitches.
- ZIF: conferir orientação, pino 1, força mecânica, acesso físico, desacoplamento e proteção ESD; **troca somente desligado**.
- A proteção do código por intervalos é uma **regra do firmware**: SDP protege o chip contra comandos de escrita sem desbloqueio, mas não oferece proteção física por região. Para impedir escrita errada no código por firmware defeituoso, precisaremos de mecanismo adicional ou aceitar esse risco.

## Estados de operação (proposta)

| Estado | /CE | /OE | /WE | Transceptor CPU→EEPROM |
|---|---:|---:|---:|---|
| IDLE / RESET / POWER_BAD |1|1|1|desabilitado|
| READ |0|0|1|desabilitado, sentido EEPROM→CPU quando necessário|
| TURNAROUND |1|1|1|desabilitado|
| WRITE_SETUP |1|1|1|CPU→EEPROM, endereço e dado estáveis|
| WRITE_PULSE |0|1|0|CPU→EEPROM|
| WRITE_HOLD |0 ou 1|1|1|segurar endereço/dado pelo mínimo exigido|
| POLL |0|0|1|EEPROM→CPU após liberar driver CPU|

A tabela é de intenções lógicas; o diagrama temporal e os valores de setup/hold ainda precisam ser derivados dos máximos/mínimos dos datasheets de todos os componentes.

## Escrita de página
- Páginas físicas têm 64 bytes; A6..A14 devem permanecer iguais durante uma transação de página.
- Até 64 bytes por programação; bytes consecutivos devem ser enviados dentro do intervalo máximo de 150 µs entre cargas (datasheet). Caso contrário o CI inicia a programação interna.
- Após a escrita, esperar conclusão por polling de I/O7 (com timeout conservador) e confirmar leitura/CRC. Não confundir leitura durante busy com dado estável.
- Para reduzir risco inicial, implementar primeiro escrita de **um byte por ciclo**; otimizar para páginas depois da validação elétrica e de software.
- O protocolo de SAVE A/B da revisão 2.3 ainda é **abstrato**; testar falha de energia real e múltiplas interrupções.

## Modelo de mídia preservado
- 0000–003F: cabeçalho de 64 bytes
- 0040–783F: código e recursos, 30.656 bytes
- 7840–7C3F: SAVE A, 1.024 bytes
- 7C40–7FFF: SAVE B, 1.024 bytes
- Todas as fronteiras são alinhadas a 64 bytes; não há página compartilhada entre regiões.
- A quantidade de código que pode ser executada simultaneamente depende do mapa de RAM, stack e buffers, ainda pendentes.

## Testes realizados
`python isa1_rev24_eeprom_verify.py` — 28 posições de pinos, 80 combinações estáticas de estados/intertravamentos, 32.768 endereços e 1.928 casos de fragmentação de escrita em páginas; sequência SDP gerada. Saída em `isa1_rev24_results.json`.

**Limites:** transcrição manual do datasheet, testes de software sem modelo de propagação de sinais, sem SPICE, sem PCB, sem medição de oscilações, glitches, retenção, endurance, alimentação ou queda de energia. O script não prova proteção contra todos os erros de firmware, nem valida a compatibilidade temporal real.

## Decisões pendentes para revisão 2.5
1. Definir latch/registrador real para A0..A14 e transceptor de dados, contando CIs e comparando com alternativa de acesso por memória mapeada.
2. Montar tabela de temporização usando tWP, tDS, tAH, tOE, tCE, tACC, tDF e atrasos dos 74HC/HCT escolhidos.
3. Definir supervisor de reset/power-good com part number real e verificar comportamento de /WE em subida/queda de alimentação.
4. Decidir como o sistema seleciona chip e como programa EEPROM sem destruir firmware de boot.
5. Conferir disponibilidade e preço de PDIP-28 genuíno e ZIF compatível antes de fechar a BOM.
