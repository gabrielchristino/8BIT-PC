Atualização NET-24 (26/11/2026): dois pinos agrupam o sincronizador de pedidos no mesmo clock, mantendo31CIs. 32 cenários selecionados, 6.886 casos ideais, dois temporizados de1.062, oito cortes da CPU e boot/quadro passaram. Permanece uma rejeição reproduzida: quatro resets com perfil assimétrico geram pulso7,722ns contra20ns no modelo HC74; não são aprovações. Fechar essa rejeição sem enfraquecer o requisito do HC74 e observar WE/bancos nos pinos. ERC parcial135 violações, sem exceções; não aprovar fabricação a partir das regressões funcionais.

Atualização NET-23 (26/11/2026): dois osciladores ACH candidatos no esquema e recepção da CPU por duas Schmitt livres, sem CI adicional de lógica. Partida/falta de clock, pinos SRAM, oito cortes de escrita da CPU e6.886 casos ideais/dois cenários temporizados de1.062 passaram. Carga15pF exige trilhas até5pF e código completo/BOM, jitter/POR e temporização global continuam abertos. 12 violações ERC parciais sem exceções. Simulação de oscilador é comportamental e alimentação qualificada é hipótese; não aprova VDD inválido. Ver NET23.md.

Atualização NET-22 (26/11/2026): variante de vídeo corrige sensibilidade do anel de fases a atrasos distintos de buffers. Shift AHC164/NOR LVC1G27 e carry de linha registrado; 36 CIs, um a mais. 384 combinações de atrasos e256 de assimetria de pulsos, 6.886 casos ideais da CPU, dois cenários temporizados de1.062, boot/quadro completo e cortes de reset passaram; osciladores físicos e fechamento global continuam pendentes. 44 violações ERC parciais, sem exceções. Carga é orçamento; matriz digital não testa slew/jitter/MTBF nem todo PVT. Ver NET22.md.

Atualização NET-21A, 26/11/2026: o conflito aritmético CL/Ci da NET20 tem alternativa em hardware/schmitt_reset, com TPS3808/Schmitt e orçamento 20 pF/condição 50 pF. A proposta depende de novo trilho nominal 5,392 V e qualificação de ripple/regulação/isolamento/corrente/POR. Não confundir fechamento desse orçamento com aprovação analógica. ERC parcial continua com 12 violações, sem exceções; esquema global/PCB/DRC e ensaio físico seguem obrigatórios. Ver NET21.md.

Atualização NET-20A, 26/11/2026: a ordem digital WE/bancos está ligada aos blocos e observada nos pinos SRAM. Não encerra o gate de alimentação: a entrada AHC125 pode ocupar todos os 10 pF da condição temporal do TPS3703. Fechar carga, transições, limiares, POR/hold-up e consumo antes de aprovação física; 12 violações ERC parciais continuam sem exceções. Ver NET20.md.

Atualização NET-19A, 26/11/2026: CPU/memórias/raster agora usam MMIO/teclado por pinos e controlador com três AHC174. Vetores, boot/quadro e raw scan passaram no escopo digital; ERC parcial 135/retorno5. Energia/domínios, clocks/cargas globais, DAC, firmware de eventos, esquema unido e PCB/protótipo continuam pendentes. Ver NET19A.md.

Atualização NET-18, 26/11/2026: janela DC e hold-up são envelopes condicionais; seis CIs/100 pinos de supervisão/reset em folha parcial. Não qualificam conversor, consumo, reverso, partida fria, curto ou VDD inválido. ERC parcial: cinco violações/retorno 5; nenhuma tentativa do modelo oficial TPS63070 completou. Ver NET18.md antes de integrar ou liberar fabricação.

# Critérios para liberar o ISA-1 para produção

Este é o roteiro de evidências para chegar a uma placa produzível. Uma bancada isolada aprovada não marca um bloco ou a placa inteira como liberado.

A [lista consolidada de testes e revisões](VALIDATION_STATUS.md) mostra o estado atual por item, sem tratar listas históricas como novas pendências. NET-14C integra o raster/captura por pinos à CPU no boot/quadro ideal; recovery estrito externo continua rejeitado e o cenário binário separado não aprova metastabilidade/MTBF físicos.

| Etapa | Evidência necessária | Estado atual |
|---|---|---|
| Especificação | ISA, flags, mapa, reset, pilha, boot e periféricos conciliados | Modelos recuperados; divergências ainda documentadas |
| Modelos de componentes | Funções, níveis ativos, carga/reset e comparação com datasheets identificados | Pacotes de CPU e memória NET-02–13 com cenários selecionados; MMIO/raster também por pinos nas NET14C/19A; cargas/PVT globais pendentes |
| Controle/datapath | Carga, retenção e efeitos únicos de COMMIT, inclusive reset/WAIT em fronteiras | SP/transações/microcódigo/ALU/registradores/PC/endereço integrados às 26 instruções; execução/guardas NET-08 integradas; X principal síncrono NET-09; cargas/clock globais em verificação |
| Esquemático completo | Todos os pinos e alimentações, portas, inicialização e interfaces definidos | Esquemas parciais KiCad com pinos/netlists das NET-02–09; CPU global NET-10 existente; decoder/controlador e interface SRAM/EEPROM NET-13 existentes por pinos; MMIO/teclado/raster/reset candidatos separados; união global, clock/fonte/DAC e footprints pendentes |
| Simulação de netlist | Modelo derivado das ligações reais e regressão das 26 instruções | Netlists KiCad dos blocos integradas à CPU, com instruções/guardas/boot/quadro VGA comparados; CPU global por pinos NET-10; memórias/barramento NET-13 integrados com modelos de CIs; boot sem SRAM zerada passou; MMIO/teclado/raster por pinos na NET19A; energia/clock/DAC e união física do sistema pendentes |
| Temporização | Setup/hold com mínimos/máximos, carga, skew, duty cycle e cantos | Cenário parcial e monitores executados; fechamento completo pendente |
| Elétrica | TTL/CMOS, drivers, DAC VGA, memória, ruído, alimentação, reset/brownout e ordem WE/bancos/posse | Datasheets de candidatos e RC de pull-ups NET-13 arquivados; análise elétrica global, cargas reais e medidas pendentes |
| Teclado | Pinagem medida, corrente de linha, bounce, pares/ambiguidades e CPU/VGA | Imagens/FAQ fornecidas pelo usuário indicam pinagem; unidades não medidas, interface/proteção/debounce físicos pendentes |
| ERC | Erros resolvidos e exceções justificadas em esquema completo | KiCad 10 instalado separadamente para ERC; CPU global parcial tem erros/avisos registrados, placa completa ainda pendente |
| Layout | Footprints conferidos, desacoplamento, retorno, conectores e montagem | Pendente |
| DRC e fabricação | DRC, BOM, posições, Gerbers, furos e revisão independente | Pendente |
| Protótipo | Medições de funcionamento, margens e testes de produção | Pendente |

**Atualização de 25/11/2026:** nenhuma etapa parcial autoriza emitir uma liberação de produção. O pedido atual é continuar até os critérios; não representa aprovação de medições inexistentes ou de uma PCB incompleta.

Para cada iteração, registrar revisão, arquivos de entrada, hashes, ferramentas/versões, comandos, saídas, falhas e limitações. Testes negativos devem comprovar que os monitores detectam violações reais. Arquivos históricos não são corrigidos em seu lugar.

As decisões de rotina podem seguir autonomamente. Consultar o usuário quando dependerem de um dado físico não disponível (por exemplo pinagem da membrana), de uma mudança material nos requisitos ou de uma decisão de compra/fabricação.
# Atualização NET-15

MMIO e controlador de teclado agora têm folhas nativas e ensaios isolados, com ERC parcial de 25/135 violações. Envelope de resistência/capacitância é condicional e unidades não foram medidas. Não há integração nova completa da CPU ao teclado nem liberação de fabricação. Reset/energia deve bloquear escritas antes de mudar bancos e liberar registradores com clocks válidos; esquemas unidos, proteção, cargas, BOM/footprints, ERC/DRC e protótipo permanecem obrigatórios. Ver [NET15](NET15.md).
## Atualização NET-17

Teclado tem variante nativa para alvo condicional de contato de 500 Ω e contrato host de até duas teclas. Isso não fecha dados físicos das membranas, firmware de CPU, sincronizadores/MTBF, proteção ou integração global. Corrente de cabo limitada por resistores não aprova carga local dos drivers. ERC parcial tem 25 violações e a placa segue sem liberação. Ver [NET17](NET17.md).
