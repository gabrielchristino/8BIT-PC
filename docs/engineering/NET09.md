# NET-09 — X síncrono e ligações explícitas de controle

25/11/2026, base NET-08 `4f2584e7e3d07b0872ecb62eae694eae13a7fd4c`. Trabalho novo separado das fontes anteriores. O banco X tem dois SN74HC273, quatro CD74HC283, oito HC157 e distribuição/portas: 18 CIs, 18 capacitores propostos, 36 componentes, 324 pinos e nove saídas NC. HDL gerado dos pinos exportados do KiCad; folha A1 renderizada e inspecionada. Não é liberação física.

X inicia em 0000h. X_N=1 carrega EA, 2 soma um, 3 subtrai um e 0 retém; os sinais são as saídas ativas em nível baixo do decodificador NET-04. O somador compartilhado usa B=0001h ou FFFFh. Muxes selecionam soma/EA e novo valor/realimentação, com clock positivo comum e enable de execução qualificado. Não há carga assíncrona ou máquina de fases para o X principal. Preservam-se wrap 16 bits, ISA, ROMs, pilha, flags e VGA.

A variante HC191/157/377 permanece com `USE_HC191=1`, somente para comparação com seu sequenciador de referência. A configuração principal é `USE_HC191=0`, usando o novo X por pinos. A escolha não alega menor BOM: a alternativa HC191 contém dez pacotes básicos mais controle que não estava inteiramente mapeado; compará-los como solução completa de dez CIs seria incorreto. O X síncrono foi escolhido para obter armazenamento, aritmética e enable explícitos sem acrescentar uma carga assíncrona não fechada. Otimização total fica para a análise global.

Na revisão das interfaces, EXEC_ACCEPT ainda era uma expressão no adaptador e o modo de escrita era uma comparação simbólica. A variante nativa separada `hardware/cpu_execution_glue` expõe o nó EXEC_ACCEPT já existente no controle e usa uma porta HC04 livre de U48 (entrada pino 5, saída 6) para inverter MEM_N_2. O número de CIs do controle não aumenta. XML, PDF, mapa de pinos e HDL próprios comprovam a ligação. Fontes NET-08 permanecem intactas. A rodada anterior, aprovada antes dessa ligação explícita, está em `baseline-before-pin-glue.json`, com os hashes daquele ensaio. A regressão completa foi repetida para os arquivos finais.

Reproduzir no WSL Ubuntu:

```text
python3 tools/build_x_register_bank.py
python3 tools/build_cpu_execution_glue.py
python3 tools/make_x_register_cpu.py
python3 tools/run_x_register_netlist.py
python3 tools/run_x_register_negative.py
python3 tools/record_net09_manifest.py
python3 tools/record_net09_manifest.py --check
```

Os logs registram versões, comandos, fontes/hashes, saídas e durações. Fixtures temporárias semeiam X em Q dos dois HC273, mantendo também as sementes da alternativa HC191; não se alteram bancadas anteriores. O programa de boot parte do reset normal.

- X isolado ideal/temporizado: todo valor de X × quatro operações × dois enables = 524.288 casos por modo. EA varia por XOR bijetivo, cobrindo todos os valores de carga, sem alegar todos os pares X/EA. Inclui wrap, hold, reset e alimentação digital insegura.
- Nove configurações da integração: duas isoladas, instruções/segurança para X principal e HC191, guardas e dois programas completos. Por variante: 6.886 casos de instruções e 13.406 transações; guardas integradas 524.288 casos. Boot completa 132.197 instruções, 232.576 transações e quadro de 76.800 pixels idêntico à referência em ambas as variantes.
- Dois negativos separados: constante de menor bit do somador ligada em zero deve falhar; clear desconectado deve ser rejeitado pelo conversor.

O cenário temporizado isolado usa intervalos de 1 µs e os mesmos limites selecionados HC273/283/157/125/portas das etapas anteriores, com monitores HC273. Até quatro entradas por net interna, sob orçamento anterior de capacitância. A integração usa modelos funcionais sem atrasos. Não há prova de skew, mínimos, carga extra de outros blocos ou frequência global.

Armazenamento/aritmética/execução da CPU principal agora vêm dos bancos de pacotes; o adaptador ainda qualifica reset comum por expressão lógica e liga interfaces entre blocos. NET-10 reúne os pinos, associa essa qualificação à porta física já existente e verifica cargas globais. Memórias/periféricos e alimentação continuam modelos/interfaces a desenvolver. Não há esquema de placa completo, layout, ERC/DRC aprovado ou protótipo. Datasheets TI existentes preservados por hash; diagnóstico histórico ausente continua falha conhecida.
