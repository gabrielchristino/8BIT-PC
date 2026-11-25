# NET-12 — controlador de acesso à memória

25/11/2026, base NET-11 `3cac9fca256377186960d106d08d7ccd0ca6c6dc`. Trabalho novo em `hardware/memory_access` e `sim/net12`, sem alterar bancos anteriores. O controlador tem 28 CIs, 28 capacitores propostos, 478 pinos e dez NC. A biblioteca local, esquema KiCad, mapa de pinos, XML exportado e HDL derivado acompanham os relatórios. A folha A1 foi renderizada e inspecionada. Não é uma placa completa ou uma BOM homologada.

Três HC174 armazenam estados/flags; um HC74 faz a sincronização de dois estágios do pedido; três HC377 retêm endereço de 16 bits e dados de oito bits; um HCT377 captura o retorno compatível com TTL. Portas/buffers AHC08/32/04/125 qualificam acessos e distribuem cargas. AHC usa 10 ns no modelo, acima dos máximos selecionados de 9/8,5 ns, a 5 V ±0,5 V e CL=50 pF nas tabelas SN74 de −40…85 °C. Os PDFs já preservados e seus hashes constam de `verification/net12/timing-basis.json`. Os demais modelos/monitores são os das etapas anteriores, sem alteração.

O grafo interno limita cada sinal a quatro entradas; não inclui os consumidores dos outros bancos, capacitância real de trilhas/provas, skew ou corrente dinâmica. A futura união de placa precisa recontar essas cargas.

## Protocolo e efeitos

O pedido RAW passa por dois flip-flops. Após reset, três flags de aquecimento e observação de pedido sincronizado baixo são necessárias antes de armar. Um pedido mantido alto através do reset não é repetido. O produtor precisa oferecer esse intervalo baixo e manter o pedido até ACK; a compatibilidade com a CPU é exercitada nas regressões, sem prometer qualquer razão arbitrária entre relógios.

Um aceite captura endereço, dados e flags separadas de leitura/escrita. Os HC377 de payload **não têm reset**: conservam os dados enquanto SAFE desativa os acessos. Apagar o endereço durante WE ativo poderia deslocar uma escrita para outro local. Leitura e escrita usam flags próprias que ambas zeram no reset; não se transforma uma escrita em leitura por inverter uma flag apagada.

| Fase | Função |
|---|---|
| SETTLE0 / SETTLE1 | Acomodar payload e decodificador NET-11 |
| WAIT_SLOT | Esperar a concessão se o destino for VRAM |
| SETUP | Assumir barramento; preparar dados e leitura |
| ACCESS | Um período de WE para SRAM, ou enable de commit MMIO |
| HOLD | Conservar acesso; capturar o retorno ao final desta fase |
| RELEASE | Conservar endereço/dados por mais um período após captura |
| DONE | Desocupar memória/VRAM e manter ACK até o pedido sincronizado baixar |

BUS_ACTIVE é um flip-flop dedicado, evitando reconstruir a posse por uma soma lógica dos estados one-hot. CS/OE permanecem ativos durante a transferência sem depender de transições entre vários Q. WE só qualifica RAM/VRAM e escrita; a janela de EEPROM continua sem programação física e suas escritas são ignoradas. IO_COMMIT é um enable para o relógio do backend, não um novo clock assíncrono.

A concessão de VRAM é uma entrada síncrona: o estímulo prepara a janela 161…192 na metade anterior do ciclo. A posse termina antes de a confirmação ser retirada, inclusive se o pedido ficar alto por mais de um quadro. O raster e a geração física dessa concessão ainda não estão implementados. A garantia de não atingir pixels visíveis depende do contrato de janela, fase e período do circuito de vídeo futuro.

O commit físico de memória/periférico precede a confirmação ao processador. A CPU atualiza seus próprios registradores depois de receber ACK. Assim, a bancada mantém a verificação estrita de PC/SP/X/A/B/flags durante WAIT; os registradores MMIO podem mudar no IO_COMMIT da transação pendente, verificado separadamente, e o estado completo continua comparado com a referência ao fim da instrução. Essa distinção substitui a simultaneidade ideal da memória antiga, sem mudar ISA, mapa, ordem de pilha ou resultado de instruções válidas.

## Verificações e reprodução

```text
python3 tools/build_memory_access.py
python3 tools/run_memory_access.py
python3 tools/make_memory_access_cpu.py
python3 tools/run_memory_access_cpu.py
python3 tools/run_memory_access_cpu.py --timed --quick
python3 tools/check_memory_access_erc.py
python3 tools/record_net12_manifest.py
python3 tools/record_net12_manifest.py --check
```

Os testes isolados usam o XML do controlador e o decoder NET-11. Há três configurações: ideal com período de 1 µs; atrasos com 1 µs; atrasos com 158,89 ns. Por configuração, 890 transações normais e 128 cortes de reset/POWER_GOOD cobrem oito fases, quatro regiões, leitura/escrita e ambos os tipos de corte. Walking ones/zeros verificam cada pino de endereço/dados nos dois níveis. Um sweep de 200 posições de chegada verifica todas as 32 posições de início de concessão. Um pedido/ACK é mantido por 105.100 ciclos. O retorno de dados do estímulo chega 220 ns após habilitação; não é um modelo do fabricante.

Os monitores verificam payload retido inclusive no reset, efeitos únicos, fases one-hot, ausência de disputa leitura/escrita, CS/OE sem desabilitação intermediária no cenário, liberação de VRAM e ausência de replay após reset. O menor WE normal registrado no cenário rápido é 158,89 ns, acima do limite conservador de 20 ns do estímulo. As 1.018 aceitações incluem os pedidos cortados; não são 1.018 transações concluídas normalmente. Três negativos exigem detectar captura de payload permanentemente habilitada, posse de VRAM sem BUS_ACTIVE e clock do payload desconectado.

A integração usa a CPU global NET-10, o decoder NET-11 e este controlador por pinos. A regressão ideal completa cobre 6.886 casos de instruções, 524.288 guardas e o programa de boot/quadro. O cenário integrado com atrasos é `--quick`, com 1.062 casos de instruções e a bancada de segurança; não inclui programa/quadro nem guardas exaustivas. As configurações finais passaram. O programa ideal completou 132.197 instruções, 232.576 transações, 32.771 transações de VRAM e quadro de 76.800 pixels idêntico à referência. Segurança/reset: 4.586 casos no ideal e 4.546 no cenário com atrasos; os cortes são calculados a partir da latência medida em cada cenário. Consulte os JSONs finais para comandos, fontes, hashes e saídas.

`make_memory_access_cpu.py` substitui as FSMs comportamentais de transação/arbitragem pelo controlador. Arrays de RAM/VRAM/EEPROM, retorno de dados, registradores MMIO, matriz de teclas, raster e concessão continuam modelos. Os selects exatos do NET-11 agora comandam também o MMIO modelado. As opções antigas `latency`/`ack_hold` são removidas das fixtures temporárias, pois a duração passou a resultar dos pinos/estados. Os originais em `sim/rtl` e `sim/tests` permanecem intactos.

O cálculo de colunas foi conservado e passa a ser refeito somente quando teclas/linha mudam, evitando repetir a travessia da matriz em cada acesso de memória. A rodada anterior a essa economia de simulação foi preservada, com as fontes anteriores restauradas pela transformação inversa e conferidas contra seus hashes registrados. Isso não é mudança no circuito ou na semântica do teclado.

O log inicial de falha do monitor MMIO registra a semeadura da fixture no instante 50 ns; o monitor agora distingue essa preparação das mudanças de periférico na transação pendente. Fontes desse ensaio estão em `verification/net12/development`. Esse log e a rodada intermediária não são resultados finais de aceitação.

## Limites de produção

O ERC parcial conserva **129 violações**: 42 entradas externas sem driver, duas alimentações sem fonte e 85 etiquetas isoladas. Nenhuma exceção foi adicionada. `check_memory_access_erc.py` transmite o retorno nativo 5; isso é falha do critério de produção, não aprovação da placa.

O primeiro estágio de CDC não tem modelo de metastabilidade, e seu setup assíncrono não é tratado como entrada síncrona. O segundo estágio e outros registradores usam os monitores selecionados. Faltam MTBF, mínimos/hold/skew completos, interligações/cargas globais e os limites reais da concessão de vídeo. A aprovação do cenário de 158,89 ns não certifica um relógio VGA físico.

A resposta ao reset é testada após um orçamento digital de 1 µs. O supervisor/hold-up precisa bloquear acessos antes de a tensão sair da faixa válida. Um reset durante WE pode truncar uma escrita já iniciada; não há garantia de cancelamento, rollback ou atomicidade contra falta de energia. Os arrays do adaptador não modelam corrupção analógica de uma escrita truncada.

Restam os CIs reais de SRAM/EEPROM, multiplexadores e drivers do barramento bidirecional, fechamento elétrico/temporal desses caminhos, raster/concessão/saída VGA, MMIO/teclado por pinos, alimentação/reset, esquema de sistema, footprints, ERC/DRC, layout e protótipo. O diagnóstico histórico ausente permanece uma falha conhecida da recuperação.
