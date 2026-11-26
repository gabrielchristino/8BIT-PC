Atualização NET-24 (26/11/2026): dois pinos agrupam o sincronizador de pedidos no mesmo clock, mantendo31CIs. 32 cenários selecionados, 6.886 casos ideais, dois temporizados de1.062, oito cortes da CPU e boot/quadro passaram. Permanece uma rejeição reproduzida: quatro resets com perfil assimétrico geram pulso7,722ns contra20ns no modelo HC74; não são aprovações. Prioridade: investigar a drenagem do token descrita em docs/engineering/CLOCK_DRAIN_STUDY.md, ainda não implementada, e repetir os cortes; depois demais clocks/energia/DAC/firmware/união/ERC/PCB/protótipo.

Atualização NET-23 (26/11/2026): dois osciladores ACH candidatos no esquema e recepção da CPU por duas Schmitt livres, sem CI adicional de lógica. Partida/falta de clock, pinos SRAM, oito cortes de escrita da CPU e6.886 casos ideais/dois cenários temporizados de1.062 passaram. Carga15pF exige trilhas até5pF e código completo/BOM, jitter/POR e temporização global continuam abertos. Próximo: largura de pulso e ramos da distribuição global, energia/consumo/USB-C/DAC e união de esquema; firmware de eventos, PCB/DRC/protótipo seguem pendentes.

Atualização NET-22 (26/11/2026): variante de vídeo corrige sensibilidade do anel de fases a atrasos distintos de buffers. Shift AHC164/NOR LVC1G27 e carry de linha registrado; 36 CIs, um a mais. 384 combinações de atrasos e256 de assimetria de pulsos, 6.886 casos ideais da CPU, dois cenários temporizados de1.062, boot/quadro completo e cortes de reset passaram; osciladores físicos e fechamento global continuam pendentes. Próximo: fontes físicas de clock, outros ramos CPU/controlador e temporização global; depois energia/DAC/firmware/união/ERC/PCB/protótipo. Ver docs/engineering/NET22.md.

Atualização NET-21A (26/11/2026): variante candidata de supervisor/Schmitt montada por pinos, com orçamento de entrada, janela DC/hold-up e resets da CPU/teclado/memórias testados condicionalmente. Próximo: fontes físicas de clock, fechamento de fonte/proteções/consumo, DAC e união global; firmware de eventos, PCB e protótipo seguem abertos. Ver docs/engineering/NET21.md.

Atualização NET-20A (26/11/2026): sequência digital global candidata ligada à CPU/teclado/memórias, reset rápido da CPU com payload retido e bancos atrasados, distribuição parcial de clocks/cargas e testes diretos nos pinos WE/endereço. Próximo: fechar interface de carga/limiares do supervisor, energia/clock/DAC e união elétrica; firmware de eventos, PCB e protótipo continuam pendentes. Ver docs/engineering/NET20.md.

Atualização NET-19A (26/11/2026): CPU/raster/memórias integrados ao MMIO/teclado por pinos, 6.886 vetores ideais, dois cenários temporizados de 1.062 casos, boot/quadro ideal completo e raw scan com CPU pausada/reset pendente passaram. Controlador mantém 31 CIs e lógica, trocando três HC174 por AHC174 com limite de setup apropriado. Próximo: domínios de reset/WE e distribuição global de clock/cargas, energia, DAC e união de esquema; debounce/fila na CPU, PCB/DRC e protótipo seguem pendentes. Ver docs/engineering/NET19A.md.

Recuperação adicional, 26/11/2026: quatro registros de conversa, 240 conteúdos e duas Pages preservados; REV33/REV76 reproduzidas sem modificar originais. A recuperação não é integral: 33 conteúdos ausentes e 72 IDs de mensagens de origem não estão nos grafos. Considerar materiais exploratórios posteriores antes de novas decisões; não tratar como implementação pronta. Ver docs/EXPORT_RECOVERY_2026-11-26.md.

Atualização NET-18 (26/11/2026): folha candidata com supervisor e reset de seis CIs/100 pinos, cantos DC, 64 cenários condicionais de hold-up e regressões digitais passaram. Modelo oficial do conversor não completou; consumo/isolamento/POR/USB-C e integração CPU/MMIO/raster continuam abertos. Ver docs/engineering/NET18.md; nenhuma placa liberada.

Atualização NET-15 (25/11/2026): MMIO/teclado e controlador com espera KEY_READY por pinos; 5.681 padrões por modo e 48 cantos elétricos dentro de orçamento condicional passaram. As membranas reais não foram medidas. Próximo: reset/energia e integração CPU/teclado; depois proteção, firmware de teclado, DAC e união da placa. Ver docs/engineering/NET15.md.

**Estado consolidado atual:** [testes, pendências e revisões](docs/engineering/VALIDATION_STATUS.md). As listas abaixo preservam o estado das etapas anteriores; checkboxes antigos não representam pendências atuais sem consultar a lista consolidada.

Atualização NET-14C (25/11/2026): CPU integrada ao raster/SLOT/captura por pinos, boot/quadro ideal completo com SRAM indefinida e imagem idêntica. Variante nativa evita truncar clock de backend por reset; negativo de reversão do pino reproduz a falha. Fronteira assíncrona tem rejeição estrita preservada e modelo binário separado, não MTBF aprovado. 1.062 instruções temporizadas e sete lotes completos de cortes/26 opcodes passaram nesse escopo. Próximo: MMIO/teclado, DAC/oscilador e energia/reset global; depois esquema unido, cargas, footprints/PCB e protótipo.

Atualização NET-14B (25/11/2026): raster/captura/divisão e concessão registrados em esquema de 35 CIs/582 pinos, XML conferido e simulado com NET-13. SLOT antecipado e HSYNC balanceado corrigem falhas reproduzidas; três cenários de quadros, cortes digitais fora da abertura de recovery e negativos registrados. Próximo: integração CPU/diagnóstico/quadro, MMIO/teclado físico, DAC/oscilador e reset/energia global. ERC parcial tem 42 violações, sem aprovação de placa.

Atualização NET-14A (25/11/2026): contrato executável de quatro fases de vídeo ligado à memória/controlador NET-13; dois quadros, todas as posições de concessão e negativos de dados/setup/hold passaram. Meia fase e clock mestre direto nos HC74/HCT574 citados foram rejeitados por orçamento/limites. Captura em fase 3 é candidata condicional, sem raster/clock real homologado. Próximo: construir os CIs/pinos do raster, divisão, captura e concessão, fechar cargas/skew/reset e integrar à CPU. Não há produção liberada.

Atualização NET-13 (25/11/2026): chips de memória e interface de dados por pinos, recepção TTL, mux de vídeo/CPU e intervalo registrado entre drivers. Todos os endereços foram exercitados; boot/quadro passou com SRAM indefinida. Imagem EEPROM do diagnóstico e RC de pull-ups preservados. Próximos blocos: relógios/raster/captura/DAC VGA, MMIO/teclado físico e alimentação/reset sequenciado, incluindo WE inibido antes de mudar bancos/posse. União global, cargas, footprints, ERC/DRC/layout e protótipo ainda impedem produção.

Atualização NET-12 (25/11/2026): controlador de acesso por pinos com payload sem clear, fases de leitura/escrita, sincronização do pedido, MDR TTL e posse registrada de VRAM. Três cenários isolados, integração ideal completa e temporizada reduzida passaram; programa/quadro preservados. Próxima etapa: chips SRAM/EEPROM, multiplexadores/drivers e temporização elétrica do barramento; depois raster/concessão física, MMIO/teclado e alimentação. ERC parcial mantém 129 violações, sem liberação de fabricação.

Atualização NET-11 (25/11/2026): decoder físico de RAM/VRAM/EEPROM e seis endereços MMIO, isolado ideal/com atrasos e integrado à CPU em modelo de sistema. Programa/quadro ideal passaram; ensaio integrado com atrasos é reduzido. Próxima etapa: controlador físico de transações de memória, captura de dados e arbitragem de VRAM; depois raster/saída VGA, MMIO/teclado e alimentação. ERC parcial do decoder tem 85 violações; sem liberação de fabricação.

Atualização NET-10 (25/11/2026): CPU global por pinos em hardware/cpu_global, com distribuição entre blocos e 4.892 pinos conferidos. O ERC tem 56 violações registradas; não há placa liberada. Próximo fechamento: memória/VRAM/MMIO, relógios de vídeo e interfaces elétricas. As listas históricas abaixo não equivalem a módulos físicos concluídos; use os relatórios de cada etapa para distinguir evidências.

# Roadmap de continuidade

## Continuidade — NET-09

- [x] X principal síncrono por pinos e ligações explícitas EXEC_ACCEPT/WRITE_MODE, com regressões completas.
- [ ] NET-10: validar união de todas as netlists da CPU, distribuição global de sinais/clocks e cenário temporal integrado.
- [ ] Mapear sistema físico de memória/VGA/MMIO/teclado e alimentação/reset/clock.
- [ ] Esquema global/footprints/ERC, layout/DRC e arquivos de fabricação; ensaiar protótipo antes de liberar.


## Continuidade — NET-08

- [x] Execução/guardas/fault/retire a partir dos pinos KiCad; testes isolados e programa completo aprovados.
- [ ] NET-09: aceitar X síncrono e integrar CPU principal sem estado procedural de execução/datapath.
- [ ] Fechar memória/periféricos/energia/reset/clock e união elétrica/temporal de todos os blocos.
- [ ] Esquema global, ERC, layout, DRC, pacote de fabricação e validação de protótipo.

Continuar pelas etapas, mantendo a distinção entre modelos, layout verificável e produção liberada.


## Continuidade até a placa — NET-07

- [x] PC, incremento/desvios e seleção de endereços a partir do esquema; regressões completas nas duas configurações de X.
- [ ] NET-08: aceitar controle de execução/guardas/fault após bancadas isoladas e programa completo.
- [ ] Concluir X sem controle simbólico e integrar todas as netlists/cargas/clock/reset.
- [ ] Mapear memória/VRAM/arbitragem/MMIO/VGA/teclado, preservando interfaces e funções.
- [ ] Fechar componentes/BOM, níveis garantidos, energia USB-C, supervisão, temporização global e testes elétricos.
- [ ] Esquema completo com footprints/ERC, layout/DRC e arquivos de fabricação revisados.
- [ ] Medições de protótipo, incluindo quatro membranas, reset/energia, barramentos e saída VGA, antes de liberação.

Usuário autorizou continuar pelas etapas necessárias. As imagens fornecidas indicam a pinagem de referência do teclado; continuidade e características das unidades ainda exigem ensaio.


## Iteração atual — NET-06

- [x] Mapear A/B/EA, flags e seleção interna de dados a CIs, com simulação derivada do XML KiCad.
- [x] Conferir matriz de seleção/carga/retenção, reset e cenário de atrasos; provar rejeições dos monitores.
- [x] Regressão integrada de instruções, guardas, boot e VGA nas duas configurações de X.
- [ ] Mapear PC, incremento/desvios e seleção de endereços, preservando captura antes de WAIT.
- [ ] Mapear controle de execução/guardas/fault restantes e concluir integração física de X.
- [ ] Rever BOM/cargas entre blocos; fechar energia/reset/clock/temporização, ERC/DRC, PCB e protótipo.

Evidência e limites: docs/engineering/NET06.md. Os registros seguintes descrevem as etapas anteriores.


## Iteração atual — NET-05

- [x] Mapear ALU de 8 bits a somadores, portas e buffers; gerar simulação dos pinos exportados do KiCad.
- [x] Conferir todas as entradas/operações/carry nos cenários ideal e com atrasos selecionados.
- [x] Integrar à CPU das ROMs e comparar instruções, guardas, boot e VGA nas duas configurações de X.
- [ ] Mapear registradores A/B/PC/EA/flags e seleção de dados/endereços, preservando captura e WAIT.
- [ ] Comparar alternativas de seleção da ALU para reduzir CIs sem perder funções ou margem.
- [ ] Fechar elétrica/temporização globais, energia/reset, ERC/DRC, PCB e protótipo.

Evidência e limites: docs/engineering/NET05.md. As etapas anteriores abaixo são snapshots de continuidade.


## Iteração atual — NET-04

- [x] Mapear microstep, FETCH, IR, ROMs, retenção e decodificação da palavra a pacotes com pinos e simulação da netlist KiCad.
- [x] Preservar palavras originais, estabilidade durante WAIT e regressões com as duas configurações de X.
- [x] Verificar atrasos selecionados e rejeição de violações temporais; registrar escolha de EEPROM/HCT e limites.
- [ ] Mapear ALU, A/B/PC/EA/flags e controle de execução restante; integrar sem mudar a ISA.
- [ ] Fechar temporização global, níveis/cargas/energia/reset, esquema completo, ERC/DRC e protótipo.

Evidência: docs/engineering/NET04.md. Listas anteriores preservam o contexto e não substituem este estado parcial.

## NET-03 — transações e payload retido

- [x] Mapear fases de captura, estabilização, pedido, drenagem, conclusão e rearme a HC174/portas.
- [x] Capturar endereço/dado/modo e MDR em HC377, com ACK em dois HC74.
- [x] Distribuir clock e clear/qualificadores e conferir o orçamento de entradas por sinal.
- [x] Exportar KiCad para XML/HDL e integrar ao banco SP/CPU das ROMs.
- [x] Testar WAIT, START mantido, reset, ACK antigo, fases de ACK, instruções e boot/VGA.
- [ ] Mapear sequenciador de microcódigo e retenção/decodificação das ROMs a CIs.
- [ ] Gerar SP_UPDATE e demais enables a partir desse controle físico e fechar temporização global.
- [ ] Concluir interface elétrica de memória, reset/alimentação, VGA/teclado, esquema completo, PCB e verificações de produção.

Ver docs/engineering/NET03.md. As fases do barramento agora são uma netlist de CIs; isso não equivale à liberação física de todo o computador.

## NET-02 — esquema e simulação do banco SP

- [x] Mapear armazenamento e SP±1 a HC273, HC157, CD74HC283, HC04 e buffers HC125.
- [x] Exportar netlist KiCad, conferir 220 pinos e gerar HDL das conexões exportadas.
- [x] Testar retenção, reset e todos os valores/direções, ideal e com atrasos selecionados.
- [x] Integrar SP da netlist à CPU preservando ROMs, X, ISA, flags, WAIT e guardas.
- [x] Acrescentar falhas intencionais de ligação/entrada aberta e monitores temporais.
- [ ] Mapear controle de transações/UPDATE e latch de endereço a CIs e ao mesmo fluxo de netlist.
- [ ] Fechar temporização global, cargas reais, elétrica, footprints, ERC/DRC e protótipo.

Ver docs/engineering/NET02.md. Esta etapa fecha a representação física e a equivalência funcional do banco SP, sem fechar a placa inteira.

## Integração RTL-01

- [x] Executar na CPU RTL as palavras reconstruídas das quatro lanes binárias originais.
- [x] Integrar memória/MMIO, arbitragem VRAM, clocks distintos e raster ideais.
- [x] Criar diagnóstico novo com boot EEPROM → RAM e uso dos 26 opcodes.
- [x] Acrescentar comparação de transações/estado, ALU exaustiva e cortes de reset/energia.
- [x] Concluir regressão do X candidato integrado e registrar a rodada completa.
- [x] Checar dois bytes de CALL/RET antes do primeiro acesso e exaurir os limites de SP/boot nas quatro operações.
- [ ] Mapear datapath/sequenciador a CIs e compartilhar netlist entre esquema e simulação.

Ver docs/engineering/RTL01.md. As listas anteriores abaixo preservam o contexto da recuperação; o resultado mais recente deve ser interpretado com o nível de modelo explicitado nessa integração.

## Iteração ativa — 9.8.4.2

- [x] Preparar Icarus Verilog, ngspice e KiCad CLI no WSL Ubuntu.
- [x] Modelar carga transparente HC191, HC157 e HC377 e testar inicialização/carga de 16 bits.
- [x] Executar rodadas lógica e com atrasos selecionados, reset, WAIT e testes negativos dos monitores.
- [x] Gerar esquema parcial do banco X, mapa de pinos e conferir netlist exportada.
- [ ] Mapear sequenciamento e portas a CIs/controle real; comparar custo com alternativas.
- [ ] Fechar temporização com atrasos mínimos, skew e cargas reais.
- [ ] Resolver SP-1 e integrar o controle à CPU com regressão das 26 instruções.

A etapa de carga tem uma bancada aprovada, mas ainda não está fechada como circuito físico completo. Detalhes e critérios em docs/engineering/REV9842.md e PRODUCTION_GATES.md.

As etapas abaixo organizam pendências recuperadas e trabalho necessário para concluir a migração. Não representam revisões implementadas ou datas prometidas.

## 1. Completar a recuperação

- [ ] Recuperar exportação completa das conversas, incluindo ramificações, anexos e imagens.
- [ ] Recuperar arquivos ausentes e revisões individuais de [LACUNAS.md](docs/LACUNAS.md), especialmente rev33 e `diagnostic.asm`.
- [ ] Registrar bytes, hashes e origem; comparar versões antes de qualquer consolidação.
- [ ] Resolver divergências de numeração: REV76 = 7.6; o pacote chamado rev984 corresponde ao estudo 9.8.4.1.

Aceitação: cada material citado tem arquivo recuperado ou ausência identificada; nenhuma alegação de completude sem inventário verificável.

## 2. Estabelecer uma base de desenvolvimento

- [ ] Criar versão de trabalho a partir do snapshot completo rev983, mantendo originais intactos.
- [ ] Recuperar diagnóstico e obter aprovação das bancadas existentes; complementar apenas riscos não cobertos.
- [ ] Conciliar especificação ISA, mapa de memória, boot, pilha e teclado entre o código 9.x e ENG-KBD-01.
- [ ] Validar integração do sequenciador/ROM ao modelo da CPU, não apenas equivalência dos geradores e modelos isolados.

## 3. Fechar os blocos digitais

- [ ] 9.8.4.2 histórica: carga e inicialização segura dos contadores.
- [ ] 9.8.4.3 histórica: resolver SP-1, commit e falhas durante PUSH/POP/CALL/RET.
- [ ] Proteção de pilha e colisões; arbitragem de barramentos; datapath e controle integrados.
- [ ] Comparar contadores, registradores e somadores com BOM e caminho crítico completos.
- [ ] Criar HDL/testbenches com reset, WAIT, CDC, opcodes inválidos e propriedades de segurança.

## 4. Integrar o teclado real

- [ ] Medir pinagem, resistência e capacitância das quatro membranas.
- [ ] Dimensionar linha ativa e proteção; resolver margem de VOL no pior caso.
- [ ] Esquema KiCad com decodificação real e ENABLE; driver, ABI e fila de eventos.
- [ ] Validar pares, trios em L entre módulos, quadros mistos, bounce, cancelamento, fila cheia e carga sobre CPU/VGA.

## 5. Validar hardware e fabricar protótipo

- [ ] Esquemático completo, datasheets identificados por revisão, pinagem e encapsulamentos.
- [ ] Orçamento de alimentação USB-C, reset/brownout, desacoplamento, níveis TTL/CMOS e saída VGA.
- [ ] Temporização com limites máximos, cargas reais, modelos SPICE quando aplicável e formas de onda digitais.
- [ ] ERC/DRC, revisão de layout/BOM e plano de montagem/teste.
- [ ] Protótipo físico e medição de boot, CPU, memórias, VGA e teclado antes de declarar validação física.

## 6. Software do computador

- [ ] Consolidar monitor/boot, diagnóstico, formatos da EEPROM e rotinas seguras de salvamento.
- [ ] Biblioteca de vídeo, teclado e testes de integração de programas.
- [ ] Retomar interpretador BASIC e recursos de uso pessoal somente com requisitos e fontes recuperados.
Atualização NET-16 (25/11/2026): contrato de inibição antes do reset e folha candidata com liberações distintas CPU/backend. Ensaios isolados e negativos passaram sob fronteiras RC/binárias explícitas; recovery estrito continua rejeitado. Próximo: fechar supervisor/energia e conectar domínios ao sistema CPU/MMIO, repetindo regressão integrada. Não há placa liberada.
Atualização NET-17 (26/11/2026): alvo condicional de contato de 500 Ω tratado com variante de resistores, espera de 16.384 ciclos e retomada sincronizada; 768 cenários elétricos e regressões digitais passaram. Política host conservadora de até duas teclas exercitada, com cancelamento/fila e limitação explícita de quadros mistos. Próximo: energia/reset global, integração CPU/MMIO/raster e firmware de varredura/eventos; medidas, BOM/PCB/ERC/DRC/protótipo continuam pendentes. Ver docs/engineering/NET17.md.
