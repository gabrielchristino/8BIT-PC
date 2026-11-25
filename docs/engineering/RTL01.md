# RTL-01 — CPU comandada pelas ROMs recuperadas

Iteração nova de 24/11/2026. Base: ROMs binárias e contrato arquitetural de `revisions/rev983`, banco candidato de X desenvolvido em 9.8.4.2. Os snapshots históricos não foram alterados. Esta etapa é emulação digital RTL com integração de modelos de componentes para X; **não é uma netlist física completa nem liberação para fabricar**.

Continuação e conferência em 25/11/2026. O campo fixo `date` dos scripts desta iteração identifica sua data de início; não é uma leitura do relógio de execução. Versões, comandos, hashes e saídas identificam as rodadas efetivas.

## Execução reproduzível

```text
wsl -d Ubuntu -- python3 /mnt/c/Users/gabri/projetos/isa1/tools/run_rtl.py
wsl -d Ubuntu -- python3 /mnt/c/Users/gabri/projetos/isa1/tools/run_stack_guards.py
wsl -d Ubuntu -- python3 /mnt/c/Users/gabri/projetos/isa1/tools/render_rtl_frame.py
```

O comando usa Icarus Verilog no Ubuntu WSL. Compilações, vetores e imagens temporárias ficam em `/tmp`, removidos ao terminar. `verification/rtl01/results.json` guarda versões, comandos, saídas e hashes; o manifesto desta etapa verifica os artefatos persistentes. `--quick` reduz os casos por opcode válido e marca o relatório como parcial; não substitui a rodada completa.

## O que está conectado

Resultados da rodada completa de referência: 6.886 casos de instruções por configuração de X; 1.048.576 combinações de ALU; 2.922 cortes de reset/energia com X ideal e 2.930 com X candidato; 524.288 verificações de limites da pilha, com 327.684 rejeições corretas. O programa completa 132.197 instruções e 232.576 transações por configuração, incluindo 32.771 acessos à VRAM; as 76.800 amostras do quadro conferem com a referência. Não somar as duas configurações como cobertura independente.

- `isa1_cpu.sv` lê as quatro lanes binárias originais, reconstruídas em palavras de 32 bits, e executa os campos de controle de 26 bits. Não usa uma tabela de instruções HDL paralela para determinar as operações. Os 8.192 endereços são conferidos contra o gerador recuperado antes do ensaio.
- PC, SP, A, B, EA, IR, MDR, flags e ALU são RTL funcional novo. O sequenciamento FETCH/execução vem do endereço da ROM. Isso ainda não define os CIs físicos desses blocos.
- X é selecionável entre registrador RTL ideal e o banco candidato com quatro HC191, quatro HC157 e dois HC377. A versão com componentes usa modelos funcionais sem atrasos nesta integração. O sequenciador interno de carga continua sendo RTL de referência, com portas não mapeadas a CIs.
- O adaptador de carga retém EA, bloqueia o avanço da CPU e conserva a conclusão mesmo se RUN estiver pausado. Não há transação de memória simultânea à carga de X. INX/DEX usam um único evento de contagem, com clock comum aos quatro nibbles.
- A interface de memória tem requisição, resposta e retorno ao repouso. Endereço/dado permanecem retidos durante WAIT. ACK mantido alto não é interpretado como novas confirmações.
- RAM, EEPROM somente leitura, bancos VRAM, overlay de boot e MMIO são modelos de simulação. A EEPROM programável e seu protocolo elétrico **não** foram incorporados a esta RTL.
- A VRAM cruza dois clocks por handshake de quatro fases e dois registradores de sincronização em cada direção. O payload fica retido. São flip-flops ideais: não há modelo de metastabilidade, MTBF ou restrições de roteamento.
- O raster conserva 200 × 525 ciclos, 160 × 480 amostras ativas e quatro repetições verticais por linha lógica. Não há ainda DAC, sincronismos VGA físicos ou PLL/clock real.
- A matriz passiva 4 × 16 propaga os componentes conectados, incluindo ghosting. O diagnóstico usa um trio em L para verificar a leitura ambígua esperada; isso não oferece reconhecimento irrestrito de múltiplas teclas. Debounce/ABI de ENG-KBD-01 continuam fora desta RTL.

## Bancadas e critérios

A referência é um adaptador novo sobre o CPU recuperado. Acrescenta a checagem antecipada dos dois bytes de CALL/RET (ADR E04); os demais efeitos arquiteturais são os originais. As instruções válidas preservam sua semântica. Falhas por limite são intencionalmente antecipadas para evitar SP e memória parcialmente alterados. Não há rollback se reset/energia interromper uma operação válida já iniciada.

`tb_stack_guards` verifica os 65.536 valores de SP, boot ativo/inativo e CALL/RET/PUSH/POP: 524.288 casos no primeiro microcomando de pilha, usando as palavras reais das ROMs. O critério independente é o intervalo necessário para um ou dois bytes; rejeição deve parar a CPU, não emitir requisição e conservar SP.

`tb_rtl_cpu` compara o estado ao terminar cada instrução e todas as suas transações com o modelo arquitetural Python recuperado. Os casos dirigidos incluem os limites da pilha, boot ativo/inativo, quatro bancos VRAM, dois bancos EEPROM, Z/C, wrap de X, escrita em ROM/overlay, MMIO e esperas de zero a dez ciclos. Cada um dos 26 opcodes válidos tem 256 casos; os 230 inválidos são testados individualmente. Memórias têm padrões diferentes por endereço/banco para evitar que leituras incorretas passem por coincidência de zeros. As duas configurações de X usam os mesmos vetores e não são amostras independentes.

`tb_rtl_safety` corta reset ou alimentação em cada posição de ciclo observada de instruções representativas dos 26 opcodes, incluindo transações de VRAM. Depois da invalidação, exige registros reinicializados, ausência de ACK/requisição e nenhuma nova escrita. Escritas já concluídas antes do corte permanecem; não existe promessa de rollback da RAM. As posições são digitais e discretas, não todos os instantes analógicos possíveis.

`tb_rtl_alu` compara as oito operações, todos os pares A/B e ambos os estados anteriores de C: 1.048.576 combinações. O ensaio é combinacional ideal; não modela atrasos internos dos somadores ou seleção.

`tb_rtl_program` inicia do vetor de reset na EEPROM. Um carregador novo copia o diagnóstico para RAM, desativa o overlay e salta para 4000h. O diagnóstico exercita os 26 opcodes, testa pilha, lê o teclado com ghosting, troca os bancos de EEPROM a partir de RAM e escreve os quatro bancos de VRAM. Todas as instruções concluídas e transações são comparadas à referência, incluindo pausas de RUN. Cada byte dos 32 KiB de VRAM e cada amostra de um quadro VGA posterior são conferidos. Clocks digitais diferentes são usados nas duas configurações; seus períodos são unidades de simulação, **não uma frequência garantida dos CIs**.

O firmware é `firmware/rtl01_diagnostic.asm`, criado nesta etapa. Ele não preenche a lacuna do `diagnostic.asm` histórico. Sucesso é RAM[5FF0h]=A5h; falha é DEh. A imagem produzida pelo HDL é comparada byte a byte à referência antes de ser preservada em `frame.ppm`; `frame.png` é a renderização dessas amostras.

`frame-display.png` amplia cada amostra horizontal quatro vezes para uma prévia 640 × 480. É uma escala de apresentação do framebuffer emulado, não uma captura de monitor físico. A rodada inicial, antes do candidato de X e da checagem antecipada da pilha, está preservada em `baseline-rtl-results.json`, como evidência intermediária, sem substituir os resultados finais.

O teste exaustivo de pilha revelou inicialmente registros desconhecidos no primeiro caso: a bancada mantinha clock estático durante o primeiro reset. Um flanco sob reset foi acrescentado antes das fixtures; a rodada completa foi então aprovada. Nenhum defeito de CI físico foi inferido. As declarações de nets da CPU também foram ordenadas para eliminar avisos de nets implícitas antes da rodada final.

## Pendências que impedem produção

| Item | Situação após esta etapa |
|---|---|
| Execução das ROMs na CPU RTL | Integrada; resultados exatos no relatório de execução |
| X candidato integrado à CPU | Modelo funcional selecionável; controle físico e temporização integrada pendentes |
| SP e endereço SP−1 | Funcionais na RTL, com atualização após a transação; circuito de CIs ainda pendente |
| Datapath e sequenciador em CIs | Não mapeados integralmente |
| Derivação da emulação a partir do esquema | Pendente; RTL e KiCad parcial são representações separadas |
| Gravação EEPROM, boot de usuário e monitor | Só boot diagnóstico e leitura EEPROM nesta RTL |
| Teclado físico | Pinagem medida, resistência/capacitância, debounce e proteção elétrica pendentes |
| VGA físico | Clocks, sinais de sincronismo, DAC e carga de 75 ohms pendentes |
| Elétrica/temporização | Setup/hold, atrasos mínimos/máximos, cargas, alimentação e brownout físicos pendentes |
| Esquema, ERC, PCB, DRC e protótipo | Esquema parcial anterior; demais etapas pendentes |

Uma rodada sem divergências demonstra os casos e contratos descritos. Não demonstra perfeição de todo o espaço de estados, equivalência formal ou funcionamento físico. O próximo passo é mapear controle/datapath a componentes e usar uma netlist comum ao esquema e à simulação, preservando estas regressões.
