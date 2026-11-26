# ISA-1 — Rev. 2.9: auditoria de estabilidade e critérios de liberação
Data: 2026-11-23
**Conclusão: subsistema ZIF mais coerente no modelo, ISA-1 NÃO está estável para fabricação.**

## Teste reproduzível
`python isa1_rev27_29_validation.py` grava `isa1_rev27_29_results.json`.
- 48.384 combinações de sinais estáticos sem conflitos no modelo.
- 32.768 endereços da EEPROM cobertos uma única vez.
- Verificação dos 20 pinos do HC244 contra tabela manual transcrita (não verificação independente do datasheet).
- Dois testes negativos detectam contenção forçada.
- Teste da exceção de desbloqueio SDP, incluindo sequência incorreta rejeitada.
- O modelo não cobre atrasos entre sinais, transientes, defeitos, alimentação, firmware completo ou vídeo.

## Bloqueadores por prioridade
**P0 — Segurança elétrica:** esquema pino a pino completo, reset e supervisor de alimentação com variante exata, /WE fail-safe desde VCC=0, proteção ZIF, desacoplamento e carga de barramento; simulação de transientes com modelos adequados e protótipo físico.
**P0 — Temporização:** extrair tACC, tOE, tCE, tWP, tAS, tAH, tDS, tDH e tWC da variante exata da AT28C256; extrair tempos de propagação/habilitação dos HC377/HC244; elaborar orçamento worst-case, testar margem e formas de onda.
**P0 — Correção funcional:** executar código real ISA-1 em simulador da CPU e ROM; LOAD/RUN/SAVE/VERIFY; injetar cortes de energia em diferentes instantes; recuperação A/B e CRC.
**P1 — Integração:** RAM 32 KB sem aliasing, ROM de firmware, mapa de I/O, CPU e instruções, teclado 4×16 com ghosting definido, vídeo composto colorido com circuito codificador realmente especificado.
**P1 — Projeto físico:** esquema e BOM com fornecedores/footprints verificáveis, ERC, PCB DRC, SI/PI simplificada, medições em protótipo e regressão de firmware.

## Critérios para 'estável'
- Nenhum conflito de barramento em ciclos completos de leitura/escrita com margens worst-case verificadas.
- Gravação/verify da EEPROM e proteção de código demonstradas com chip real; proteção de queda de energia medida.
- CPU executa instruções, interrupções se previstas, stack e sub-rotinas em hardware/protótipo.
- Vídeo RCA colorido testado na tela-alvo; teclado 64 teclas testado.
- Esquemático e PCB passam ERC/DRC e protótipo funcional passa testes de regressão.

## Estratégia
Continuar por marcos verificáveis; **não confundir passar testes de software com versão estável física**. Reutilizar decisões do Gigatron somente onde o benefício for demonstrado para a arquitetura ISA-1.
