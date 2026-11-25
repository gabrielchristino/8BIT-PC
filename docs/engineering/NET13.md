# NET-13 — chips de memória e barramento de dados

25/11/2026, base NET-12 `ce19e78eeb865e7787b5f913dd5a6aa6e3914547`. Trabalho novo; os bancos anteriores permanecem intactos. A interface em `hardware/memory_bus` tem 28 CIs, 28 capacitores propostos, 24 resistores de 3,3 kΩ, 576 pinos e sete NC. A variante separada do controlador em `hardware/memory_bus_access` tem 30 CIs, 30 capacitores, 510 pinos e onze NC. As duas folhas KiCad foram exportadas, comparadas pino a pino, renderizadas e inspecionadas. Não constituem um esquema unido de placa nem uma BOM homologada.

## Circuito candidato

Dois AS7C256A na variante SOJ de 28 pinos representam RAM/VRAM de 32 KiB cada; o modelo usa os limites selecionados da versão −20. A EEPROM AT28C256−15 usa a pinagem PDIP de 28 pinos, 32 KiB e acesso de 150 ns. Os símbolos nomeiam o encapsulamento: a pinagem TSOP é diferente e não pode ser substituída por aparência. Ainda faltam footprints e a homologação dos códigos completos de compra. Fontes: [Alliance AS7C256A v1.2](https://www.alliancememory.com/wp-content/uploads/as7c256av.1.2.pdf) e [Microchip DS20006386A](https://ww1.microchip.com/downloads/en/DeviceDoc/Industrial-Grade-256-Kbit-%2832%2C768-x-8%29-Paged-Parallel-EEPROM.pdf).

Há barramentos I/O separados para RAM, VRAM e EEPROM. Quatro AHCT157 selecionam os quinze bits de endereço de VRAM entre vídeo e CPU. Buffers AHC125 escrevem somente na SRAM selecionada. Cada chip fornece dados a um HCT244 compatível com TTL, e seis AHCT157 formam o mux de retorno RAM/VRAM/ROM/MMIO. O buffer de VRAM alimenta também a saída digital de vídeo. EEPROM WE fica permanentemente alto: a programação em circuito continua não implementada, preservando as escritas ignoradas do modelo anterior.

O HCT244 evita aplicar diretamente o VOH TTL mínimo de 2,4 V das memórias a entradas CMOS que podem exigir mais. Também recebe os sinais com pull-up quando os chips ficam em alta impedância; a transição desses sinais precisa respeitar seu limite de entrada. O modelo usa 42 ns para propagação do HCT244, 12 ns para AHCT157 e 10 ns para portas/buffers AHC, nas condições selecionadas. O PDF novo do [SN74HCT244, SCLS175I](https://www.ti.com/lit/ds/symlink/sn74hct244.pdf) foi preservado sem alteração; URLs, revisões e hashes estão em `references/memory-bus-2026-11-25.json`.

## Intervalo de segurança entre drivers

A união revelou uma limitação que o retorno ideal de dados da NET-12 não mostrava. Com o controlador anterior, devolver a VRAM ao vídeo e desligar o driver de escrita no mesmo passo permite sobreposição durante a propagação. O teste negativo compila o controlador NET-12 original contra esta interface e detecta `SRAM output and write buffer overlap VRAM`.

A variante NET-13A acrescenta DRIVE_WINDOW em um canal de HC174 antes não utilizado. O driver liga em ACCESS, depois do período SETUP que desabilita a leitura de vídeo, e desliga ao entrar em RELEASE. A posse de VRAM continua até DONE, oferecendo um período adicional antes de reabilitar a leitura de vídeo. O circuito cresce em dois CIs de lógica/distribuição, sem economia de componentes alegada. BUS_ACTIVE, sem reset no payload, flags separadas e os demais contratos da NET-12 são preservados.

Os modelos contam os drivers ativos, independentemente de seus valores serem iguais ou de o barramento resolver como X. Um cenário adversarial habilita a saída da memória sem atraso mínimo e mantém os atrasos selecionados de desabilitação. A variante passa; o controlador antigo é rejeitado. Isso comprova a proteção no modelo selecionado, sem substituir mínimos/skew, cargas reais ou validação elétrica de saída.

## Memória, reset e firmware

`sim/net13/memory_devices.sv` implementa os modelos funcionais/temporizados dos chips conectados aos pinos do XML. Inclui saída tri-state, janelas de dados indefinidos durante acesso, escrita terminada por WE ou CE e verificações selecionadas de escrita da SRAM. Não são modelos de transistores nem modelos fornecidos pelos fabricantes.

SRAM inicia indefinida e não tem reset. As fixtures de instruções usam padrões explícitos nos arrays dos componentes, com tags/épocas somente para isolamento dos testes. O programa completo usa `FIXTURE_DEFAULTS=0`, carrega a imagem da EEPROM e não recebe zeragem artificial de RAM/VRAM. Ele passou com 132.197 instruções, 232.576 transações, 32.771 acessos de VRAM e quadro de 76.800 pixels idêntico à referência. Não houve escritas abortadas nessa execução.

Um corte durante escrita pode deixar a palavra indefinida. O modelo representa esse caso por X e conta `aborted_writes` separadamente de escritas válidas. As bancadas de segurança registraram cinco abortos RAM/quatro VRAM no ideal e nove/cinco no cenário temporizado, sem afirmar que reset desfaz ou preserva a escrita. Os testes verificam ausência de novas transações válidas/efeitos da CPU após reset; não representam atomicidade analógica. O supervisor/hold-up ainda precisa manter a alimentação válida até os acessos serem bloqueados.

O modelo marca o endereço lembrado no início da escrita; não modela toda a extensão possível de corrupção durante uma transição analógica. O fechamento de reset deve garantir bloqueio de WE antes de alterar bancos/posse e endereço no chip, incluindo mínimos/skew e o mux de VRAM. Reter o payload lógico sozinho não prova essa ordem. A alimentação e o sequenciamento de reset continuam critérios obrigatórios de liberação.

A imagem exata da EEPROM usada no boot aprovado está em `firmware/net13/integration-diagnostic-eeprom.bin`, com 32.768 bytes e SHA-256 `f55d63d70b2da8150b0586e665823639374734ac181f1aefa801a06b8f6b1393`. É o diagnóstico de integração desenvolvido durante a continuidade, não o `diagnostic.asm` histórico ausente, nem firmware final liberado. O arquivo `.hex` adjacente é um byte por linha para `$readmemh`, não Intel HEX.

## Ensaios e reprodução

```text
python3 tools/prepare_memory_bus_access.py
python3 tools/build_memory_bus_access.py
python3 tools/run_memory_bus_control.py
python3 tools/build_memory_bus.py
python3 tools/run_memory_bus.py
python3 tools/run_memory_pullups.py
python3 tools/make_memory_bus_cpu.py
python3 tools/run_memory_bus_cpu.py
python3 tools/run_memory_bus_cpu.py --timed --quick
python3 tools/export_memory_diagnostic.py
python3 tools/check_memory_bus_erc.py
python3 tools/record_net13_manifest.py
python3 tools/record_net13_manifest.py --check
```

- Compatibilidade do controlador: três cenários herdados, 890 transações e 128 cortes por cenário, mais três negativos esperados.
- Endereços/dados: dois cenários da interface, ideal e com atrasos/ativação antecipada. Por cenário, 131.072 escritas válidas, 164.096 leituras pelo mux, 65.536 leituras de vídeo, dezesseis escritas ignoradas em ROM e um corte que deve produzir palavra indefinida. Todos os 32.768 endereços de cada memória são percorridos, com padrões separados para partes baixa/alta do endereço e conferência do offset físico escrito.
- Controlador + decoder + interface: dois cenários temporizados, 714 transações, 124.871 amostras de vídeo por cenário e todas as 32 posições de início da concessão. Inclui pedido mantido por mais de um quadro. O raster/concessão desse ensaio ainda é estímulo, não um circuito físico de vídeo.
- Negativos da interface: controlador antigo sem intervalo entre drivers, WE da SRAM desconectado e WE da EEPROM ligado a zero devem ser rejeitados.
- CPU: integração ideal completa com 6.886 casos das 26 instruções, 524.288 guardas, segurança e boot/quadro; integração com atrasos é reduzida a 1.062 casos e segurança, sem programa/quadro temporizado. Os originais das bancadas permanecem intactos.

A primeira amostragem de vídeo da fixture verificava dados antes da acomodação após reset. O log e a fonte anterior estão preservados; a fixture final espera a acomodação e compara o barramento assíncrono já estável, sem alegar validar a janela setup/hold de um flip-flop de pixel.

## RC, cargas e critérios ainda abertos

O ngspice 42 verificou um modelo de primeira ordem dos pull-ups de 3,3 kΩ, tolerância ±5%, alimentação 4,5/5,5 V e fugas de pior caso selecionadas. Das 24 combinações, dezesseis com 30/50 pF satisfazem o critério conservador de subida 10–90% em 500 ns; oito com 100 pF são calibrações fora do orçamento e são rejeitadas. Os decks, saídas e fórmulas estão em `verification/net13/rc` e `rc-results.json`. A corrente calculada no pull-up da EEPROM em nível baixo é cerca de 1,61 mA, abaixo dos 2,1 mA usados na garantia de VOL de 0,45 V. Isso é análise condicional, não medição de placa ou um modelo do pad do fabricante.

**O orçamento RC de 50 pF não aprova a carga de leitura da SRAM.** Seus tempos de acesso usam carga de teste de 30 pF e os tempos Hi-Z, 5 pF; capacitâncias de memória são caracterizadas em condições indicadas no PDF. A EEPROM usa 100 pF no ensaio de acesso e 5 pF para float. Faltam extração/limites de carga da placa, capacitância de saída do driver desligado, temperatura, I/O do fabricante, ruído/overshoot e verificação correspondente. Os pull-ups ideais dos modelos digitais não simulam a rampa analógica; o ensaio RC é separado. ΔICC de entradas TTL deve entrar no orçamento de alimentação.

O caminho selecionado de vídeo soma até 12 + 20 + 42 = 74 ns antes do registrador de pixel. Isso não define uma fase de captura válida: setup/hold, mínimos e skew ainda precisam ser fechados pelo circuito de relógio/raster. O vídeo RGB332, sincronismos e DAC continuam pendentes.

ERC separado: interface com 171 violações e controlador com 129, referentes a entradas/fontes externas e etiquetas sem consumidores nas folhas parciais. Nenhuma exceção foi inserida; os comandos retornam 5. Não somar esses relatórios como ERC do sistema unido. Faltam união global com cargas contadas, footprints, alimentação/reset, MMIO/teclado por pinos, raster/relógios/DAC, ERC/DRC/layout e protótipo. **Produção permanece bloqueada.**
