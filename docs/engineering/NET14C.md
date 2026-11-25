# NET-14C — CPU, boot e quadro com raster por pinos

25/11/2026, base NET-14B `6a83d5601ff42b7a970f7d180b405094f612ba09`. Variante nativa separada em `hardware/video_system`, com 35 CIs/35 capacitores propostos, 582 pinos e 29 NC. O adaptador novo em `sim/net14c/isa1_memory_video.sv` substitui o raster, a concessão e a captura comportamentais da NET-13 pelas ligações KiCad. A CPU, ISA, X, pilha, flags, mapa e firmware de diagnóstico são preservados. MMIO/teclado ainda são modelos nesta integração; não há esquema unido de placa nem fabricação liberada.

## Correção do relógio de backend

A integração temporizada encontrou `DFF clock pulse violation` no controlador durante reset. O clear assíncrono do FF de BACKEND podia truncar um pulso depois de uma última borda mestre. A variante separada mantém esse clear permanentemente alto; o FF passa a amostrar as fases já apagadas nas bordas mestre, sem alterar sua saída diretamente por reset. `verification/net14c/native/changed-pin.json` identifica exatamente o pino alterado. Não muda a contagem de CIs nem cria um clock combinacional.

Um ensaio dedicado varre oitenta cortes relativos à borda de descida do backend e verifica pulsos de pelo menos 20 ns, com o modelo de fronteira assíncrona descrito abaixo. A variante passa. Reverter somente o pino de clear reproduz `backend truncated pulse`. A primeira fixture aguardava clock antes de dar seu primeiro reset e foi rejeitada pelo watchdog; a varredura somente após subidas também foi rejeitada como calibração insuficiente porque não detectava a variante antiga. Ambos os registros foram preservados antes da fixture final.

Isso fecha o caso digital selecionado, não o reset/energia global. Startup do oscilador, clocks/cargas reais, metastabilidade, mínimos independentes, brownout e a ordem WE/bancos/posse/endereço da memória continuam critérios obrigatórios.

## Fronteira assíncrona de reset: aprovação condicional explícita

O modelo estrito de AHC74 rejeita a integração quando a liberação externa cai na abertura de recovery do sincronizador. A rejeição atual está em `cpu/results-timed.json`; uma rejeição anterior foi preservada separadamente. Elas não são convertidas em aprovação física.

Foi criado outro modelo de verificação, em `sim/net14c/package_models_async.sv`, derivado do estrito preservado. Somente os dois FFs diretamente ligados ao reset externo são marcados como fronteira assíncrona; os monitores de recovery de todos os FFs posteriores continuam estritos. Cada evento de recovery é contado. No primeiro estágio, a abertura é analisada com duas possibilidades binárias: resolução imediata ou retenção de zero por uma borda adicional. Essa limitação de duração é **uma hipótese de verificação**, não uma garantia do fabricante sobre metastabilidade. Não se modelam amplitudes/durações analógicas arbitrárias nem se comprova MTBF.

A varredura de quarenta deslocamentos de 1 ns para RESET_N e POWER_GOOD passa nas duas possibilidades: oitenta cortes/2.560 pixels por possibilidade. Em cada uma, seis eventos por estágio foram exercitados/contados na abertura. O teste de pulsos de backend também usa esse modelo. A variante do grafo usada na simulação mantém os mesmos pinos e acrescenta somente parâmetros de verificação aos dois FFs identificados. Não se declara a placa segura para qualquer liberação analógica de reset.

## Integração e resultados

As ferramentas novas geram variantes e fixtures temporárias; não editam fontes históricas nem antecessoras. A fixture fornece um pulso de reset real aos modelos, pois o backend dividido não fica clockando durante reset como o modelo antigo. O monitor do programa só começa após carregar a referência e a imagem da EEPROM; isso elimina eventos de preparação da fixture, mantendo a comparação de todas as transações do programa. A captura de PPM observa o clock real de captura e a saída registrada, em vez de presumir o pixel procedural antigo.

| Ensaio | Resultado e escopo |
|---|---|
| Integração ideal completa | 6.886 casos das 26 instruções; 13.406 transações; 4.560 casos de reset/energia; 524.288 guardas, com 327.684 rejeições |
| Boot/quadro ideal | 132.197 instruções, 232.576 transações, 32.771 acessos de VRAM e 76.800 pixels; PPM idêntico à referência |
| Estado inicial do boot | FIXTURE_DEFAULTS=0, SRAM não semeada/zerada; 337 escritas válidas RAM, 32.770 VRAM e zero abortos |
| Instruções com atrasos | 1.062 casos e 1.821 transações, com modelo binário de fronteira; 96 eventos de recovery por estágio contabilizados |
| Segurança com atrasos | Sete lotes cobrindo os índices 0..25, sem omitir pontos de corte; total de 1.700 casos de reset/energia no cenário temporizado |
| Raster isolado da variante | Três cenários de dois quadros, 153.600 pixels visíveis, 2.012 escritas concorrentes e 32 posições de concessão por cenário |

O número de cortes depende do número de ciclos da instrução em cada configuração: o backend real é mais rápido que o backend escalado das etapas anteriores. Não igualar artificialmente 1.700 e 4.560 nem somá-los como cobertura de estados independentes. As instruções temporizadas são uma seleção reduzida; guardas e programa/quadro completos não foram executados com atrasos nesta etapa.

No ideal, mestre de meio período 1,75 ns e CPU de 5 ns são estímulos funcionais escalados, sem alegação de frequência física. O log antigo formata `video_half` como inteiro e mostra 2; a fixture registrada usa parâmetro real de 1,75. No temporizado, o mestre é 25,175 MHz e o meio período da CPU é 5.000 ns. Continuam sendo cenários de componentes, não STA/PVT de PCB.

A segurança temporizada monolítica foi interrompida depois das instruções aprovadas e substituída pelos sete lotes completos para evitar perder trabalho por limite de execução. O processo interrompido retornou zero, mas **não produziu RESULT da segurança e não é aprovado**. `timed-rescheduling.json` e o relatório bruto permanecem; a aceitação dessa cobertura depende exclusivamente dos sete lotes e da conferência dos 26 índices. A presença de código de saída zero sozinha não aprova um ensaio.

## Reprodução e pendências

Gerar com `tools/build_video_system.py`, `tools/make_video_cpu.py`, `tools/make_video_reset_model.py` e `tools/prepare_video_system_checks.py`. Executar `tools/run_video_cpu.py` (ideal completo), `tools/run_video_cpu_async.py --timed --quick` (inclui uma segurança monolítica demorada), `tools/run_video_safety_batches.py`, `tools/run_reset_resolution.py`, `tools/run_video_clock_cuts.py` e `tools/run_video_system.py`. O comando estrito `tools/run_video_cpu.py --timed --quick` deve rejeitar recovery externo; não é uma aprovação pretendida. Todos rodam no WSL Ubuntu, com hashes/comandos/versões/saídas registrados.

ERC parcial da variante: 42 violações, retorno nativo 5, sem exceções. O PDF exportado pertence à folha parcial. Próximos fechamentos: MMIO/teclado por pinos e firmware de varredura, DAC e oscilador, alimentação/reset global, cargas/temporização/CDC/MTBF, esquema unido, BOM/footprints, ERC/DRC/layout e protótipo. As membranas não estão medidas: o usuário informou que ainda não consegue medi-las; seguir com envelopes condicionais, sem homologar unidades por imagem ou FAQ.
