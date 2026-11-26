# ISA-1 — Registro de decisões e riscos — Rev. 0.8
Data: 2026-11-22. Status: estudo de viabilidade, **NÃO APTO PARA FABRICAÇÃO**.

## Requisitos fixados
- Nome: ISA-1 (homenagem a Isabel). Computador autônomo, CPU própria com lógica 74HC, sem microcontrolador como processador ou controlador gráfico.
- Barramento de dados 8 bits; endereços 16 bits; ROM monitor, teclado físico 4×4×4, saída RCA CVBS monocromática.
- Um único modo gráfico, framebuffer 256×192, 1 bit/pixel; caracteres 8×8 renderizados por software (32×24).
- Não exigir taxa fixa de FPS de software; gerador CVBS funciona independentemente da execução da CPU.
- Revisão por simulação, esquemático, análise elétrica e protótipo antes de qualquer PCB definitiva.

## Decisões de arquitetura provisoriamente adotadas
D01. ROM CPU 0000–3FFF (16 KiB expostos da EEPROM AT28C256 de 32 KiB); RAM 4000–BFFF (32 KiB 62256); VRAM C000–DFFF (8 KiB 6264); I/O E000–E0FF; expansão E100–FFFF. Revisar seleção de chips e barramento.
D02. SRAM 62256: A0–A13 físicos ligados a A0–A13 CPU; A14 físico ligado a A15 CPU, somente com chip-select habilitado para 4000–BFFF. Tradução verificada matematicamente; sinais elétricos não verificados.
D03. Framebuffer ocupa C000–D7FF (6144 B), 32 bytes por linha; D800–DFFF livres como VRAM auxiliar. Uma só modalidade de vídeo; firmware desenha caracteres.
D04. Vídeo com clock mestre candidato de 14,31818 MHz, pixel clock /2 = 7,15909 MHz; 455 clocks de pixel por linha = 15.734,26 linhas/s. 262 linhas/quadro => 60,054 Hz. **Não é ainda uma temporização CVBS validada**. O desenho ocupa 256 clocks de pixel (~35,75 us) e precisa de margens e dimensionamento horizontal; sinal progressivo 240p-like pode não ser aceito em todos os monitores.
D05. Clock CPU derivado do mesmo oscilador mestre /16 ≈ 894,886 kHz como alvo de estudo. Evita cruzamento de clock entre CPU e vídeo se todos os controles forem síncronos; CPU pode ser parada por clock-enable, sem interromper o clock do vídeo. Divisão, skew e setup/hold precisam ser verificados.
D06. Prioridade do vídeo na SRAM; interface CPU–VRAM por requisição/concessão com parada da CPU em fronteira segura de microciclo. Não usar duas saídas push-pull sobre o mesmo barramento. Circuito de arbitragem ainda não projetado.
D07. CPU de acumulador A/B, PC16, X16, SP16, flags Z/C, instruções indiretas e CALL/RET. ISA binária ainda NÃO congelada; emulador Rev 0.7 é apenas referência parcial e não modela X nem microcódigo.
D08. Teclado 4 linhas × 16 colunas, 4 membranas 4×4, 2 teclas simultâneas; linhas não selecionadas em alta impedância. 74HC574 + 74HC139 + 74HC125 + 2×74HC244 é candidato, ainda sem pinagem elétrica auditada.
D09. Fonte 8×8 em ROM do firmware; não haverá ROM de caracteres no caminho de vídeo. Atualização de EEPROM por gravador externo inicialmente.
D10. Reservar saída de diagnóstico por LEDs, RESET global, pontos de teste, desacoplamento e conectores modulares.

## Problemas identificados (bloqueiam fabricação)
P01. Falta datapath pino a pino, microsequenciador, formato de microinstrução e geração de sinais sem glitches.
P02. Falta conjunto definitivo de instruções e prova de execução com ciclos/microcódigo.
P03. Falta esquema de arbítrio da VRAM, orçamento de tempos de acesso e protocolo WAIT/clock-enable.
P04. Falta forma de onda de sincronismo horizontal/vertical, blanking e saída analógica CVBS terminada em 75 ohms; compatibilidade de 262 linhas progressivas com monitor não verificada.
P05. Falta análise do caminho crítico da CPU e dos buffers/decodificadores, incluindo tempo de acesso EEPROM e SRAM.
P06. Falta validação do teclado elétrico, pinagens de CI, ghosting com 3+ teclas, reset e bounce.
P07. Falta verificação da alimentação 5 V, orçamento de corrente, integridade de sinal e footprint de cada CI.
P08. Falta firmware real (monitor, fonte, desenho, teclado), assembler e programa de diagnóstico.
P09. Contagem de CIs, BOM exata, preço e PCB **não podem ser afirmados** ainda.
P10. Mapeamento do barramento externo e isolamento de sinais não especificados.

## Testes executados
- Rev 0.7 existente: mapeamento RAM 32768 bytes, framebuffer completo, pequenos programas de CPU e pilha; aprovados em modelo comportamental.
- Rev 0.8: repetição dos testes; fronteiras ROM/RAM/VRAM/I/O; teste aritmético de referência em 256×256 pares ADD/SUB; cálculo da frequência de linha e de quadro candidata; aprovados.
- Esses testes **não** simulam portas lógicas, microcódigo, latência, sinais de vídeo ou componentes físicos. A verificação aritmética Rev 0.8 não executa a ALU do circuito.

## Próximo gate de aprovação
1. Fechar ISA binária e construir emulador independente de referência com testes de instruções, incluindo X/SP, flags e pilha.
2. Definir datapath, sinais e microcódigo; escrever simulador ciclo a ciclo e comparar estados com o emulador.
3. Simular controlador de vídeo e VRAM com cronograma de barramento, testar no mínimo leitura contínua e escritas concorrentes.
4. Gerar esquemático KiCad com datasheets por fabricante e executar ERC; análise de temporização e simulação da saída CVBS.
5. Protótipo modular e medição em osciloscópio/analisador lógico; só então congelar BOM e PCB.

## Política de mudanças
Toda alteração recebe revisão, motivo, riscos, testes executados e arquivos alterados. Nenhuma afirmação de '100% funcional' sem testes físicos. Decisões são provisórias até satisfazer os gates.
