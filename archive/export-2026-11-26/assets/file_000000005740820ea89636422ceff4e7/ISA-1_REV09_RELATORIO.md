# ISA-1 — Relatório de engenharia Rev. 0.9
Data: 2026-11-22. Estado: PROTÓTIPO COMPORTAMENTAL; NÃO FABRICAR.

## Decisões desta revisão
- D11: Preservar ROM 0000–3FFF, RAM 4000–BFFF, VRAM C000–DFFF, I/O E000–E0FF. O circuito físico de decodificação continua pendente.
- D12: CPU de referência terá X16 e endereçamento indireto; a pilha inicia em BFFF e cresce para endereços menores. CALL empilha PC alto e depois PC baixo; RET desempilha baixo e depois alto. O firmware deve inicializar SP.
- D13: Flags Z/C: ADD define C como carry-out; SUB/CMP definem C=1 quando não há empréstimo; CMP não modifica A. Operações lógicas e carga de A modificam Z e preservam C (convenção provisória).
- D14: Manter candidato clock mestre 14,31818 MHz e pixel /2, 455 clocks/linha, 262 linhas/quadro; NÃO está demonstrado sincronismo CVBS compatível. Área de 256x192 começa no clock horizontal 96 e linha vertical 35, apenas para testar endereços.
- D15: Um byte de vídeo deve ser buscado a cada oito clocks de pixel, enquanto registrador de deslocamento transmite bits. A arbitragem CPU–VRAM será desenhada somente após orçamento de temporização real.
- D16: O programa de teste de hardware será uma sequência verificável de ROM e RAM, antes de tentar o monitor ou biblioteca gráfica.

## Testes realizados
Arquivo `isa1_rev09_model.py` executado com Python 3. O programa incorpora e repete testes da Rev. 0.7.
- PASS: mapeamento bijetivo de 32768 endereços CPU em RAM física.
- PASS: teste do framebuffer 256x192, com set/clear de todos os 49152 pixels.
- PASS: programas Rev. 0.7 de ADD, CALL/RET, pilha e salto.
- PASS: integração Rev. 0.9 com LDX #16, STA [X], LDA [X], INX, DEX, CMP, JNZ, CALL, RET.
- PASS: 6144 leituras de bytes de vídeo, de C000 a D7FF, no modelo de agendamento, e 12000 requisições abstratas de CPU atendidas fora das reservas de leitura de vídeo.
- PASS: frequência candidata 15734,2637 linhas/s, 60,0544 quadros/s.

## LIMITAÇÕES CRÍTICAS — não confundir teste com prova elétrica
- O agendador considera cada tick de pixel um slot, mas um tick dura ~139,7 ns. Uma SRAM 6264 lenta (p.ex. 150 ns) NÃO pode ser presumida capaz de realizar um acesso completo por tick. A CPU tampouco opera por tick de pixel. Necessário especificar chip por sufixo de velocidade, propagação de multiplexadores e buffers, tempos de /OE, /WE e turn-around. Não há ainda arbitração real.
- O teste de CPU executa instruções em nível de software, não microoperações de um datapath 74HC; o teste aritmético é uma identidade matemática, não verificação de uma ALU construída.
- O programa demonstra alguns opcodes, não cobre todas as combinações de registradores, flags, endereços e instruções.
- A frequência de linha próxima de NTSC não garante um CVBS correto: ainda faltam sincronismos horizontal/vertical, níveis analógicos, apagamento e avaliação de 240p/262 linhas pelo monitor.
- Não há esquemático, PCB, BOM exata, microcódigo nem pinagem verificada. Não comprar nem fabricar.

## Riscos adicionais encontrados
- R01: O tempo de acesso de SRAM é restrição primária; uma 6264 de 150 ns pode inviabilizar slots curtos. Estudar SRAM 6264 rápida, latch e leitura antecipada, ou divisão de fases mais longas.
- R02: A seleção de clock /16 da CPU não dispensa sincronização e sequenciamento de escrita: um ciclo de CPU é ~1,117 µs e o de pixel ~139,7 ns.
- R03: O endereçamento indireto X16 requer circuito real para incrementar 16 bits e fornecer endereço ao MAR, não só um par de latches.
- R04: CALL/RET e PUSH/POP requerem atualização de SP16, sequenciamento e proteção contra pilha fora de RAM. O emulador só fornece proteção diagnóstica, não mecanismo de proteção em hardware.
- R05: O mapa ROM 16 KB + RAM 32 KB + VRAM 8 KB + I/O/expansão precisa de lógica de seleção mutuamente exclusiva, com teste de todos os 65536 endereços.

## Próximo gate
1. Fixar a ISA de referência e gerar testes de opcode/flags/casos-limite; avaliar instruções faltantes para monitor de comandos.
2. Desenhar datapath em nível de registradores com fontes/destinos únicos por ciclo, PC/SP/X de 16 bits e ALU; estimar largura de microinstrução.
3. Criar simulação de microoperações e comparar estado final com o emulador em cada instrução.
4. Construir orçamento de tempo real para VRAM e gerar formas de onda digitais e analógicas CVBS antes da BOM.
