## ADR E33 — Auditar cargas nas fronteiras antes de aceitar modelos a50pF

26/11/2026, circuito NET26. A união estrutural NET29 confere sete XMLs e
7.810pinos conectados. Quatro redes têm cinco/seis entradas; orçamento
uniforme10pF por entrada+10pF de trilhas resulta60/70pF. É triagem, não
extração ou medição de falha. Aprovação funcional não fecha essa margem.

Não extrapolar atrasos CL50pF, retirar cargas ou chamar bidirecionais/Hi-Z
de capacitância zero. Alternativas: comprovar cargas reais menores ou
distribuir ramos com canais existentes. Preferir investigar AHC125 livres
preservando funções; proposta em NET29_LOADS.md não é circuito aprovado.

Aceitar após pinagem/XML da nova variante, equivalência, tempos/cargas
correspondentes e regressões afetadas. Fontes NET27 ficam congeladas; seu
resultado pertencerá ao circuito NET26. ISA/pilha/flags/CPU/vídeo intactos.

## ADR E32 — Consumo por parcelas, sem promover uma soma de referências a limite

26/11/2026, base NET26. O ledger NET28 cobre32 tipos de CIs e dois osciladores
usando PDFs primários arquivados, com condições e hashes. Manter referências
estáticas/ativas, cargas resistivas condicionais, Delta-ICC e comutação
separadas. Soma473,516mA não é máximo da placa; limite global permanece aberto.
Nenhuma família, pinagem, ISA ou hipótese de hold-up foi alterada.

Alternativas rejeitadas: dimensionar a fonte só pelo ICC estático, adotar CPD
típico como máximo ou tratar1,5A do envelope de falha como corrente calculada.
As tabelas usam condições distintas e não cobrem automaticamente entradas
TTL reais, saída carregada, transientes, fonte/DAC ou perdas de conversão.

Evidência: verification/net28/power-allowances.json e NET28_POWER.md.
Critério de aceitação da fonte: consumo por estado e limites/margens
auditáveis, componentes reais, análise de partida/regulação/reverso/USB-C,
simulação correspondente e medidas do protótipo. Este ADR não fecha esse gate.

## ADR E29 — Agrupar os dois estágios de pedidos sem mudar a lógica

26/11/2026. Base NET23. Mover U4CLK0/CLK1 de BUF_3_3/BUF_3_4 para BUF_4_1
na variante [NET24](docs/engineering/NET24.md). Apenas dois pinos;31CIs e
todo o estado/payload/MDR/ISA preservados. Estados, payload e REQ/MDR ficam
com três cargas cada, orçamento40pF sem extração de PCB.

Datasheet HC74 dá máximo44ns e não mínimo de CLK–Q. Modelo ilustrativo6ns
com buffers1/8,5ns reproduz setup inválido no segundo estágio; não é medida
de silício. Relógio comum elimina essa dependência selecionada entre buffers.
Manter atrasos máximos iguais ocultaria a lacuna; impor CQ mínimo sem fonte
ou relaxar o monitor não é alternativa. Acrescentar/reduzir CIs não é necessário
para este agrupamento. Primeiro estágio analógico/skew de pinos seguem abertos.

Critério funcional: XML delta exato,32 cenários locais, negativo revertendo
um clock, instruções ideal/temporizadas, oito cortes/scans e boot/quadro
com SRAM desconhecida. Esses ensaios passaram; não aprovam toda a temporização.
Quatro ensaios distintos continuam rejeitados por pulso7,722ns/20ns durante
reset, embora regime50% tenha orçamento47,44ns. Registrar falha aberta e
avaliar parada por drenagem em estudo separado, sem presumir implementação
ou enfraquecer guardas. ERC135 e critérios físicos permanecem abertos.

## ADR E28 — Fontes ACH candidatas e recepção Schmitt da CPU

26/11/2026. Base NET22; detalhes em [NET23](docs/engineering/NET23.md).
Construir variante separada com dois módulos configurados ACH25,175MHz/100kHz,
L/C/T/A, carga padrão15pF. Enable em VDD, sem gate por RAW. Uma entrada por
oscilador exige10pF de Ci a5V mais5pF de trilha; confirmar na PCB e na BOM.
Dois Schmitt livres de U2 recebem CPU_OSC e formam CPU_CLK não inversor,
alimentando U7. Oito CIs existentes (sete digitais/um supervisor) preservados,
dois módulos osciladores/capacitores acrescentados; mesma ISA/X/SP/flags/VGA.

Alternativas: dois pinos diretos na fonte da CPU excedem15pF; AHC125 livre
requer qualificar a forma da borda40ns frente ao limite20ns/V. Schmitt evita
essa hipótese sem pacote adicional. Opção ACH50pF não herda automaticamente
tempos da tabela15pF; LVC2G125 tem Ci típico3,5pF em3,3V e não máximo em5V.
Fontes3,3V acrescentam regulação/tradução e outra análise de pulsos. Não se
declara código de compra/carga/jitter/POR homologado por construir o símbolo.

Aceitação digital da etapa: pinos/XML/carga, fonte iniciando desconhecida,
partida interrompida, clock ausente mantendo WE bloqueado, oito cortes/scans
reais nominais/corners, instruções com clocks do circuito, negativos e hashes
conferidos. Não há novo boot completo; os resultados NET22 mantêm seu escopo.
Próxima revisão deve fechar duração de pulsos acumulada, clocks CPU/controlador,
energia/POR/consumo/DAC, firmware de eventos e união/ERC/PCB/protótipo.

## ADR E27 — Compartilhar fases no shift e registrar carry de linha

26/11/2026. Base NET21, decisão e resultados em [NET22](docs/engineering/NET22.md).
O anel anterior falha no modelo com atrasos independentes admissíveis dos
buffers. Adotar variante separada com AHC164, NOR3 LVC1G27 e um novo AHC74:
36 CIs no vídeo, um a mais. Contadores H/RUN/SLOT compartilham ramo, contadores
V compartilham outro; terminais de linha/quadro registrados em P3, clock de
captura exportado depois do buffer. Backend continua sem clear assíncrono.

Alternativas: manter atrasos iguais na simulação não fecha skew; reagrupar só
o anel passou nos ensaios intermediários mas deixa outros caminhos a resolver;
um clock driver diferente exige fonte, carga e condições garantidas próprias.
Preservar CPU/ISA/X/SP/flags/VGA/WAIT/COMMIT e firmware. Fase de reset passa de
P3=1 para quatro zeros, com auto-injeção na primeira borda válida e saídas
inibidas durante partida. Custo de mais um CI aceito por equivalência funcional
e redução da dependência entre ramos. Não remove requisito de análise global.

Aceitação desta etapa: XML/pinos conferidos, fases/raster/SLOT/quadros e reset,
matriz digital selecionada com monitores estritos downstream, regressões
CPU/boot/teclado/WE com marcadores completos e negativos detectados, fontes e
hashes auditados. Não equivale a slew/MTBF/PVT completo ou fabricação. ERC44
sem exceções, oscilador/BOM/energia/DAC/PCB/protótipo permanecem abertos.

## ADR E24 — Integrar teclado por pinos e usar AHC174 no estado do controlador

26/11/2026: integrar o periférico NET17 à CPU/raster/memórias, substituindo MMIO/colunas procedurais; preservar mapa, 26 instruções, X, SP, flags, VGA, WAIT, payload e COMMIT único. Criar hardware/system_access separado, trocando apenas os três HC174 de estado por AHC174 de mesma pinagem. Não acrescentar nem remover CIs: 31 pacotes/526 pinos.

A espera de KEY_READY acrescentou profundidade ao caminho de SLOT. A integração encontrou setup observado de 18,944ns, menor que 25ns do HC174 selecionado. AHC174 tem requisito de 4,5ns nas condições documentadas e melhora também a margem dos outros pacotes de estado, mantendo classe uniforme. Alternativas rejeitadas: esconder a violação, reduzir o requisito do CI antigo, remover espera do teclado, reduzir funções ou alterar frequência VGA para mascarar o caminho. Não é escolha de BOM homologada.

Separar também falha de monitor: saídas de FF podem mudar depois da queda de IO_COMMIT se a captura anterior foi autorizada. Verificar permissão no CLK físico de U1 e rejeitar alteração não autorizada; manter comparação de transações/estados. Bancadas de vetores semeiam fora da borda e antes do epoch; programas completo/scan não recebem estado artificial. Negativos reproduzem atualização inválida, bypass de acomodação e retorno aos HC174.

Aceitação digital: vetores completos ideais, dois cenários reduzidos temporizados, boot/quadro ideal e scan com pausas/cancelamento, sob hipóteses binárias explícitas. Temporização/cargas/clock globais, integração NET18, conversão/POR, firmware de eventos, esquema/PCB e ensaio físico continuam critérios. [Evidências e limites](docs/engineering/NET19A.md).

## ADR M05 — Publicar somente o recorte ISA-1 da exportação de conta

26/11/2026: a exportação local possui 58 conversas. Preservar o pacote original local e publicar quatro registros identificados do ISA-1, conteúdos vinculados por origination_thread_id e as duas Pages já conhecidas. Manter 240 conteúdos byte a byte em diretórios por file ID; conversas são JSON reserializado identificado, com Markdown derivado do caminho atual. Excluir campos de conta da metadata das Pages e não publicar o restante da conta.

Alternativas rejeitadas: enviar a exportação geral; substituir versões de mesmo nome; reconstruir ZIPs ausentes e chamá-los originais; usar metadata de biblioteca para inventar mensagens ausentes ou revisão completa. 171 registros apontam a 72 IDs de origem que não constam dos grafos; 33 conteúdos continuam ausentes nessa exportação. As cópias dos ZIPs já recuperados por outra fonte permanecem válidas.

REV33/REV76 foram inspecionadas e reproduzidas em cópias temporárias, com JSON idêntico. Isso fecha lacunas de fonte e reprodução histórica, sem misturar SP antigo ou reduzir as 26 instruções modernas. README 9.8.4.6.6.7 é explicitamente exploratório; qualquer adoção técnica exige decisão e validação novas. diagnostic.asm da rev983 não foi recuperado e sua falha fica preservada. [Inventário, evidências e limites](docs/EXPORT_RECOVERY_2026-11-26.md).

## ADR E23 — Separar supervisão rápida, reserva isolada e qualificação do conversor

26/11/2026: criar hardware/power_reset separada da NET-16, incluindo TPS3703F6050DSER candidato e divisor 950/100 ohm; mover entrada do inibidor rápido para RAW_BUFFERED. A saída open-drain do supervisor deve carregar somente uma entrada CMOS mais pull-up/trilha, sob orçamento total de 10pF. Pinagem e regressão digital são verificadas; o supervisor é ponto de injeção externo no modelo, sem simulação analógica interna aprovada.

Propor conversão de USB 5V para trilho interno nominal de 5,232V com TPS63070 em PWM, para acomodar limiar de supervisão, resistência de isolamento e queda de trilha. Alternativas de 5V com esse divisor não mantêm a margem DC; TPS3808 tem tempos típicos insuficientes para a prova máxima proposta. Não selecionar BOM apenas pelo nome do candidato. Não mudar ISA/X/pilha/mapa/VGA ou permitir retorno a VBUS.

O envelope de 4,4mF efetivos/20mohm/1,5A e reverso limitado passou em 64 redes com três negativos; consumo de 456 CIs candidatos permanece aberto e não foi inferido do limite de 1,5A. Ripple, fuga SENSE, derating, reverso, rampas e partida fria continuam requisitos, não resultados. A biblioteca oficial do conversor não concluiu no ngspice: preservar falhas e não promover fonte ideal a validação do regulador.

Aceitação desta etapa: XML/100 pinos, reset/pausas, fronteira binária e rejeição estrita, cantos DC e energia condicionais. Fechamento futuro exige corrente real, conversor/isolamento/POR/USB-C qualificados, integração global, cargas/PVT/MTBF, ERC/DRC e protótipo. [Evidências NET18](docs/engineering/NET18.md).

# Decisões recuperadas e registro da migração

## ADR E22 — Alvo de 500 Ω com leitura conservadora e espera após habilitar linhas

26/11/2026: informação comercial de contato até 500 Ω amplia o alvo condicional, sem substituir a medição das quatro membranas. Criar hardware/keyboard_500 separado: colunas 270k/linhas 120k ±5%, séries de 820 Ω ±1%, limiar do contador em 16.384 ciclos e um AHC74 adicional para qualificar a retomada de ACCESS_SAFE no backend. Usar canal livre de U33 e ramo existente de clock; folha final tem 41 CIs/806 pinos, não os 40 da NET-15.

Alternativas: não promover o envelope de sete contatos/150 Ω a aprovação de 500 Ω; não usar driver ideal instantâneo sobre a capacitância como prova de corrente; não permitir que o contador termine enquanto as linhas estão desabilitadas. A variante de 8.192 ciclos passou condicionalmente, mas tinha margem menor; ampliar o contador não custa CI. A habilitação tardia reproduz defeito ao reverter apenas os clears. Hipótese binária nos dois FFs novos conserva a rejeição estrita de recovery e não fecha MTBF.

Aceitar até duas teclas estáticas; com mais bits, cancelar e bloquear até vazio estável, conforme objetivo do planejamento histórico. A referência rev983 mais permissiva para alguns acordes de três teclas permanece original; a nova política restringe esses acordes. Isso evita depender de todos os fantasmas atingirem LOW, sem alterar CPU/ISA/mapa/COMMIT. Contrato de debounce/fila ainda é host, não firmware embarcado, e não prova simultaneidade em quadros mistos.

Aceitação atual: 768 redes RC, três negativos elétricos, 5.681 padrões por modo digital, espera/retomada e política exercitadas; ERC parcial 25 violações. Critérios futuros: implementar firmware/scan completo e integrar CPU/energia/raster, confirmar R/C/isolação/bounce reais, cargas/ruído/MTBF, BOM/footprints, ERC/DRC e protótipo. [Evidências e limites NET17](docs/engineering/NET17.md).

## ADR E21 — Bloqueio rápido e reset atrasado em dois domínios

25/11/2026: criar hardware/reset_domains como candidato separado, com buffer e RC/Schmitt antes de afirmar reset, dois FFs por domínio para liberar CPU/backend e ACCESS_SAFE exigindo RAW_SAFE_N e ambos liberados. Preservar CPU/ISA/mapa e exigir supervisor externo com pulso/energia qualificados. Não usar o reset de backend diretamente na CPU de clock distinto.

Alternativas rejeitadas: reset direto de bancos pode vencer a inibição de WE; RC sem esticamento de entrada pode ignorar pulso curto; liberação sem esperar o clock da CPU é rejeitada em bancada. Uma triagem otimista também rejeita supervisor de 4,63 V/±2% com 470 uF/−20% e carga hipotética de 0,5 A. Nenhuma escolha de supervisor/hold-up foi homologada. A hipótese binária nos FFs permite testes digitais, mas a rejeição estrita de recovery fica preservada e MTBF permanece aberto.

Aceitação atual: dois envelopes RC de 128 cenários cada, dezesseis configurações de cortes/pausas e dez liberações próximas das bordas por política; ERC parcial com seis violações. Critério futuro: supervisor/regulação/isolamento/cargas/temporização fechados e integração completa CPU/MMIO/memória/raster. Ver [NET16A](docs/engineering/NET16A.md) e [NET16B](docs/engineering/NET16B.md).

## ADR E20 — MMIO por pinos e espera antes de ler colunas

25/11/2026: acrescentar folhas separadas MMIO/teclado e controlador com KEY_READY, preservando endereços, valores, ISA, COMMIT único, payload e posse. Usar drivers baixo/Hi-Z, pull-ups de linha 100 kohm e coluna 150 kohm, Schmitt AHC14, duas etapas de amostragem e espera de 8.192 ciclos de backend após ROW/reset. Não alterar membranas nem adicionar diodos por tecla.

Alternativas: driver push-pull alto foi rejeitado por conflito entre teclas; ausência de polarização de linhas foi rejeitada por fuga IOZ; espera somente em software não protege leituras MMIO arbitrárias. HC14/HCS125 foram consultados, mas não selecionados. A leitura de coluna pendente permanece em WAIT; outras operações não recebem essa espera. O temporizador não é debounce, não evita ghosting e não fecha MTBF.

Aceitação digital: 5.681 padrões por modo, três configurações do controlador e integração isolada do temporizador, com negativos. Aceitação elétrica apenas condicional: 48 cantos dentro do orçamento RC passaram, mas unidades não medidas. Critérios futuros: integrar CPU/raster sob reset/energia qualificados, confirmar R/C/contatos reais, proteger conectores e validar firmware de ambiguidades/bounce/fila. ERC parcial tem 25/135 violações e não libera placa. Evidências e limites em [NET15](docs/engineering/NET15.md).

## ADR E19 — Backend sem clear assíncrono e fronteira de reset explícita

Decisão nova de 25/11/2026: criar hardware/video_system separado e fixar alto o clear do FF de backend, mantendo suas transições em bordas mestre. O caso integrado revelou pulso truncado; o ensaio de reversão de um único pino reproduz a falha. Preservar os demais pinos/35 CIs, raster/ISA/mapa e antecessores. A alternativa de ocultar o monitor de pulsos foi rejeitada; clocks de runtime não passam a ser decodificação combinacional.

Recovery externo não é digitalmente garantido: preservar a rejeição do modelo estrito. Para verificar o sistema, criar modelo separado que marca somente os dois FFs de reset como fronteira assíncrona, conta eventos e testa resolução binária imediata/uma borda depois. Isso é hipótese de verificação, não medição, limite analógico ou MTBF. Não desabilitar monitores posteriores nem apresentar o cenário como aprovação de fabricação.

Aceitação de integração: instruções/guardas/segurança e boot/quadro ideal completo com SRAM não semeada, instruções temporizadas reduzidas, cortes completos dos 26 índices em lotes e negativos de clock. Processo interrompido sem RESULT continua incompleto mesmo com saída zero; somente lotes conferidos aprovam a cobertura de segurança. Firmware/imagem e funções preservados. Fechamento físico ainda exige fontes de clock, reset global/WE/bancos/posse, cargas/PVT/CDC/MTBF e protótipo. Ver NET14C.md.

## ADR E18 — Anel registrado, contadores com clear assíncrono e metadados capturados

Decisão nova de 25/11/2026: implementar NET-14B separada, com fases one-hot em AHC74, raster em LV161A e captura CMOS AHC574 após o receptor HCT244 da memória. O clear assíncrono evita depender de clock dividido durante reset; RUN retém H=0 na primeira emissão. Reset local usa dois FFs antes de liberar o anel, sem alegar MTBF ou brownout fechado. Clocks de runtime vêm de saídas registradas; não usar portas de decodificação como clock. O apagamento ocorre após captura, com sincronismos capturados juntos.

Alternativas: LV163 síncrono exigiria outro caminho para inicializar contadores com clock parado; HCT574 deixava margem insuficiente; AHCT574 consultado tem inconsistência de título/tabela de latch no PDF e não é usado. AHC574 recebe CMOS do HCT244, preservando a recepção TTL e evitando inferir compatibilidade direta da SRAM com CMOS. SLOT inicialmente na fase 1 falhou em setup; registrar na fase 0 a previsão H anterior 160..191 conserva a janela efetiva 161..192. Comparador serial de HSYNC falhou com captura rápida; expressão balanceada preserva 164..187.

Aceitação parcial: XML/pinos, três cenários de dois quadros com escrita concorrente, concessões, 16 cortes digitais/512 pixels e quatro negativos. Cortes de release excluem a abertura de recovery do primeiro sincronizador; análise de metastabilidade e liberação arbitrária permanece pendente. Cargas reais, min/max independentes, integração CPU e reset global ainda são critérios. Nenhuma função da ISA, X, pilha ou VGA é removida; não há alegação de BOM mínima ou fabricação liberada. Evidências em NET14B.md.

## ADR E17 — Testar o contrato de fases antes do raster físico

Decisão nova de 25/11/2026: criar NET-14A como pré-projeto separado, sem promover raster comportamental a circuito implementado. Preservar 160 × 120 RGB332, stride de 256 bytes, quatro repetições verticais e janela de concessão H=161..192. Emissão de endereço na fase 0, backend na fase 2 e captura candidata na fase 3 de quatro períodos do estímulo de 25,175 MHz; alinhar visível e sincronismos à captura. CIs de memória/controlador NET-13 são reutilizados sem alteração.

Alternativas: meia fase não fecha o caminho atual; HC74/HCT574 diretamente no mestre não atendem frequência/pulso nos limites citados. Um pulso dividido e fase 3 são candidatos, não escolhas físicas homologadas. A margem condicional de setup é cerca de 3,66 ns após reservar 5 ns de incerteza proposta; atrasos do contador/decodificação, carga, clock e reset reais podem exigir rever componentes ou pipeline. Nenhuma função da CPU/ISA/mapa/VGA é removida e não há alegação de economia de BOM.

Aceitação deste pré-projeto: dois quadros com endereço/dados/apagamento/sincronismos conferidos, escritas concorrentes fora da área visível, 32 posições de início e negativos de captura prematura/setup/hold. Aceitação do circuito posterior exige KiCad/pinos reais, relógios sem hazards, fanout, mínimos/máximos/PVT/skew, reset, alinhamento e integração CPU. Ver NET14A.md, resultados com hashes e lista consolidada de critérios; não é liberação de produção.

## ADR E16 — Barramentos locais, recepção TTL e janela registrada de escrita

Decisão nova de 25/11/2026: mapear dois AS7C256A/SOJ28 e AT28C256/PDIP28 com barramentos locais separados, receptores HCT244, pull-ups de 3,3 kΩ e muxes AHCT157. A alternativa de compartilhar um único barramento de todos os chips ampliaria os riscos de disputa; aplicar diretamente VOH TTL a CMOS não fecha as margens. Preservar 96 KiB e mapa/ISA; WE da EEPROM fica alto, sem programação em circuito prometida. Seleção ainda é candidata, condicionada às cargas, alimentação e homologação de encapsulamentos/códigos.

O retorno ao vídeo revelou sobreposição de drivers com o controlador NET-12 original, reproduzida por teste negativo. Criar variante separada com DRIVE_WINDOW registrado: escrita habilitada em ACCESS/HOLD, desligada em RELEASE, posse mantida até DONE. Não recombinar fases para criar enable sem analisar hazards. Aproveita canal de FF livre, mas acrescenta dois CIs de lógica/distribuição. Sem alteração de resultados arquiteturais; fontes anteriores preservadas.

Modelar bytes nos CIs, não em arrays paralelos ocultos do adaptador; SRAM inicia indefinida. Fixtures de instruções explicitam padrões, e o boot completo usa FIXTURE_DEFAULTS=0. Abortos de escrita são contados e produzem X, sem rollback ou precisão analógica de toda corrupção. O reset físico deve inibir WE antes de alterar bancos/posse/endereço no chip; isso depende do sequenciamento e de mínimos/skew, ainda não fechados.

Aceitação: pinagem/XML, todos os endereços/offsets e padrões baixa/alta, leituras de vídeo, janelas de concessão/ACK prolongado, cenários adversariais de enable/Hi-Z, negativos, regressão ideal completa e temporizada reduzida. RC separado comprova somente o modelo de pull-up nos orçamentos testados. Carga de leitura SRAM 30 pF/Hi-Z 5 pF e análise real de placa permanecem critérios; não usar orçamento RC 50 pF como homologação temporal. Evidências em docs/engineering/NET13.md.

## ADR E15 — Reter payload no reset e desocupar VRAM antes de esperar o produtor

Decisão nova de 25/11/2026. Controlar memória no domínio do backend/vídeo, sincronizando o pedido por dois HC74 e mantendo a sincronização de ACK existente na CPU. Após reset, aquecimento e observação de pedido baixo impedem replay do pedido antigo. Três HC377 sem clear capturam endereço/dados; flags de leitura/escrita separadas zeram juntas. A alternativa de apagar payload no reset foi rejeitada porque poderia mudar o endereço com WE ainda ativo. Não se promete atomicidade de uma escrita truncada por reset/energia.

BUS_ACTIVE tem flip-flop próprio; CS/OE não são reconstruídos pelo OR de fases one-hot. A VRAM é concedida somente por SLOT síncrono e é desocupada após acesso/hold, antes de manter ACK. Reter a posse até o produtor baixar o pedido foi rejeitado: uma pausa prolongada poderia atravessar pixels visíveis. O raster/concessão físico e a prova dos clocks continuam etapas próprias.

O commit físico externo ocorre antes de ACK, e os registradores da CPU só mudam após confirmação. Fixtures novas mantêm a estabilidade do núcleo em WAIT e verificam mudanças de MMIO na transação pendente apenas durante IO_COMMIT; comparam o estado completo ao retirar a instrução. A alternativa de impor simultaneidade ideal entre gravar um periférico e a chegada da confirmação não representa os atrasos do circuito. Isso muda latência, sem alterar ISA, mapa, flags, pilha ou resultados válidos. Escritas de EEPROM continuam ignoradas.

Aceitação do bloco: pinos/XML consistentes, três cenários isolados com 890 transações/128 cortes por cenário, todas as posições de início de janela, pedido mantido por mais de um quadro, três negativos detectados, regressão ideal completa de CPU/programa/quadro e temporizada reduzida. AHC é candidato fundamentado nos PDFs arquivados, sem alegação de BOM homologada/economia. ERC parcial mantém 129 violações; faltam memórias/barramento reais, limites mínimos/skew/MTBF, elétrica, alimentação e placa completa. Evidência em docs/engineering/NET12.md.

## ADR E14 — Separar decodificação de endereço e pulso de acesso

Decisão nova de 25/11/2026: implementar o mapa de memória/MMIO em portas HC e buffers, mantendo 96 KiB físicos, overlay e bancos. Selects são qualificados por SAFE/ACCESS e comparações MMIO exatas. A alternativa de ligar decodificação diretamente a WE foi rejeitada por hazards e falta de retenção/commit; o controlador de acesso continua uma etapa própria. Não muda a ISA válida ou o mapa posterior. Escritas em EEPROM continuam ignoradas pelo modelo, sem programação física prometida. Aceitação do decoder: todos os endereços/bancos/habilitações em cenários ideal/com atrasos, negativos e integração ideal completa com CPU. O ensaio temporizado integrado é reduzido, não aprovação completa. Fabricar exige backend físico, TTL/CMOS, conflitos OE/WE, clock/CDC, cargas globais e ERC/DRC do sistema. Evidência em docs/engineering/NET11.md.

## ADR E13 — Unificar pinos e distribuir cargas antes dos periféricos

Decisão nova de 25/11/2026. Construir uma nova hierarquia KiCad a partir dos oito bancos preservados e gerar a CPU do XML exportado. Usar a saída física SAFE_CORE e distribuir sinais com HC125 quando ultrapassarem quatro entradas. A alternativa de ligar somente módulos HDL esconderia cargas entre blocos; otimizar a contagem de CIs antes da equivalência dificultaria localizar regressões. Impacto: nenhum opcode, flag, mapa ou convenção de pilha válido muda; acrescentam-se 17 CIs de distribuição, sem alegar otimização. Aceitação digital: correspondência de 4.892 pinos, ausência de drivers conflitantes/entradas flutuantes internas, negativos detectados e regressões completas ideal/com atrasos, incluindo quadro. ERC com 56 violações e ausência de memória/periféricos físicos impedem liberação da placa; quatro entradas por net não substituem análise capacitiva/temporal. Evidência em docs/engineering/NET10.md.

## ADR E12 — X síncrono e controle explícito nas interfaces

25/11/2026: X principal em HC273/283/157, com carga EA e ±1 síncronos; preservar HC191 como alternativa de referência. Não se alega economia contra dez pacotes sem o respectivo controle físico. A escolha fecha uma implementação sem carga assíncrona adicional, mantendo funções/ISA/ROMs. Expor EXEC_ACCEPT já físico e usar um inversor livre para WRITE_MODE em variante separada do controle. Aceitação: todos os valores X/modos/enables ideal/temporizado, negativos de ligação, instruções/segurança/guardas e boot/VGA nas duas variantes; revisão global de fanout/clock ainda exigida. Ver NET09.md.


## ADR E11 — Execução one-hot, pedidos retidos e guardas por portas

25/11/2026: HC174 mantém RESPONSE/DROP/X_LOAD e flags, EXEC implícito; portas geram retenção e transições, guardas por limites binários de SP, fault/retire. Alternativa de FSM binária economiza bits mas acrescenta decodificação/hazards; START combinacional direto de microcódigo não preserva a transação. Aceitam-se 51 CIs sem alegar economia. Preservam-se ISA, semântica de WAIT/COMMIT, preflight de dois bytes e conclusão durante pausa. Aceitação: guardas todo SP/overlay/checked, HALT/handshake, falhas introduzidas, CPU/segurança/guardas/boot/VGA nas duas configurações. O erro inicial de polaridade MEM_N_0 é preservado e corrigido no trabalho novo. Sem fechamento temporal global. Ver docs/engineering/NET08.md.


## ADR E10 — PC síncrono e árvore de seleção de endereço

25/11/2026: dois HC273, quatro HC283 para incremento e HC157 para próximo PC/retenção e endereço; portas reutilizam PC_N físico e Z anterior. Alternativas: contadores com carga assíncrona exigiriam novas fases de captura/liberação; barramento tri-state exigiria exclusão de drivers/turnaround. A árvore evita disputa por construção, sem alegar menor BOM. Preservam-se wrap, desvios, endereço SP/SP−1 e captura pela NET-03 antes de WAIT. Aceitação: 2.097.152 casos PC e 524.288 padrões/seletores por modo ideal/temporizado, regressões completas e rejeições intencionais. Limites: cenário temporal isolado, sem placa liberada. Ver docs/engineering/NET07.md.


## ADR E09 — Registradores com realimentação e Z sobre dado selecionado

Decisão de 25/11/2026: quatro SN74HC273 para A/B/EA com HC157 de realimentação, HC74 para Z/C com retenção por portas e árvore HC157 para origem do dado. Reusar DST_N/FLAGS_N físicos da NET-04 e manter clock positivo comum; EXEC_ENABLE ainda deriva da qualificação RTL da execução. Alternativas: HC377 exigiria resolver clear; clock por enable foi rejeitado por introduzir hazards; bancos tri-state exigiriam exclusão/turnaround adicionais; outra codificação de flags poderia compactar pacotes, mas ampliaria a análise de reset e retenção. Z continua testando o dado selecionado, incluindo cargas de memória; C recebe carry somente em flags=2. Preservam-se ISA, ROMs, X, pilha e VGA. Aceitação: matriz de 262.144 casos por modo, quatro cortes de reset/energia digital, testes negativos de ligação e oito violações temporais esperadas, regressões de CPU/guardas/boot/VGA e auditoria de hashes. Não é BOM otimizada ou temporização global; PC e caminho de endereços permanecem RTL. Ver docs/engineering/NET06.md.


## ADR E08 — ALU combinacional com soma/subtração compartilhada

Decisão nova de 25/11/2026: usar dois CD74HC283 em cascata, XOR para B condicionado e carry-in de subtração, portas HC para lógica/seleção, HC138 para códigos e HC125 para distribuir cargas. Carry de SUB/CMP significa ausência de empréstimo; operações lógicas e códigos inativos preservam carry. A ISA e as ROMs não mudam. Alternativas: somadores separados duplicam aritmética; muxes na seleção podem reduzir os 49 CIs desta base, mas exigem comparar caminhos/fanout/BOM; uma ROM ALU exigiria outros requisitos de níveis, acesso e armazenamento. A base atual prioriza equivalência, sem alegar economia. A saída ZERO da ALU não substitui Z da CPU, que testa o valor selecionado no barramento. Aceitação: todas as 2.097.152 combinações por modo ideal/temporizado, regressões completas de CPU/guardas/boot/VGA, rejeição de falhas introduzidas e auditoria de pinos/hashes. Temporização aprovada somente no cenário isolado; A/B/PC/EA/flags e controle restante continuam parcialmente RTL. Evidência: docs/engineering/NET05.md.


## ADR E07 — Microsequenciador com palavra retida e handshake por tokens

Decisão de 25/11/2026: HC161 para step, HC74 para FETCH e tokens, HC377 para IR, HC157 para máscara FETCH, quatro AT28HC64B-120 e quatro HCT377 para palavra retida, decodificadores HC138/139 e portas/buffers. A fase positiva avança endereço; a oposta captura palavra pendente; CONTROL_READY bloqueia execução durante a troca. Alternativa de ROM combinacional direta foi rejeitada por expor a execução a transientes e não reter controle em WAIT; latch transparente exige outra análise de fases. AT28C64B DS20006432A foi rejeitada por margem garantida nula na entrada HCT; AT28HC64B 0274L oferece margem DC parcial de 0,4 V nas condições documentadas. Não é BOM final nem fechamento elétrico. Preservam-se as quatro imagens originais, opcodes e pilha. A integração revelou direção DEX amostrada antes da nova captura; o novo adaptador usa a direção já retida, mantendo a fonte anterior intacta. Aceitação: palavras/endereço/decodificação, retenção sob perturbação, regressões de CPU/guardas/boot/VGA nas duas configurações de X, rejeições intencionais e auditoria de hashes. ADVANCE_REQ/EXECUTE_PULSE e demais partes do datapath continuam RTL. Evidência, alternativas e limites: docs/engineering/NET04.md.


## ADR E06 — Transação em fases registradas e payload independente

Decisão de 25/11/2026: usar HC174 para seis fases mais IDLE implícito, portas HC08/32/04, HC74 para amostrar ACK em dois estágios e cinco HC377 para endereço/dado/modo/MDR. Captura e estabilização precedem REQUEST; DONE ocorre depois do retorno de ACK, e LOCK impede repetição por START mantido. O endereço não acompanha SP durante WAIT. Alternativas: FSM binária com decodificação menor em bits mas mais dependência de hazards; descritor HC74 com mux, que adicionaria um pacote neste bloco; reaproveitar diretamente o nível WR da ROM, que não preservaria o modo se a fonte mudasse. A opção aceita mais ciclos e 17 CIs antes da otimização global, mantendo a semântica da ISA e a atualização única. Clock e clear/qualificadores têm ramos HC125 e orçamento de até quatro entradas por sinal interno. Aceitação: pinagem/XML consistentes, fontes alteradas durante WAIT sem mudança do payload, ACK antigo descartado, pedido mantido consumido uma vez, regressões da CPU e testes negativos. Clocks/níveis reais, MTBF, mínimos/máximos/skew, reset analógico e interface TTL/CMOS continuam critérios de produção pendentes. Não se modifica a CPU anterior nem se declara SP_UPDATE/controle ROM físico concluído. Evidência em docs/engineering/NET03.md.

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


## ADR E25 — Separar reset rápido da CPU e bancos que afetam SRAM

26/11/2026. Base NET-19A/NET-18; variante NET-20A, não liberação física.
Decisão: afirmar reset da CPU por RAW_BUFFERED, liberar após bancos e duas
bordas de CPU; manter reset de controlador/decoder/MMIO/posse atrás do RC,
com inibidor rápido e buffers separados. RUN preservado. A CPU não dirige mais
endereço/dado SRAM diretamente: os HC377 sem clear retêm o payload capturado.
Alternativas: limpar todos os bancos imediatamente arrisca mudança de endereço
antes de WE; atrasar também a CPU não é necessário para a retenção e prolonga
atividade arquitetural em falha. Um novo gate assíncrono em RUN criaria outra
entrada temporal. Não mudar ISA/X/SP/flags/VGA nem prometer rollback de byte.

Evidência/aceitação: XML exato de 22 componentes/oito CIs/132 pinos; 48 cortes
ativos com WE alto em até 80 ns antes de bancos, payload retido, nenhum endereço
físico mudando enquanto WE baixo; dois negativos calibram a rejeição. Pausas das
fontes retêm SAFE baixo até ambas retomarem. Raw scan na CPU usa domínios reais.
Orçamento até bancos/decoder sobe a 20 us; hold-up repetido, 64+3 cenários
condicionais. Critério de produção permanece aberto: CL do supervisor, fontes,
transições, cargas/clock/skew/PVT/MTBF, ERC global, PCB e protótipo. Em particular
Ci máximo AHC125=10 pF não deixa margem para trilhas no teste CL=10 pF do
TPS3703; não promover o prazo analógico anterior a garantia. Alternativas de
datasheet preservadas são pesquisa e exigem novo cálculo/circuito/ADR.
Detalhes e comandos: docs/engineering/NET20.md.


## ADR E26 — Supervisor com CL50pF e recepção Schmitt em portas livres

26/11/2026. Base NET-20A, variante NET-21A candidata, sem liberação física.
Decisão: TPS3808G01DBVR com CT aberto/MR alto, pull-up100k, sense1120/100 ohm,
dois inversores AHC14 antes de RAW_BUFFERED. Mesmos oito pacotes de reset;
reutilizar U2 e desabilitar o canal antigo U1. Pinagem DBV explícita; preservar
payload/CPU/ISA/X/SP/flags/VGA e sequência rápida/demorada anterior.
Alternativas: AHC1G125 também tem Ci máximo10pF e não deixa margem no teste do
TPS3703; capacitância típica LVC não demonstra limite garantido menor. Aumento
arbitrário de atraso analógico ou declaração de trilha zero foram rejeitados.
O TPS3808 admite orçamento20pF contra CL50pF e Schmitt recebe subida lenta.

Impacto elétrico: dispersão/histerese do supervisor exige proposta de feedback
TPS63070 57,4k/10k, saída nominal5,392V interna; USB preservado5V. Margens DC de
retomada20,179mV e teto19,049mV dependem dos orçamentos de referência/resistores,
carga/ripple/caminho, ainda não qualificados. Não reutilizar o valor5,232V de
NET18 como se tivesse passado nesta variante. Não alterar o modelo oficial
anterior para declarar uma simulação do regulador aprovada.

Aceitação no escopo executado: XML22componentes/8CIs/132pinos/9NC, 48 cortes
ativos com WE até94ns, quatro cortes de escrita da CPU com reinício completo,
rawscan em duas políticas binárias, 64+3 reservas condicionais, 24+1 cenários
da linha RC e quatro negativos de janela. Proxy Ron/leakage não é modelo do
supervisor. ERC parcial12 violações, sem exceções. Produção exige fonte/POR e
transientes reais, capacitâncias extraídas, consumo, clocks/PVT/CDC/MTBF, DAC,
esquema global/footprints, PCB/DRC e protótipo. Ver docs/engineering/NET21.md.


## ADR E30 — Drenagem síncrona experimental, ainda sem promoção

26/11/2026. Base5a871ff3ddc58986ae1fb7998690bb9ec3711d5b. Status: experimento com falhas abertas.

Trocar U8 vídeo AHC74 por AHC164 de quatro estágios, clear RC independente, condicionar serial do shift de fases e armar bancos por READY|BANK_SYNC1. Mantém36CIs de vídeo e não mexe em CPU/ISA/SP/ROMs. Alternativas: apagar fases assincronamente (reproduz runt ativo), aumentar duty (backend já50%), relaxar guardas ativas (rejeitado), sincronizar reset local em fase distante e reduzir distribuição de clocks (próximas hipóteses).

Evidência:32 cortes selecionados passam, mas padrão frio4 rejeita7,722ns/20ns sob CLR0. RAW50ns/offset39 rejeita recovery em U36_1. Projeção cold diagnóstica permite observar apenas contenção conhecida sob CLR0 e conserva restrição aberta. Hipótese de pacote AHC74 extra local emP1 passou156 casos funcionais com essa mesma restrição fria; não tem esquema próprio e não substitui a variante nativa.

Impacto: fronteira warm de dados/clear passa a ter hipótese binária explícita; não é MTBF/POR qualificado. Futuro pacote local aumentaria vídeo para37CIs. Aceitar somente após esquema real, XML/cargas/guardas estritas, glitches/pausas/partidas, pinos SRAM/CPU/teclado, quadros/boot e orçamento completo. Não promover o experimento pelo sucesso nominal. Ver NET25.md e CLOCK_TREE_STUDY.md.


## ADR E31 — Reset local emP1, clock direto e AHC174 no teclado

26/11/2026. Base64d01218193259dfc3740f71b6af5ecbe154149e. Adotada como variante candidata após regressões selecionadas; sem liberação física.

Problemas: NET25 tem pulso frio7,722ns/20ns e recovery em RAW50ns. Decisão: adicionar dupla AHC74 local emP1 pelo ANDbuffer livre, ligar controlador diretamente a BACKEND conservando uma etapa de folha e trocar U1 do teclado HC174→AHC174 real. Mantém função/ISA/SP/X/ROMs/teclado/VGA, +1CI no vídeo, mesma pinagem/redes da U1. Quatro cargas50pF condicionais no BACKEND; conta selecionada22,72ns/20ns no controlador e7,72ns/5ns no teclado.

Alternativas: máscara SAFE&PHASE_RUN falha em reset breve; três buffers falham em cold; relaxar guardas rejeitado; distribuição Q/QB/inversores é alternativa maior não necessária para estes cenários. Não se usa READY como clear dos bancos antes de WE alto.

Evidência:156cenários estritos,128combinações, três reversões que reproduzem os defeitos,48cortes SRAM, oito CPU/scans, vetores e boot ideal. Compatibilidade funcional/pinagem conferida, porém novo hold0,5ns e caminhos de mux/min-delay entram no futuro STA global. Critérios restantes: fulltimedboot, cargas extraídas/jitter/slew/PVT/CDC/POR/energia, DAC/firmware, união/ERC/footprints/PCB/DRC e protótipo. Ver NET26.md.
