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
