# Critérios para liberar o ISA-1 para produção

Este é o roteiro de evidências para chegar a uma placa produzível. Uma bancada isolada aprovada não marca um bloco ou a placa inteira como liberado.

A [lista consolidada de testes e revisões](VALIDATION_STATUS.md) mostra o estado atual por item, sem tratar listas históricas como novas pendências. NET-14A acrescenta um contrato executável de raster/captura, não o circuito físico de relógio/vídeo.

| Etapa | Evidência necessária | Estado atual |
|---|---|---|
| Especificação | ISA, flags, mapa, reset, pilha, boot e periféricos conciliados | Modelos recuperados; divergências ainda documentadas |
| Modelos de componentes | Funções, níveis ativos, carga/reset e comparação com datasheets identificados | Pacotes de CPU e memória NET-02–13 com cenários selecionados; periféricos, raster e cargas/PVT completos pendentes |
| Controle/datapath | Carga, retenção e efeitos únicos de COMMIT, inclusive reset/WAIT em fronteiras | SP/transações/microcódigo/ALU/registradores/PC/endereço integrados às 26 instruções; execução/guardas NET-08 integradas; X principal síncrono NET-09; cargas/clock globais em verificação |
| Esquemático completo | Todos os pinos e alimentações, portas, inicialização e interfaces definidos | Esquemas parciais KiCad com pinos/netlists das NET-02–09; CPU global NET-10 existente; decoder/controlador e interface SRAM/EEPROM NET-13 existentes por pinos; união global, periféricos e footprints pendentes |
| Simulação de netlist | Modelo derivado das ligações reais e regressão das 26 instruções | Netlists KiCad dos blocos integradas à CPU, com instruções/guardas/boot/quadro VGA comparados; CPU global por pinos NET-10; memórias/barramento NET-13 integrados com modelos de CIs; boot sem SRAM zerada passou; MMIO/raster ainda modelos, sistema completo pendente |
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
