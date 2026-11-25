# NET-11 — decodificação física de memória

25/11/2026. Continuação da CPU global NET-10, commit `52bb48901fda92848add95f01097b704472d397e`. Novo banco em `hardware/memory_decode`, separado dos originais; 32 CIs HC08/32/04/125, 32 capacitores propostos, 512 pinos, três NC e até quatro entradas internas por sinal. A biblioteca local e o esquema/PDF acompanham XML exportado e mapa de pinos. Não há memória de dados, controlador de acesso ou placa completa nesta folha.

O mapa preserva 96 KiB físicos: 32 KiB RAM, 32 KiB VRAM e 32 KiB EEPROM. Enquanto BOOT=1, 0000h–3FFFh seleciona a primeira metade da EEPROM; caso contrário 0000h–7FFFh é RAM. A janela 8000h–9FFFh seleciona VRAM pelo banco VB de dois bits; A000h–BFFFh é MMIO; C000h–FFFFh seleciona EEPROM por EB. Os barramentos físicos têm 15 bits. O estado dos bancos e o mecanismo de BOOT ainda pertencem ao modelo de periféricos.

Os seis selects MMIO são comparações exatas: A000h VB, A001h EB, A002h BOOT, A010h linha do teclado, A011h colunas baixas e A012h colunas altas. Não se introduzem aliases de endereços. O modelo histórico retorna FFh nos demais endereços de leitura de MMIO e ignora escritas não implementadas. As escritas na janela de EEPROM permanecem ignoradas pelo modelo; não se implementou programação da EEPROM.

Os selects de região e MMIO são qualificados por SAFE e ACCESS. **Não são pulsos WE/OE**, nem têm garantia de ausência de hazards enquanto endereço/bancos mudam. O controlador seguinte precisa reter a transação, permitir acomodação da decodificação e produzir um único acesso seguro. O modelo temporizado usa 31 ns para portas, 24 ns para inversores e 36 ns para buffers, com estímulos espaçados por 1 µs. Não é fechamento dos mínimos/máximos de um ciclo físico.

Reprodução no Ubuntu WSL:

```text
python3 tools/build_memory_decode.py
python3 tools/run_memory_decode.py
python3 tools/analyze_memory_decode.py
python3 tools/make_memory_decode_cpu.py
python3 tools/run_memory_decode_cpu.py
python3 tools/run_memory_decode_cpu.py --timed --quick
python3 tools/check_memory_decode_erc.py
python3 tools/record_net11_manifest.py
python3 tools/record_net11_manifest.py --check
```

O teste isolado percorre 65.536 endereços × dois estados de BOOT × dois de EB × quatro de VB × quatro de SAFE/ACCESS: 4.194.304 combinações, mais um caso dirigido, em cada modo ideal e com atrasos. Compara selects de região/MMIO e todos os barramentos físicos, inclusive nas regiões não selecionadas. Dois negativos exigem detectar EB preso em zero e SAFE desconectado.

A análise do grafo exportado encontra caminho máximo de 251 ns até IO_VB, usando somente os atrasos máximos selecionados e chegada simultânea das entradas no instante zero. O intervalo de teste de 1 µs excede esse valor em 749 ns. Essa margem pertence ao modelo: não inclui chegada tardia das fontes, carga física, setup do consumidor, skew, mínimos, hazards ou cantos adicionais. Não deve ser usada como frequência certificada do sistema.

`make_memory_decode_cpu.py` deriva uma cópia separada de `sim/rtl/isa1_memory.sv`, substituindo somente a seleção/captura de região e endereço pelos resultados da netlist. Armazenamento, registradores MMIO, leitura de colunas, sincronização e arbitragem de vídeo **continuam comportamentais**. A interface MMIO nessa cópia ainda usa o case histórico; os selects físicos MMIO são verificados isoladamente. O adaptador é identificado por origem e hashes. A regressão ideal completa compara instruções, guardas, boot e quadro com a referência; o ensaio integrado com atrasos é somente a configuração `--quick`, sem programa/quadro nem guardas exaustivas. Consulte `verification/net11/cpu` para os resultados, sem somar cobertura parcial como aprovação completa.

ERC parcial com KiCad 10.0.8 conserva **85 violações**: 22 entradas externas sem driver, duas alimentações sem fonte e 61 etiquetas isoladas, incluindo saídas sem consumidores nesta folha. Comando e retorno 5 em `erc-summary.json`; nenhuma exceção foi adicionada. O script ERC transmite esse retorno de falha. No esquema de sistema, as fontes/consumidores precisam existir e as cargas entre CPU/decoder/memórias precisam ser recontadas. ERC da CPU e ERC do decoder são relatórios separados; não somá-los como uma análise de placa completa.

Onze PDFs oficiais foram preservados em `references/system-candidates-2026-11-25.json`, com URLs, datas e hashes. AS7C256A, AT28C256 e famílias rápidas de lógica são candidatos para etapas futuras; não são uma BOM homologada. Leituras de SRAM/EEPROM exigem recepção compatível com TTL; endereços podem vir de CMOS conforme limites de carga. Nenhuma seleção de encapsulamento, corrente, alimentação ou velocidade está aprovada por esta etapa.

Restam controlador físico de acesso/commit, captura e buffers do barramento bidirecional, prevenção de conflito OE/WE, acesso à VRAM em blanking, registradores MMIO, teclado elétrico, raster/saída VGA, alimentação/reset e a integração de placa. Resultados finais: dois modos isolados e dois negativos passaram; integração ideal completa e integração temporizada reduzida passaram. O programa integrado executou 132.197 instruções e 232.576 transações, com quadro de 76.800 pixels idêntico à referência. O arquivo histórico `diagnostic.asm` continua ausente, sem substituto apresentado como original recuperado.
