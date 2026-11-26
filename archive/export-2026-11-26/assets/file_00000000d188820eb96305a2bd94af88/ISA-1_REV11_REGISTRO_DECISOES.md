# ISA-1 — Registro de decisões Rev. 1.1 (proposta)
Data: 2026-11-23

## Objetivo
Computador autônomo de 8 bits com CPU de lógica discreta 74HC/HCT, teclado de quatro matrizes 4x4, vídeo composto RCA para monitor pequeno, execução e armazenamento de programas sem PC moderno durante uso normal.

## Decisões
- D27 (confirmada pelo usuário): quatro teclados matriciais 4x4 compondo 4 linhas x 16 colunas, 64 teclas. Exigir varredura eletricamente segura e teste de duas teclas; sem diodos, não garantir rollover de 3 ou mais teclas.
- D28 (direção aprovada): investigar CPU minimalista com controle combinacional inspirada no Gigatron; não congelar número de CIs antes de netlist, pinagem e temporização.
- D29 (confirmada): saída RCA composto, sem exigir monitor VGA.
- D30 (em avaliação): vídeo composto colorido usando codificação NTSC/PAL compatível com a tela. Avaliar encoder dedicado, disponibilidade, preço e sincronismos. Plano de contingência: monocromático.
- D31 (proposta): SRAM de trabalho, ROM/EPROM ou EEPROM de firmware protegida e EEPROM separada para SAVE/LOAD. Não confundir EPROM UV com EEPROM gravável eletricamente.
- D32 (proposta): desenvolvimento no próprio computador via monitor/BASIC e salvamento não volátil. Gravação inicial do firmware exige mecanismo de bootstrap externo ou gravador manual, a definir.
- D33 (em avaliação): ROM de instruções de 16 bits ao estilo Gigatron versus ROM de 8 bits + controle combinacional; estimar custo e ICs antes de escolher. Evitar prometer 16KiB ROM no mapa se ROM for memória de instruções separada.

## Riscos e pontos de revisão
1. Alterar a CPU altera a ISA: emuladores anteriores não validam a nova CPU.
2. No Gigatron, ROM de 16 bits contém instruções e controle; 32KiB de SRAM é memória de dados, não um mapa único igual ao desenho anterior.
3. CPU gerando vídeo reduz ICs mas exige ciclos determinísticos e pode comprometer BASIC/teclado/armazenamento; comparar com controlador independente.
4. RCA colorido exige subportadora e codificação, não apenas resistores RGB; confirmar NTSC/PAL aceito pela tela.
5. EEPROM de armazenamento precisa de controle de escrita, polling de conclusão, proteção e política de desgaste.
6. A meta '100% usável' exige software real, esquema verificável, BOM, teste de temporização e protótipo físico; não há validação elétrica ainda.

## Próximo marco
Comparar duas arquiteturas com contagem de ICs por função: (A) Gigatron-like ROM de 16 bits e vídeo por CPU; (B) CPU minimalista e vídeo independente. Selecionar depois de testar ciclo a ciclo e orçamento de temporização. Definir memória e interface de teclado e armazenamento coerentes com a arquitetura escolhida.
