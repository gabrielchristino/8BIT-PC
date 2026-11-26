Recuperação histórica, 26/11/2026: REV33/REV76 agora têm fontes completas e reprodução simbólica em cópias temporárias, com saídas idênticas. Não alteram a aprovação da CPU atual nem os bloqueios de energia/PCB. Fontes posteriores de prefetch/DAC são exploratórias; ver ../EXPORT_RECOVERY_2026-11-26.md.

Atualização NET-18, 26/11/2026: [supervisor/energia condicional](NET18.md), seis CIs/100 pinos, 64 cenários de reserva e regressões digitais passaram; ERC parcial tem cinco violações. O modelo oficial do regulador não completou. Consumo real, conversão/USB-C/isolamento/POR, integração global, PVT/MTBF e PCB/protótipo continuam abertos.

# Lista consolidada de testes, itens e revisões

Atualizada em 26/11/2026, após NET-17 de teclado candidato para 500 Ω e NET-16A/B de reset, ainda separados da integração CPU/raster NET-14C. Esta lista substitui a leitura dos checkboxes antigos como estado atual; eles permanecem no ROADMAP como registros das respectivas etapas. Não há percentual de placa pronta: uma aprovação de modelo não equivale a aprovação elétrica ou física.

## Evidências aprovadas no escopo de modelo

| Item | Evidência atual | Revisão ainda necessária |
|---|---|---|
| CPU, ISA e datapath | NET-10–13: CPU por pinos, 26 instruções; NET-13 tem 6.886 casos na integração ideal | Temporização global, cargas e circuito completo |
| Pilha e guardas | 524.288 casos na integração ideal; SP vazio 8000h, dois bytes de CALL/RET verificados antes do acesso | Margens temporais e ensaio físico |
| WAIT, COMMIT e handshake | Payload retido, efeitos únicos, pedido/ACK prolongados e cortes digitais; NET-12/13 | CDC/MTBF, mínimos/skew e reset elétrico |
| Microcódigo e registradores | ROMs históricas preservadas; sequenciador/ALU/PC/X/flags mapeados em etapas anteriores | União de fontes, cargas, clocks e alimentação |
| Mapa de memória e bancos | NET-11: 4.194.305 combinações por modo ideal/temporizado | Ligação global a MMIO e periféricos físicos |
| Memórias e barramento | NET-13: todos os endereços; 131.072 escritas, 164.096 leituras e 65.536 leituras de vídeo por configuração isolada | Cargas reais, PVT e encapsulamentos/footprints homologados |
| Troca de drivers | NET-13: intervalo registrado; cenário adversarial passa, controlador antigo é rejeitado | Tempos mínimos, capacitância e integridade de sinal da placa |
| Boot e quadro | NET-14C: 132.197 instruções, 232.576 transações, quadro de 76.800 pixels idêntico com raster por pinos e SRAM inicialmente desconhecida | Programa completo temporizado e depois boot em protótipo |
| Detecção de falhas | Negativos de pinagem, WE, disputa, fases e monitores temporais registrados | Ampliar conforme cada circuito físico é acrescentado |

Evidências: [NET13](NET13.md), [integração ideal](../../verification/net13/cpu/results-ideal.json), [integração temporizada reduzida](../../verification/net13/cpu/results-timed.json), [barramento](../../verification/net13/bus-results.json). Os números têm escopos diferentes e não devem ser somados como uma contagem única de testes. Não foi executado programa/quadro completo com atrasos na NET-13.

## Itens em desenvolvimento ou ainda pendentes

| Prioridade / item | Estado atual | Critério para fechar |
|---|---|---|
| 1. Relógio, raster e captura de vídeo | NET-14C: CPU/boot/quadro ideal com circuito por pinos; variante corrige clock truncado; cortes temporizados têm hipótese binária na fronteira de reset | Cargas/setup/hold/skew/PVT, oscilador e reset/MTBF físico; programa/quadro temporizado completo |
| 2. Concessão física da VRAM | SLOT por pinos, 32 posições exercitadas e integração com CPU/quadro ideal | Fechar cargas/min/max/clock globais e validar placa |
| 3. MMIO e teclado por pinos | NET-17: variante para alvo de 500 Ω, séries nas linhas, 16.384 ciclos e retomada qualificada; 768 cenários elétricos e 5.681 padrões digitais por modo; debounce/fila em referência host | Integrar CPU/raster após energia/reset; implementar scan/firmware de cancelamento, fechar MTBF/proteções/cargas e medir unidades |
| 4. Alimentação e reset | NET-16A/B: ordem WE/estado e liberações CPU/backend em folha candidata; RC/cortes/pausas isolados sob hipóteses explícitas | Supervisor/brownout/hold-up e integração global; níveis/cargas/min/max/MTBF e rampas/cortes físicos. Escrita interrompida continua desconhecida |
| 5. Saída VGA e DAC RGB332 | Dados digitais disponíveis; DAC e conector não fechados | Níveis/correntes/impedância, cargas do monitor, sincronismos, proteção, simulação e medição |
| 6. Temporização global | Cenários de atrasos selecionados e orçamento de captura NET-14A | Setup/hold/recovery/removal, mínimos/máximos, temperatura/tensão, skew/jitter/duty cycle e MTBF; regressão integrada correspondente |
| 7. Elétrica e cargas | Compatibilidade TTL/CMOS estudada; 24 cantos RC de pull-ups com calibração fora do orçamento | Fanout/capacitância por net, SRAM acesso 30 pF/Hi-Z 5 pF, ruído/overshoot, consumo/Delta-ICC e temperatura |
| 8. Esquema global e ERC | CPU e folhas de memória existem; ERC parcial com violações abertas | Unir todos os blocos/pinos/alimentações e resolver erros; não inserir exceções para esconder entradas sem fonte |
| 9. BOM e footprints | CIs candidatos e PDFs identificados; códigos completos não homologados | Conferir função, pinagem, encapsulamento, faixa garantida, montagem e footprint de cada componente |
| 10. Entrada USB-C e distribuição | Requisito de 5 V; circuito completo pendente | Orçamento de corrente, CC/proteção, queda de tensão, desacoplamento/retornos e comportamento ao conectar/desconectar |
| 11. PCB e DRC | Pendente | Posicionamento/roteamento, retornos, clock, memória, VGA, mecânica e DRC revisados |
| 12. Revisão e pacote de fabricação | Pendente | Revisão independente de esquema/BOM/layout; Gerbers, furos, posições e montagem coerentes com a revisão aprovada |
| 13. Firmware de produto | Diagnóstico novo exportado para EEPROM, hash igual ao boot aceito | Monitor/boot definitivo, diagnóstico de bancada e procedimentos de gravação/teste; não confundir com firmware histórico ausente |
| 14. Protótipo e teste de produção | Nenhum ensaio físico de placa realizado | Boot, margens, RAM/VRAM, VGA, membranas, consumo/reset/energia e repetibilidade medidos; corrigir e repetir antes de liberar |

O ERC atual das folhas NET-13 tem 171 e 129 violações, sem aprovação. Isso não é a soma de erros de uma placa unida. O RC de 50 pF não aprova acesso de SRAM nessa carga. Produção permanece bloqueada pelos [critérios completos](PRODUCTION_GATES.md).

## Lacunas históricas separadas da engenharia nova

- `diagnostic.asm` original continua ausente e a bancada recuperada do montador continua com falha conhecida. O diagnóstico novo não resolve essa ausência histórica.
- Conversas completas, revisões intermediárias, REV33 e JSON completo REV76 não foram recuperados integralmente. Ver [LACUNAS](../LACUNAS.md).
- As imagens das membranas são referência de pinagem, não medição de continuidade/resistência/capacitância/bounce das quatro unidades.

## Rotina de revisão

Cada bloco deve registrar entradas/hashes, versões/comandos, bancadas pertinentes, negativos, falhas intermediárias e limites. Repetir regressões afetadas; ampliar a rodada apenas quando nova mudança ou risco justificar. Auditar manifestos históricos nos próprios commits, conferir os bytes publicados e manter originais intactos. Quando houver esquema unido, repetir ERC e análise de cargas globais; quando houver placa, acrescentar DRC e revisão de fabricação; depois validar o protótipo. Nenhuma dessas revisões pode ser antecipada como aprovada.
