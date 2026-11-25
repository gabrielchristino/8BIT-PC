# Decisões recuperadas e registro da migração

## ADR E05 — Banco SP com soma compartilhada e simulação da netlist

Decisão nova de 25/11/2026: manter SP em dois HC273 com feedback por quatro HC157, um somador de quatro CD74HC283 para SP±1, duas inversões em HC04 e direção distribuída por HC125. SP lógico vazio continua 8000h; somente Q15 é codificado invertido para usar clear=0. Alternativas: contadores HC191 exigiriam ainda resolver SP−1 retido; somadores separados duplicariam a aritmética; compartilhar com X ampliaria os estados de arbitragem/WAIT. Escolher esta base verificável sem alegar economia de BOM. O esquema é exportado e suas conexões reais geram a simulação; o controle físico de UPDATE e o latch de barramento permanecem externos. Aceitação funcional: pinos/netlist consistentes, todo SP/direção, guardas e regressões de instruções/boot/VGA sem divergências. Produção ainda exige circuito de controle, temporização global, cargas, reset/alimentação, esquema completo e ERC/DRC. Evidência: docs/engineering/NET02.md.

## ADR E04 — Verificar dois bytes antes de CALL/RET

Decisão nova de 24/11/2026: CALL e RET verificam antecipadamente a disponibilidade dos dois bytes da pilha antes do primeiro acesso de pilha. O modelo recuperado verificava cada byte separadamente, permitindo escrita/alteração parcial de SP antes de falhar no segundo. A alternativa de manter isso foi rejeitada por deixar um estado parcial evitável; rollback após escrita física seria mais complexo e não corrige cortes de energia. O intervalo válido de CALL é [0002h,8000h] sem overlay, [4002h,8000h] com overlay. RET aceita [0000h,7FFEh] ou [4000h,7FFEh]. PUSH/POP mantêm os limites de um byte. Não mudam a ordem da pilha, SP vazio, os opcodes ou instruções válidas. Em caso inválido, a nova RTL para com código de falha e SP intacto; buscas da instrução/operandos já realizadas não são desfeitas. Isso altera intencionalmente somente casos de falha da referência histórica. A referência de testes é um adaptador novo sobre o CPU original, com essa extensão explícita. Aceitação: todos os valores de SP, ambos os estados de overlay e as quatro operações, além da regressão integrada. Não há promessa de atomicidade contra reset/energia depois de uma escrita válida já concluída.

## ADR E03 — Executar as ROMs antes de otimizar todo o controle físico

Decisão nova de 24/11/2026: estabelecer uma CPU RTL comandada pelas quatro lanes binárias originais, com comparação de estado/transações contra a referência arquitetural e seleção entre X ideal e o banco HC191/157/377. A alternativa de fechar primeiro um sequenciador isolado de carga deixaria sem comprovação a ligação entre ROM e datapath. A integração tem prioridade porque a inspeção mostrou que o sequenciador recuperado era testado isoladamente. Preservam-se as ROMs e os 26 opcodes; não há alteração intencional da ISA válida. Critério de aceitação: regressão de instruções, reset/energia, ACK prolongado, boot real a partir da imagem EEPROM, bancos e quadro VGA sem divergências. Componentes de controle, SP−1 físico, compatibilidade elétrica e netlist derivada do esquema continuam necessários. Evidência e limites: docs/engineering/RTL01.md.

## ADR E01 — Carga protegida do contador candidato

Decisão de engenharia nova, 24/11/2026: separar captura, carga assíncrona, liberação e retenção antes de voltar a permitir contagem. Não ligar LOAD diretamente ao nível de ACK/COMMIT. Preservar a CPU recuperada enquanto o controle físico, a equivalência arquitetural e SP-1 não estiverem resolvidos. A alternativa de substituir imediatamente registradores por HC191 foi adiada: o banco isolado precisa de armazenamento/multiplexação auxiliares e não demonstrou economia total. Critério de aceitação para integração: simulação de netlist, 26 opcodes equivalentes, estabilidade durante WAIT, atualização única e reset seguro, além de fechamento temporal. Resultados e condições em docs/engineering/REV9842.md.

## ADR E02 — Execução das ferramentas no Ubuntu WSL

Preferência explícita do usuário: simulações/construção em WSL Ubuntu, com fontes persistentes no diretório Windows do projeto e saídas temporárias no Linux. Pacotes Icarus Verilog, ngspice e KiCad instalados pelos repositórios Ubuntu. Registrar versões efetivas e não confundir disponibilidade de ferramentas com validação do circuito. KiCad CLI 7 exporta o esquema/netlist, mas o ERC segue pendente.

As decisões técnicas abaixo são registradas a partir de fontes históricas. O status «proposta» não significa aprovação de fabricação. Novas decisões da migração são identificadas explicitamente.

| ID | Decisão e razão | Status e fonte |
|---|---|---|
| H01 | Preservar CPU própria, X, pilha, flags e todas as 26 instruções; não remover recursos para economizar CIs | Diretriz histórica; conversa principal e auditoria REV76 |
| H02 | VGA RGB332 160 × 120 lógico, em lugar de propostas anteriores RCA/16 ou 64 cores | Direção posterior; conversa 6.x–9.x e README rev983 |
| H03 | USB-C 5 V; retirar a necessidade anterior de 12 V | Direção histórica; análise 6.9 |
| H04 | Banco de VRAM e EEPROM permite 96 KiB físicos com endereçamento de 16 bits | Modelo implementado; cpu.py/system.py rev983 |
| H05 | SP=8000h vazio, PUSH em SP-1, POP em SP; preservar atualização única após transação | Modelo posterior; cpu.py/control.py e README rev984. Difere da REV33 |
| H06 | Endereço/dados estáveis em WAIT; efeitos arquiteturais após confirmação; reset cancela operações antigas | Modelos integrated.py/control.py, revisões 9.3/9.8.3 |
| H07 | Compartilhar somadores X/SP somente se houver economia real e retenção segura de endereço | Alternativa adiada; conversa 9.8.4: muxes podem eliminar a economia |
| H08 | Investigar 74HC191 para X; manter circuito SP anterior até resolver SP-1 | Proposta 9.8.4.1; alternativa 74HC193 usa dois clocks; contador isolado não entrega os dois endereços |
| H09 | Membranas prontas sem diodos; quatro linhas e 16 colunas; linhas inativas Hi-Z | Proposta ENG-KBD-01 D01–D03 |
| H10 | Bloquear quadros acima de duas teclas, CANCEL/ALL_UP, rearme após vazio estável | Proposta ENG-KBD-01 D04; três teclas legítimas também podem ser rejeitadas |
| H11 | MMIO sem novos opcodes; polling inicial; endereços e ABI por conciliar | Proposta ENG-KBD-01 D05–D06 |
| H12 | Não fabricar antes da validação elétrica, temporal, integração e revisão de esquema/layout | Bloqueio histórico REV76 e ENG-KBD-01 D07 |

## ADR M01 — Preservar snapshots e originais

**Decisão da migração, 24/11/2026.** Guardar ZIPs sem alterações em `archive/packages/` e extrações em `revisions/`, por revisão. Não consolidar arquivos de versões diferentes sob uma falsa revisão completa. Alternativa rejeitada: copiar apenas o último simulador e perder os estudos intermediários. Consequência: duplicação deliberada, controlada por hashes.

## ADR M02 — Separar evidências por nível

Downloads de arquivos, texto extraído da interface e resumos editoriais têm provenance distinta. Um trecho virtualizado de JSON é um fragmento, não uma tabela completa. Números históricos são relatos até reprodução local. Nenhum código será recriado e apresentado como original para preencher ausências.

## ADR M03 — Publicar a recuperação disponível com lacunas explícitas

O GitHub estava vazio na inspeção inicial. Publicar materiais recuperados e documentação de continuidade sem reescrever histórico nem simular commits antigos. A existência de uma revisão citada em conversa não comprova que seu pacote foi recuperado. A migração integral permanece condicionada à recuperação das lacunas listadas.

## ADR M04 — Preservar a falha da bancada do montador

O pacote rev983 contém `test_assembler.py`, mas omite `diagnostic.asm`. Manter a bancada e registrar a falha de dependência. Não inventar um firmware diagnóstico ou retirar a bancada para produzir um relatório artificialmente verde. Recuperar o arquivo e executar novamente é o critério de resolução.
