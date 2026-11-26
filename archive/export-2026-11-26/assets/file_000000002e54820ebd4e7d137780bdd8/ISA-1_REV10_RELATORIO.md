# ISA-1 — Relatório de engenharia Rev. 1.0
Data: 2026-11-22. **NÃO FABRICAR / NÃO COMPRAR BOM DEFINITIVA.**

## Evidências reproduzíveis
Execute `python3 isa1_rev10_audit.py` na pasta que contém os emuladores das revisões anteriores. Testes executados com sucesso:
- Partição exaustiva dos 65.536 endereços: ROM 16.384, RAM 32.768, VRAM 8.192, I/O 256, reservado 7.936.
- Teste de bijeção da tradução RAM CPU 4000–BFFF -> SRAM física 0000–7FFF.
- **196.608 execuções reais de CPU.step()** para ADD, SUB e CMP, em todos os 65.536 pares de operandos, verificando A, Z, C e PC. Diferente das identidades matemáticas da Rev. 0.9, agora são executadas as instruções do emulador.
- 256 PUSH e 256 POP em ordem inversa, conferindo dados e SP.
- 6.144 endereços consecutivos de framebuffer.

## Decisões D17–D22
- D17: manter resolução **lógica** 256×192 1bpp e VRAM 8 KiB. A compatibilidade CVBS ainda não foi demonstrada.
- D18: clock mestre 14,31818 MHz, vídeo /2 e CPU /16 continuam **candidatos**, não peças aprovadas.
- D19: manter uma única representação de vídeo (bitmap); caracteres desenhados pelo firmware.
- D20: para minimizar risco, desenvolver primeiro CPU+ROM+RAM+LEDs, depois vídeo independente e finalmente arbitragem; não fazer uma placa integrada antes de protótipos.
- D21: não escolher modelo/sufixo de SRAM antes de análise de setup, hold, tempo de acesso e turnaround.
- D22: criar teste de equivalência entre microoperações e emulador antes de declarar CPU validada.

## Erros e riscos identificados
1. **Geometria do vídeo**: 256 pixels a 7,15909 MHz ocupam 35,7587 µs. A área ativa nominal de ~47,7 µs não é preenchida. Margens e proporção física exigem cálculo; não chamar isso de sinal CVBS final.
2. **Quadro 262 linhas**: ~60,0544 Hz com 455 clocks/linha; não é por si só sincronismo NTSC 525 linhas entrelaçado. Avaliar sinal progressivo compatível com monitor AV real.
3. **Arbitragem da VRAM**: janela de 8 pixels = 1,11746 µs por byte. Não é prova de acesso da CPU, que exige ciclo completo com endereço estável, OE/WE, habilitação e isolamento.
4. **Microcódigo não existe**: ainda não há uma microinstrução executável nem uma contagem válida de EEPROMs.
5. **ALU de portas não simulada**: a execução de ADD/SUB/CMP no emulador prova apenas semântica de software.
6. **CPU incompleta para monitor**: ainda não temos instruções de inicialização explícita de SP, transferência flexível entre A/B, carregamento de B pela RAM, testes de limites, reset e tratamento de opcode inválido em hardware. A ISA não está congelada.
7. **Pilha**: a proteção contra overflow/underflow do emulador é diagnóstica e não está prevista em hardware. O firmware deve inicializar SP e respeitar limites.
8. **ROM**: EEPROM 32 KiB fisicamente com 16 KiB mapeados; verificar pinos, tempos e seleção antes de esquemático.
9. **Teclado**: matriz sem diodos só suporta duas teclas sem ambiguidade em modelo ideal; verificar componentes, pinos, tempos e interferência real.

## Critérios do próximo gate
- ISA completa com tabela de opcodes, operandos, flags, reset, stack, memória e instruções inválidas.
- Modelo independente de microoperações que passe pelos mesmos programas do emulador, sem reutilizar a função `CPU.step()`.
- Datapath com todos os caminhos físicos de 8/16 bits, um único driver por barramento, registradores e clocks especificados.
- Orçamento de tempo para cada tipo de acesso à VRAM e temporização CVBS detalhada.
- Depois: simulação elétrica/digital, datasheets específicos, esquemático pino a pino, ERC/DRC e protótipo.

## Estado
**Modelo comportamental testado parcialmente; circuito não validado; lista definitiva de materiais indisponível.**
