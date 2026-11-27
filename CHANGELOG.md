NET31,27/11/2026: acrescentados contrato candidato de DAC, calculos racionais e bancada comportamental de pacotes VGA.256cores/16cantos e quadro sintetico105000/76800pixels; quatro negativos rejeitados pelos guards. Registrados seis PDFs TI, quatro timeouts ADI, fatos web e lacunas. Nenhum esquema/BOM modificado; NET30 mantido. Evidencias e manifestos em verification/net31; ver docs/engineering/NET31_DAC.md.

Atualização NET-24 (26/11/2026): dois pinos agrupam o sincronizador de pedidos no mesmo clock, mantendo31CIs. 32 cenários selecionados, 6.886 casos ideais, dois temporizados de1.062, oito cortes da CPU e boot/quadro passaram. Permanece uma rejeição reproduzida: quatro resets com perfil assimétrico geram pulso7,722ns contra20ns no modelo HC74; não são aprovações. Apenas U4.3/U4.11 da folha common_request mudam; modelos e resultados originais preservados. Rejeições de pulso constam explicitamente do relatório.

Atualização NET-23 (26/11/2026): dois osciladores ACH candidatos no esquema e recepção da CPU por duas Schmitt livres, sem CI adicional de lógica. Partida/falta de clock, pinos SRAM, oito cortes de escrita da CPU e6.886 casos ideais/dois cenários temporizados de1.062 passaram. Carga15pF exige trilhas até5pF e código completo/BOM, jitter/POR e temporização global continuam abertos. Variante intermediária e falhas de fixture preservadas; detalhes em docs/engineering/NET23.md.

Atualização NET-22 (26/11/2026): variante de vídeo corrige sensibilidade do anel de fases a atrasos distintos de buffers. Shift AHC164/NOR LVC1G27 e carry de linha registrado; 36 CIs, um a mais. 384 combinações de atrasos e256 de assimetria de pulsos, 6.886 casos ideais da CPU, dois cenários temporizados de1.062, boot/quadro completo e cortes de reset passaram; osciladores físicos e fechamento global continuam pendentes. Antecessores e falhas intermediárias preservados; detalhes em docs/engineering/NET22.md.

Atualização NET-21A, 26/11/2026: TPS3808G01DBVR, pull-up 100 kohm, dois Schmitt em portas livres, divisor de sense 1120/100 ohm e proposta de feedback 57,4k/10k para 5,392 V internos. Oito CIs/132 pinos; 48 cortes do mestre de teste, quatro escritas reais da CPU interrompidas e retomadas, scan, 64 cenários de hold-up e 24 de linha RC. Hipóteses, negativos e ERC parcial não aprovado em docs/engineering/NET21.md.

Atualização NET-20A, 26/11/2026: oito CIs de reset/distribuição, integração digital de domínios, monitores SRAM independentes de SAFE, 48 cortes em RAM/VRAM, CPU/relógios/teclado e hold-up condicional revisado. Registrada lacuna de CL do supervisor; nenhuma aprovação física inferida. Ver docs/engineering/NET20.md.

## 26/11/2026 — NET-19A, integração CPU/teclado e correção temporal

- MMIO/colunas procedurais substituídos por pinos e temporizador real da NET17; arquitetura e mapa preservados.
- Nova folha de controlador com três AHC174 no lugar de HC174, mesma lógica, 31 CIs e 526 pinos; retorno aos HC174 reproduz a violação temporal.
- 6.886 vetores ideais, dois cenários temporizados reduzidos, programa/quadro completo e raw scan na CPU passaram; negativos e falhas intermediárias preservados.
- Monitor de COMMIT confere permissão amostrada no registrador; seed de epoch e snapshot de lançamento corrigidos com evidências. Reset/energia global e produção permanecem pendentes.

## 26/11/2026 — Exportação local e fechamento das lacunas REV33/REV76

- Quatro registros JSON de conversa, leituras derivadas, 240 arquivos em bytes originais e duas Pages, com origem/hashes e preservação das cópias anteriores.
- REV33 e REV76 executadas em cópias temporárias: saídas JSON idênticas; 196.608 roundtrips históricos reproduzidos.
- 33 conteúdos ausentes e 171 registros com 72 IDs de origem não exportados mantidos como lacunas. diagnostic.asm original continua ausente.
- Outros dados da conta permanecem locais; fontes exploratórias posteriores não foram promovidas a circuito ou revisão completa.

## 26/11/2026 — NET-18, supervisor candidato e energia condicional

- Variante nativa de seis CIs/100 pinos limita RESET a uma entrada e mantém inibição antes dos bancos nos testes digitais.
- 64 redes de reserva, 16+16 cantos DC e negativos completos; 456 CIs candidatos inventariados sem consumo fictício.
- Modelo original TPS63070/ZIP preservado; tentativas de compatibilidade/convergência não concluíram, sem aprovação de regulador.
- Cinco violações ERC parciais e limites de POR/reverso/carga documentados; fabricação permanece pendente.

NET-15 — 25/11/2026: acrescentados MMIO/teclado por pinos e controlador que aguarda acomodação de colunas; matriz, cortes e RC condicional verificados, intermediários e negativos preservados. Não integrado ainda ao programa completo CPU/raster, sem fabricação liberada.

## 25/11/2026 — NET-14C, integração CPU/vídeo e correção de clock

- Variante nativa de um pino impede truncamento assíncrono do clock de backend; teste negativo reproduz o circuito anterior.
- CPU/guardas/segurança e boot/quadro ideal completos com raster por pinos; imagem igual e SRAM inicialmente desconhecida.
- 1.062 instruções temporizadas e 1.700 cortes em sete lotes dos 26 índices, com hipótese binária explícita na fronteira de reset.
- Recovery estrito continua rejeitado, analógico/MTBF não aprovados. Processo monolítico interrompido sem RESULT preservado como incompleto.
- MMIO físico, DAC/oscilador, reset global, cargas/PVT/PCB e protótipo seguem pendentes.

## 25/11/2026 — NET-14B, raster/captura por pinos

- Esquema parcial de 35 CIs/582 pinos, contadores assíncronos, fases registradas, captura e SLOT derivados do XML.
- Três cenários de dois quadros ligados à memória/controlador NET-13; 16 cortes digitais fora da abertura de recovery e quatro negativos.
- SLOT tardio e cadeia de HSYNC corrigidos a partir das falhas preservadas. Limite do monitor AHC74 conferido/corrigido no datasheet.
- ERC parcial: 42 violações sem exceções. CPU/quadro integrado, PVT/cargas/CDC/DAC/energia/PCB continuam pendentes.

## 25/11/2026 — NET-14A, contrato de vídeo e lista consolidada

- Lista atual de testes, pendências e critérios de revisão, separada dos roadmaps históricos.
- Pré-projeto de fases/raster ligado às netlists NET-13: dois quadros, 153.600 pixels visíveis, 2.012 escritas concorrentes e 32 posições de concessão.
- Negativos de dados, setup e hold detectados; falha inicial de cobertura da fixture preservada.
- Orçamento temporal condicional rejeita meia fase e ligação dos HC74/HCT574 citados ao mestre; captura em fase 3 ainda depende do circuito real e margens de carga/skew/reset.
- Sem novo raster KiCad, DAC ou liberação de fabricação.

## 25/11/2026 — NET-13, chips de memória e barramento

- Nova interface de 28 CIs/576 pinos com SRAM/EEPROM, buffers HCT, muxes AHCT e 24 pull-ups.
- Variante separada de controlador com janela registrada: 30 CIs/510 pinos; controle anterior reproduz disputa no teste negativo da nova interface.
- Percurso de todos os endereços, cenários temporizados/Hi-Z, dados de vídeo e RC com carga excessiva rejeitada.
- Boot completo com SRAM inicialmente indefinida e imagem EEPROM exportada por hash; sem abortos nessa execução.
- Critérios de carga, reset sequenciado e ERC parcial permanecem explícitos; sem produção liberada.

## 25/11/2026 — NET-12, controlador de acesso à memória

- Novo esquema de 28 CIs/478 pinos, pedido sincronizado, payload retido no reset, MDR e strobes físicos.
- Posse de VRAM independente da espera por retirada do pedido; BUS_ACTIVE registrado e flags de leitura/escrita separadas.
- Três cenários isolados com 890 transações e 128 cortes por cenário; três negativos detectados.
- Integração ideal completa com 26 instruções, guardas e programa/quadro; integração temporizada reduzida passou.
- Distinção explícita entre commit do periférico e confirmação à CPU; fontes/intermediários preservados. ERC parcial: 129 violações, sem produção liberada.

## 25/11/2026 — NET-11, decodificador de memória

- Novo esquema de 32 CIs, 512 pinos, mapas/bancos preservados e seis selects MMIO exatos.
- 4.194.305 verificações por modo ideal/com atrasos, dois negativos; integração ideal completa e temporizada reduzida aprovadas.
- Modelo combinacional: caminho máximo 251 ns; ERC parcial mantém 85 violações.
- Onze PDFs oficiais de candidatos com URLs/hashes; controladores/periféricos físicos e produção continuam pendentes.

## 25/11/2026 — NET-10, união global da CPU

- Nova hierarquia KiCad e simulação do XML, com 17 HC125 adicionais para distribuição: 283 CIs, 566 componentes, 4.892 pinos.
- Regressões ideal/com atrasos, negativos de pinagem e registros das falhas intermediárias; sem alterar snapshots anteriores.
- KiCad 10.0.8 separado; ERC com 56 violações retidas. Sem liberação de fabricação.

# Histórico preservado

## NET-09 — 25/11/2026

X síncrono de 18 CIs e variante nativa do controle com EXEC_ACCEPT/WRITE_MODE explícitos; mesmas funções, fontes anteriores intactas. Matriz ideal/temporizada, negativos e regressão completa repetida após explicitar as ligações. Variante HC191 preservada para comparação. União global da CPU e sistema físico seguem em trabalho, sem liberação para fabricação.


## NET-08 — 25/11/2026

Controle de execução, guardas de pilha, fault e retire com 51 CIs derivados do esquema. Bancadas isoladas ideal/temporizada, dois negativos e regressão integrada completos. Logs preservam a falha inicial de polaridade MEM_N_0. Próximo X por pinos em trabalho separado; fabricação não liberada.


## NET-07 — 25/11/2026

PC e caminho de endereço de 45 CIs derivados do esquema KiCad, regressão completa e testes negativos em verification/net07. Imagens/FAQ de membrana fornecidas pelo usuário preservadas com provenance e referência de contatos em docs/engineering/KEYPAD_CONNECTOR.md. Autorizada continuidade pelas etapas restantes; fabricação não liberada.


## NET-06 — 25/11/2026

Registradores A/B/EA, Z/C e mux de dados a partir do esquema KiCad, com 40 CIs e adaptador separado da NET-05. Matriz de seleção/carga/retenção nos dois modos, reset, oito violações temporais esperadas e regressões integradas em verification/net06. Preservado o ensaio inicial que falhou por ausência de pulso de reset na fixture; rodada final usa reset explícito. Fontes anteriores intactas. Relatório docs/engineering/NET06.md; sem liberação para fabricação.


## NET-05 — 25/11/2026

ALU de 8 bits com 49 CIs, esquema nativo, XML, mapa de pinos e simulação derivada das conexões; adapter separado da NET-04. Preserva carry sem empréstimo e flags dependentes do valor selecionado. Verificação exaustiva ideal/temporizada, análise de caminhos do modelo, regressões integradas e falhas intencionais em verification/net05. Fontes anteriores preservadas. Relatório docs/engineering/NET05.md; sem liberação para fabricação.


## NET-04 — 25/11/2026

Banco parcial de microcódigo com 34 CIs: esquema/pinos/XML e simulação derivada, integração sem alterar as ROMs recuperadas, retenção da palavra em WAIT e decodificação de SP. Correção nova da fase de direção DEX, fontes anteriores preservadas. Regressões nas duas configurações de X, monitores temporais e casos negativos em verification/net04; relatório docs/engineering/NET04.md. Não constitui liberação para fabricação.


## 25/11/2026 — NET-03, transações derivadas do esquema

- Controle em HC174/HC74/portas, com captura e retenção de endereço/dado/modo/MDR em HC377.
- Esquema parcial com 17 CIs e 17 desacoplamentos propostos; 304 pinos conferidos e HDL gerado do XML KiCad.
- Rearme exige retorno de START/ACK; fontes podem mudar após captura sem alterar a transação ativa.
- Distribuição de clock/clear, orçamento de carga, monitores e testes negativos; regressões com SP da NET-02 e CPU das ROMs.
- Interface CMOS e validações digitais explícitas; sequenciador ROM, condicionamento elétrico e produção permanecem pendentes.

## 25/11/2026 — NET-02, banco SP derivado do esquema

- Esquema parcial SP com 12 CIs e 12 desacoplamentos; 220 pinos conferidos, HDL derivado da netlist KiCad.
- Armazenamento HC273 com bit 15 codificado, soma SP±1 compartilhada e direção distribuída por HC125.
- Bancadas de todas as direções/valores, retenção, reset, atrasos selecionados, falhas intencionais e regressão da CPU integrada.
- Base RTL-01 e snapshots históricos preservados; controle físico e liberação de placa ainda pendentes.

## 24–25/11/2026 — integração de emulação RTL-01

- CPU HDL comandada pelas ROMs binárias originais, memória/MMIO, arbitragem VRAM e raster ideais.
- Adaptador de carga e seleção entre X RTL e banco funcional HC191/157/377, preservando o esquema parcial anterior.
- Diagnóstico novo com boot EEPROM → RAM e imagem VGA; bancadas de instruções, ALU, reset/energia, WAIT e pausas de RUN.
- CALL/RET verificam dois bytes antes do primeiro acesso de pilha; os limites foram exauridos para todos os valores de SP e boot.
- Validação funcional separada de netlist física, temporização integrada e liberação de produção.

## 24/11/2026 — desenvolvimento 9.8.4.2

- Ferramentas Icarus Verilog 12.0, ngspice 42 e KiCad CLI 7.0.11 preparadas no WSL Ubuntu.
- Modelos novos HC191/157/377, banco de carga de 16 bits e sequenciador de referência, mantendo a CPU e arquivos históricos intactos.
- Duas rodadas de 393.235 verificações de valor aprovadas; modelo HC191 exercitado e sete violações temporais intencionais detectadas.
- Primeiro esquema parcial do banco X, com 20 componentes e 188 pinos; mapa conferido contra a netlist exportada. Controle físico, SP-1, ERC/DRC e produção continuam pendentes.

## 24/11/2026 — migração para GitHub

- Inspeção do remoto vazio e das pastas locais, recuperação dos pacotes 9.3, 9.8.3 e incremento 9.8.4.1.
- Preservação de arquivos originais, leituras de quatro conversas e duas páginas, com capturas adicionais da interface.
- README, AGENTS, arquitetura, decisões, roadmap, provenance, inventário e registro de lacunas.
- Execução local das bancadas existentes em cópias temporárias, preservando a falha por diagnostic.asm ausente.
- Comparação das quatro lanes de ROM regeneradas com os binários originais.

## Sequência histórica recuperada

Nova conferência: acervo salvo em `C:/Users/gabri/projetos/isa1`, arquivos locais adicionais preservados e modelos 7.4/7.5 reexecutados com resultados iguais aos registros existentes. Downloads novos pelo chat compartilhado bloqueados com `ERR_BLOCKED_BY_CLIENT`; completude integral não confirmada. Ver `docs/RECHECK_SHARED_CHATS.md`.

| Revisão | Conteúdo e limite de evidência |
|---|---|
| 7.6 / REV76 | Auditoria estrutural, divergência de convenção de pilha, sete opcodes pendentes naquele estágio; não emulador completo |
| 7.7–7.9 | CPU simbólica executável com X e conjunto de 26 opcodes, indicada no cabeçalho de cpu.py posterior |
| 8.x | Integração de modelos digitais, teclado e regressões; snapshots individuais não recuperados integralmente |
| 9.2–9.3 | Proteção de escrita/reset, cancelamento por epoch e recuperação; ZIP 9.3 preservado |
| 9.4.x | Microcódigo codificado e controle horizontal, incorporados aos arquivos posteriores |
| 9.8.1 | Sequenciador/ROM, incorporados ao pacote posterior |
| 9.8.2 | ALU booleana integrada ao controle; README preservado cumulativamente |
| 9.8.2.1–9.8.3 | Seleção de ALU, flags e aritmética de 16 bits em blocos isolados; ZIP 9.8.3 preservado |
| 9.8.4 | Análise arquitetural/BOM preliminar em conversa; não nova bancada relatada |
| 9.8.4.1 | Contadores candidatos e limites de pilha isolados; ZIP chamado rev984 preservado |

Esta tabela não substitui o histórico original nem atribui data/autoria de commit às revisões. Resultados de engenharia física continuam pendentes.
NET-16A/B — 25/11/2026: ensaios RC de ordem de reset, triagem que rejeita retenção insuficiente, esquema candidato de cinco CIs e liberações CPU/backend. Cortes/pausas e abertura de recovery testados sob hipóteses explícitas; rejeição estrita e ERC parcial de seis violações preservados.
NET-17 — 26/11/2026: acrescentada variante para alvo condicional de 500 Ω, com quatro resistores série, pull-ups recalculados, espera de 2,60 ms e proteção da habilitação tardia por AHC74. Bancadas elétricas/digitais e contrato host de cancelamento/debounce/fila registrados. Originais, hipóteses físicas e rejeição estrita de recovery preservados; sem liberação de placa.


## 2026-11-26 — NET-25 experimental

- Novas folhas de drenagem/armamento e modelo warm calibrado;32 cortes selecionados e vetores ideais passam.
- Preservadas falhas de clock frio sob CLR0 e recovery de reset breve. Variante não promovida.
- Hipótese apenasHDL de reset local emP1 passa156 cenários funcionais; clock frio continua aberto. Estudos de próxima variante não contam como implementação.


## 2026-11-27 — NET-30, regressões próprias concluídas

- Quatro cenários de dois quadros temporizados e boot ideal132197instruções/76800pixels idênticos passaram; SRAM do boot inicialmente desconhecida e nenhum abort.
- Metadados de títulos/datas corrigidos após os jobs, com grafos XML e modelos/JSONs invariantes; originais e falha intermediária de exportação preservados.
- NET30 adotada como candidato digital para continuidade, sem liberação física; fulltimed próprio preparado, ainda sem resultado final.

## 2026-11-26 — NET-30 em validação

- Três variantes nativas com quatro canais AHC125 livres,15pinos alterados, sem CIs novos; união até quatro entradas contadas, sem alegação de carga extraída.
- Conferidos XMLs/ERC parcial e regressões de instruções/memória/cortes; quadros/boot ideal ainda em validação no checkpoint.
- Preservado watchdog da primeira bancada de quadros e diagnóstico de reset frio insuficiente; nova tentativa com50us não altera modelos/monitores.
- Ensaios ativos mantêm fontes congeladas e limites próprios; resultados NET27/NET30 não são intercambiáveis.

## 2026-11-26 — NET-29 estrutural

- União estrutural por fronteiras HDL, com todos os pinos dos sete XMLs conferidos e quatro negativos do leitor.
- Quatro redes acima do orçamento preliminar: WDATA0 com6entradas; SELECT_IO/BOOT/H2 com5. Proposta com canais AHC125 livres ainda não implementada.
- Fontes da execução NET27 preservadas; nenhum novo resultado completo temporizado ou circuito corrigido foi declarado.

## 2026-11-26 — NET-27 preparação e NET-28 documental

- Executor completo temporizado com logs, snapshots e limites de recursos; cinco verificações reais do executor passaram, sem alegação de boot completo temporizado aprovado.
- Ledger de34 famílias/configurações, fontes primárias/hashes, parcelas estáticas/ativas e resistivas condicionais; consumo global permanece aberto.
- Lista corrente de testes conciliada com NET26, incluindo recuperação REV33/REV76 e falha histórica diagnostic.asm preservada.
- Publicação documental independente dos arquivos mutáveis da tentativa NET27 ativa; fontes do ensaio não foram alteradas.

## 2026-11-26 — NET-26

- Novas folhas de reset localP1, clock direto do controlador e AHC174 no teclado, com +1CI local e predecessores preservados.
-156cenários estritos/128combinações, três negativos,48cortes SRAM/oito CPU, vetores ideais/temporizados e boot/quadro ideal passaram.
- Inventário460CIs+2módulos ACH; ERC parcial49/13/25 violações e fechamento global/produção continuam abertos. CVC pesquisado e não adotado; programa inteiro temporizado permanece pendente.
