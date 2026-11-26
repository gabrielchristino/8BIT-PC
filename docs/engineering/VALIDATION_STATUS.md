NET-25:32 cortes selecionados passam na drenagem, mas há falhas abertas de partida sob CLR0 e recovery de reset breve50ns/offset39ns. Não considerar o experimento uma correção global aprovada. Projeção diagnóstica só observa contenção durante reset conhecido; OPEN_RESET_CLOCK permanece não qualificado. Hipótese localP1 passou156 cenários funcionais e ainda não tem esquema próprio. Resultados completos e escopos em NET25.md.

Atualização NET-24 (26/11/2026): dois pinos agrupam o sincronizador de pedidos no mesmo clock, mantendo31CIs. 32 cenários selecionados, 6.886 casos ideais, dois temporizados de1.062, oito cortes da CPU e boot/quadro passaram. Permanece uma rejeição reproduzida: quatro resets com perfil assimétrico geram pulso7,722ns contra20ns no modelo HC74; não são aprovações. Escopos e evidências em [NET24](NET24.md); o boot novo foi ideal com SRAM desconhecida, programa completo temporizado segue pendente.

Atualização NET-23 (26/11/2026): dois osciladores ACH candidatos no esquema e recepção da CPU por duas Schmitt livres, sem CI adicional de lógica. Partida/falta de clock, pinos SRAM, oito cortes de escrita da CPU e6.886 casos ideais/dois cenários temporizados de1.062 passaram. Carga15pF exige trilhas até5pF e código completo/BOM, jitter/POR e temporização global continuam abertos. Os números e resultados de instruções são conferidos em [NET23](NET23.md), sem herdar boot NET22 como nova execução.

Atualização NET-22 (26/11/2026): variante de vídeo corrige sensibilidade do anel de fases a atrasos distintos de buffers. Shift AHC164/NOR LVC1G27 e carry de linha registrado; 36 CIs, um a mais. 384 combinações de atrasos e256 de assimetria de pulsos, 6.886 casos ideais da CPU, dois cenários temporizados de1.062, boot/quadro completo e cortes de reset passaram; osciladores físicos e fechamento global continuam pendentes. Evidências e escopos em [NET22](NET22.md); resultados integrados em verification/net22. Não somar coberturas sobrepostas.

Atualização NET-21A, 26/11/2026: [supervisor/Schmitt candidato](NET21.md) acomoda orçamento de 20 pF contra CL=50 pF especificado, preservando oito CIs. 48 cortes ativos, quatro com CPU real, scan temporizado em políticas 0/1 e SPICE condicional passaram. A janela DC proposta de 5,392 V tem margens pequenas; consumo, regulador/isolamento/POR e circuito físico não qualificados. Próximo: fontes de clock e fechamento global de energia/DAC/cargas, firmware de eventos, ERC/PCB/protótipo.

Atualização NET-20A, 26/11/2026: [reset integrado](NET20.md) por pinos, CPU rápida e bancos atrasados; 48 cortes ativos, dois negativos e raw scan ideal/com atrasos, com parada de clocks. WE bloqueado em até 80 ns nos cenários executados. A condição CL=10 pF do supervisor não comporta Ci máximo do AHC125 mais trilhas; hold-up permanece condicional. ERC parcial: 12 violações. Energia analógica, clock/skew/PVT global, DAC, firmware de eventos, PCB/protótipo abertos.

Atualização NET-19A, 26/11/2026: [CPU/MMIO/teclado integrados por pinos](NET19A.md), com vetores ideais completos, dois cenários reduzidos temporizados e boot/quadro ideal. Raw scan executado na CPU, inclusive relógio parado e leitura cancelada. Três AHC174 corrigem setup do controlador; ERC parcial continua com 135 violações. Reset NET18, distribuição/cargas globais, clock/DAC, firmware de eventos e placa permanecem pendentes.

Recuperação histórica, 26/11/2026: REV33/REV76 agora têm fontes completas e reprodução simbólica em cópias temporárias, com saídas idênticas. Não alteram a aprovação da CPU atual nem os bloqueios de energia/PCB. Fontes posteriores de prefetch/DAC são exploratórias; ver ../EXPORT_RECOVERY_2026-11-26.md.

Atualização NET-18, 26/11/2026: [supervisor/energia condicional](NET18.md), seis CIs/100 pinos, 64 cenários de reserva e regressões digitais passaram; ERC parcial tem cinco violações. O modelo oficial do regulador não completou. Consumo real, conversão/USB-C/isolamento/POR, integração global, PVT/MTBF e PCB/protótipo continuam abertos.

# Lista consolidada de testes, itens e revisões

Atualizada em 26/11/2026, após NET-21 de supervisor/Schmitt e NET-20 de domínios digitais integrados à CPU/MMIO/memórias. Esta lista substitui a leitura dos checkboxes antigos como estado atual; eles permanecem no ROADMAP como registros das respectivas etapas. Não há percentual de placa pronta: uma aprovação de modelo não equivale a aprovação elétrica ou física.

## Evidências aprovadas no escopo de modelo

| Item | Evidência atual | Revisão ainda necessária |
|---|---|---|
| CPU, ISA e datapath | NET-20: 6.886 casos ideais e 1.062 temporizados reduzidos, 26 instruções, com domínios de reset ligados | Temporização global, cargas e circuito completo; regressão correspondente a cada nova variante |
| Pilha e guardas | 524.288 casos na integração ideal; SP vazio 8000h, dois bytes de CALL/RET verificados antes do acesso | Margens temporais e ensaio físico |
| WAIT, COMMIT e handshake | NET-19/20/21: payload retido, efeitos únicos, ACK prolongado, pausa de CPU e cortes nos pinos SRAM; quatro cortes de escrita da CPU real na NET21 | CDC/MTBF, mínimos/skew e reset elétrico; escopos de cortes preservados separadamente |
| Microcódigo e registradores | ROMs históricas preservadas; sequenciador/ALU/PC/X/flags mapeados em etapas anteriores | União de fontes, cargas, clocks e alimentação |
| Mapa de memória e bancos | NET-11: 4.194.305 combinações por modo ideal/temporizado | Ligação global a MMIO e periféricos físicos |
| Memórias e barramento | NET-13: todos os endereços; 131.072 escritas, 164.096 leituras e 65.536 leituras de vídeo por configuração isolada | Cargas reais, PVT e encapsulamentos/footprints homologados |
| Troca de drivers | NET-13: intervalo registrado; cenário adversarial passa, controlador antigo é rejeitado | Tempos mínimos, capacitância e integridade de sinal da placa |
| Boot e quadro | NET-20: 132.197 instruções, 232.576 transações, 76.800 pixels idênticos com resets ligados e SRAM inicialmente desconhecida | Repetir nas variantes seguintes; programa completo temporizado e depois boot em protótipo |
| Detecção de falhas | Negativos de pinagem, WE, disputa, fases e monitores temporais registrados | Ampliar conforme cada circuito físico é acrescentado |

Evidências: [NET13](NET13.md), [integração ideal](../../verification/net13/cpu/results-ideal.json), [integração temporizada reduzida](../../verification/net13/cpu/results-timed.json), [barramento](../../verification/net13/bus-results.json). Os números têm escopos diferentes e não devem ser somados como uma contagem única de testes. Não foi executado programa/quadro completo com atrasos na NET-13.

## Itens em desenvolvimento ou ainda pendentes

| Prioridade / item | Estado atual | Critério para fechar |
|---|---|---|
| 1. Relógio, raster e captura de vídeo | NET22/23 integrados; NET24 confirma backend50% em regime, porém quatro resets com assimetria de bordas violam20ns no modelo | Corrigir/qualificar pulsos de reset e os demais caminhos, cargas extraídas, jitter/slew/MTBF/PVT e programa/quadro temporizado completo |
| 2. Concessão física da VRAM | SLOT por pinos, 32 posições exercitadas e integração com CPU/quadro ideal | Fechar cargas/min/max/clock globais e validar placa |
| 3. MMIO e teclado por pinos | NET-21: raw scan na CPU com domínios digitais, pausa/reset e escrita interrompida retomada; alvo NET17 de 500 Ω/16.384 ciclos e política host preservados | Implementar debounce/fila/cancelamento na CPU, fechar MTBF/proteções/cargas e medir unidades |
| 4. Alimentação e reset | NET-20/21: domínios digitais ligados, WE/bancos observados nos pinos, oito CIs. TPS3808/Schmitt acomoda orçamento20pF/CL50pF e exige proposta5,392V. Hold-up/DC condicionais; regulador oficial não completou | Qualificar fonte/consumo/isolamento/POR/transientes e cargas extraídas, min/max/MTBF e rampas/cortes físicos; byte interrompido continua desconhecido |
| 5. Saída VGA e DAC RGB332 | Dados digitais disponíveis; DAC e conector não fechados | Níveis/correntes/impedância, cargas do monitor, sincronismos, proteção, simulação e medição |
| 6. Temporização global | NET24 agrupa dois clocks REQ,32 cenários locais e regressões passam; pulso de7,722ns permanece rejeitado em4 casos de reset | Fechar rejeição ativa sem waiver, todos os mínimos/máximos, demais grupos/skew/hold/setup/recovery, jitter/PVT/MTBF e circuito elétrico correspondente |
| 7. Elétrica e cargas | TTL/CMOS estudados; NET21 conta16 redes selecionadas, até4 entradas/saída; RC e reservas condicionais | Fanout/capacitância global extraída, SRAM acesso30pF/Hi-Z5pF, ruído/overshoot, consumo/Delta-ICC e temperatura; budgets não são medidas |
| 8. Esquema global e ERC | Folha common_request NET24 tem31CIs/526pinos e135 violações; fonte/reset e vídeo continuam parciais | União real de blocos/pinos/alimentações, resolver ERC e conferir footprints; não somar folhas parciais nem mascarar entrada sem fonte |
| 9. BOM e footprints | Configurações candidatas e PDFs por família; ACH L/C/T/A15pF tem código completo aberto e exige até5pF de trilhas na entrada | Conferir códigos reais, pinagem, encapsulamento/faixa/carga/consumo e footprint de cada componente; não tratar típico como limite |
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
