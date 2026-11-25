# Inventário do acervo

O inventário detalhado por caminho, tamanho, SHA-256 e origem fica em [archive/manifest.json](../archive/manifest.json). Esta visão explica os grupos e seu estado.

| Grupo | Conteúdo | Estado |
|---|---|---|
| archive/packages | Três ZIPs de revisões 9.3, 9.8.3 e 9.8.4.1 | Bytes originais retidos |
| revisions/rev93 | 17 entradas: CPU/sistema, reset, handshake, teclado e validações | Snapshot anterior separado |
| revisions/rev983 | 34 entradas: CPU/ALU, controle, montador/desmontador, EEPROM, teclado/vídeo, testes, resultados e quatro ROMs | Snapshot completo mais recente recuperado; diagnóstico ausente |
| revisions/rev984 | 4 entradas: README, counter.py, results.txt e previous_README.md | Incremento isolado; não inclui CPU completa |
| archive/conversations | Quatro leituras de conversas relacionadas com IDs de mensagens | Parcial; não exportação completa |
| archive/pages | Duas páginas com conteúdo retornado pela API e Markdown | Completo para as páginas lidas |
| archive/browser-captures | Capturas adicionais da conversa e prévias de arquivos | Texto da interface; verificar cobertura e virtualização |
| scripts | Verificador de bancadas e de integridade do acervo | Novo na migração |
| verification | Saídas locais, falhas e comparação de ROM | Novo na migração |

## Fontes e código por função

- CPU e sistema: cpu.py, system.py, integrated.py.
- Modelos de portas: logic.py, alu_gates.py, datapath_blocks.py; counter.py no incremento.
- Microcódigo: microcode.py, control.py, sequencer.py e control_lane0–3.bin.
- Ferramentas de software: assembler.py, disassembler.py, eeprom.py.
- Teclado e validações: keyboard.py, validation.py e test*.py.
- Resultados históricos: arquivos *_results.json, blocks_results.txt e results.txt presentes em seus respectivos snapshots.
- Engenharia do teclado: página ENG-KBD-01 integral, com alternativas, pseudocódigo, orçamento elétrico e plano de testes.

## Revisões e decisões

REV76 é a grafia de arquivo usada para revisão 7.6. Revisões 7.7–7.9 e posteriores são mencionadas em cabeçalhos e fontes cumulativas dos pacotes. Isso comprova presença de conteúdo cumulativo, não posse de cada ZIP intermediário. A conversa contém propostas que mudaram de numeração; a documentação não deve tentar criar uma sequência de commits antigos a partir delas.

As decisões de arquitetura e alternativas são indexadas em [DECISIONS.md](../DECISIONS.md). O roadmap organiza pendências sem declarar implementações novas.
