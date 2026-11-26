# NET-22 — Fases de vídeo e ramos de relógio

26/11/2026. Base Git `03e224b48ec1657ea2adfd8330c9d3bf4d262255`.
Variante separada em `hardware/video_common_clock`; antecessores preservados.
**Simulação digital selecionada; placa não liberada para fabricação.**

## Problema reproduzido

A auditoria `verification/net22/clock-tree.json` enumera 72 rotas de pinos de
clock em cinco módulos anteriores. Quatro ligações diretas D–Q atravessam ramos
distintos. Isso é inventário parcial, não STA: a ligação da CPU entre tokens,
por exemplo, usa relógios derivados e exige análise de intenção e temporização.

No anel de fases do vídeo anterior, buffers com atrasos iguais escondiam uma
sensibilidade. `run_phase_skew_probe.py` reproduz perda/duplicação do token com
ramo A=8,5 ns, ramo B=1 ns e CQ antecipado de P3. Ambos os atrasos de buffer
pertencem ao intervalo selecionado de AHC125, 1–8,5 ns, a 5 V ±0,5 V,
CL=50 pF e −40…85 °C. É uma combinação de modelos, não falha medida em placa.
A hipótese intermediária de reagrupar apenas os quatro FFs passou em seis
cenários, mas não é o circuito final desta etapa.

## Decisão E27 e circuito nativo

A variante tem **72 componentes, 36 CIs, 590 pinos e 31 NC**, conferidos por
XML exportado do KiCad 10.0.8. Acrescenta um CI e seu desacoplamento: a economia
de pacotes não justifica conservar uma dependência de skew sem limite fechado.

- U9 passa de dois FFs AHC74 para um **SN74AHC164**. Os quatro primeiros bits
  produzem P0…P3 no mesmo pacote; A recebe `NOR(P0,P1,P2)`, B recebe VDD.
- U10 passa a **SN74LVC1G27**, NOR de três entradas real, com pinagem DBV6.
  Não se supõe a existência de um AHC27 equivalente.
- Depois de clear, os quatro bits estão em zero. A sequência injeta 0001 na
  primeira borda válida e percorre 0001,0010,0100,1000. O antecessor mantinha P3
  em um durante reset; a nova fase inicial difere enquanto as saídas estão
  inibidas. A sequência observável depois da inicialização é preservada.
- Um único ramo MASTER alimenta os dois FFs de sincronização de reset, CLK do
  shift e FF do backend: quatro pinos. O backend continua **sem clear
  assíncrono**, evitando truncamento de pulso.
- Contadores H, RUN e SLOT compartilham um ramo; os três contadores V
  compartilham outro. RUN passa pela antiga porta AND, agora com entrada um,
  preservando um atraso mínimo antes do enable dos contadores H.
- Novo U36 AHC74 registra o terminal H e o terminal combinado H/V na fase P3.
  V usa H_END_REG em ENP e o complemento registrado em LOAD_N. A cadeia ENT/RCO
  permanece original; não se propaga o enable através de três estágios depois
  de P3.
- P3 alimenta U36 e um buffer exclusivo para os dois AHC574 de pixel e o FF
  READY. A interface exporta esse **clock de captura efetivo**, após o buffer.

`clock-topology.json` confere grupos e contratos de pinos, com três mutações
estruturais rejeitadas. Ramos MASTER/H têm quatro entradas, V/captura três;
P3 direto tem três. Com orçamento de 10 pF por entrada e 10 pF de trilhas,
resultam 50/50/40/40/40 pF. Não são cargas extraídas nem garantia de sinal.
A união candidata sobe de 458 para 459 CIs antes de osciladores e demais
circuitos ainda ausentes; não é uma BOM completa ou cálculo de consumo.

`clock-budget.json` verifica sete caminhos de bordas com limites selecionados.
A menor margem é de 0,5 ns no hold de D do backend, que recebe P0 no ramo
MASTER comum. Supõe jitter zero e skew de trilha zero; não são garantias do
oscilador ou da PCB. As contas também cobrem pulsos, loop serial, preparação
de V e hold do enable H, sem fechar todos os caminhos de decode/cascade/reset.
O mínimo de 1 ns da AND AHC08 é conferido em SCLS236L, CL50pF, −40…85 °C.

## Evidência executada

| Bancada | Cobertura e resultado |
|---|---|
| Modelo AHC164 | Três modos positivos e seis violações deliberadas detectadas: setup, hold, pulso CLK, recovery, pulso CLR e envelope de frequência |
| Vídeo nativo completo | Dois quadros por cenário ideal/temporizado/temporizado com P3 antecipado; cada um com 210.000 amostras, 153.600 visíveis, HSYNC 25.200, VSYNC 800, 2.012 escritas e 32 inícios de concessão; sem falhas |
| Matriz de fases | 384 combinações: quatro buffers em extremos 1/8,5 ns, duas políticas binárias de reset, três modos CQ do shift, NOR 1/3,6 ns e duty 47,5/52,5%; cada uma com 2.000 amostras de fases e sequência raster/SLOT conferida |
| Assimetria de pulsos | Outras 256 combinações selecionam subida/descida digitais opostas por buffer (1/8,5 ns) e no shift (1/12,5 ns), com duas políticas, NOR e duty; 2.000 amostras por caso, sem violações dos monitores. Não é forma de onda elétrica |
| Reset com mestre livre | 80 cortes de reset/power-good por política binária, 2.560 pixels por cenário; seis eventos de recovery em cada estágio/política. Negativo recolocando clear do backend detecta pulso truncado |
| Pinos SRAM/VRAM | 48 cortes ativos: políticas 0/1 × RC de 1/19 us × 12 cortes; inibição máxima de WE 94 ns. Pausas de relógio e dois defeitos deliberados detectados |

As regressões integradas adicionais ficam registradas em relatórios próprios
da pasta `verification/net22`; só resultados concluídos com marcador RESULT
e saída sem falhas podem entrar na aceitação desta etapa.

Já concluídos: 6.886 casos ideais da CPU/13.406 transações; dois cenários
temporizados de 1.062 casos/1.821 transações cada (CQ normal/antecipado do
estado do controlador), setup observado do estado de
54,888/36,944/46,944 ns; raw scan temporizado nas duas políticas com cinco
quadros, 40 leituras de colunas, 20 escritas ROW concluídas e uma interrompida
por cenário; quatro cortes de escrita da CPU real e quatro scans reiniciados,
WE bloqueado em até 84 ns nesse escopo. Não somar esse máximo com os 94 ns
observados na outra bancada de cortes.

Boot/quadro ideal integrado concluído: 132.197 instruções, 232.576 transações,
32.771 transações VRAM, 76.800 pixels, 5.388.380 verificações WAIT e 46.465
de pausa; SRAM inicialmente desconhecida (`fixture_defaults=0`) e PPM idêntico
à referência. Execução de 1.008,778 s. Clocks escalados ideais não são a
frequência física; programa/quadro completo com atrasos permanece pendente.

O teste isolado de quadros semeia VRAM. O programa de boot integrado, quando
executado, tem outro escopo: deve iniciar a SRAM desconhecida e produzir a
imagem por instruções reais. Não atribuir a um teste a cobertura do outro.
CPU/ISA de 26 instruções, X, SP, flags, VGA, retenção em WAIT e COMMIT único
continuam sendo contratos da integração, sem mudança de firmware nesta etapa.

## Limites das fontes e dos modelos

[TI AHC164 SCAS970](https://www.ti.com/lit/ds/symlink/sn74ahc164.pdf):
CLK–Q 1–12,5 ns, setup 4,5 ns, hold 0,5 ns, recovery 2,5 ns, pulsos mínimos
de 5 ns e frequência garantida mínima de 95 MHz nas condições selecionadas.
O monitor de frequência marca a saída do envelope garantido; não afirma que
o CI físico deixa de funcionar acima dele. Oito bits são estado interno de um
pacote, não oito FFs externos com relógios independentes.

[TI LVC1G27 SCES488F](https://www.ti.com/lit/ds/symlink/sn74lvc1g27.pdf):
tpd selecionado 1–3,6 ns em 5 V ±0,5 V, CL=50 pF, −40…85 °C. Outras portas e
contadores conservam os atrasos selecionados dos modelos anteriores; a matriz
não varre todos os mínimos/máximos, correlações, transições ou cargas.
Não testa slew elétrico, ringing, jitter, MTBF nem todo PVT.

A pesquisa preserva PDFs originais e extrações separadas. Abracon ACH é
candidato a 25,175 MHz/100 kHz com alimentação 4,5–5,5 V e opções de carga/duty;
**nenhum código completo ou oscilador físico foi homologado ou construído**.
ECS-2100X de 4,75–5,25 V não atende diretamente o trilho proposto de 5,392 V.
LVC125A de até 3,6 V não é substituto direto em 5 V. O AC125 pesquisado tem
divergência entre tabela de carga e recomendação de aplicação; não se adotou
CL=150 pF por conveniência. Duas tentativas de PDFs Analog falharam por timeout
e estão registradas como falhas de coleta, sem arquivos fictícios.

Para preparar a folha de osciladores: o clock da CPU entra em dois pinos
AHC125 de U7; orçamento de 30 pF com trilha. MASTER entra em um pino de U34;
20 pF previstos. Ambos ultrapassam os 15 pF padrão do ACH, portanto a opção
de carga 50 pF precisa constar da configuração candidata. Não aplicar os
tempos da opção de carga maior a uma peça padrão. Correntes máximas listadas
dos dois intervalos de frequência somam 75 mA; isso é apenas a parcela dos
osciladores, não fechamento do consumo da placa. Partida máxima de 10 ms e
reset mínimo de 12 ms não garantem sozinhos cold start: referências de início,
rampa da fonte, POR, VDD válido e jitter ainda exigem análise correspondente.

## ERC, proveniência e pendências

ERC desta folha: **44 violações** (duas de alimentação, 11 de entrada e
31 rótulos isolados), saída nativa 5, sem exceções. PDF/preview foram gerados;
a disposição mantém a folha por pacotes e inclui U36 na região inferior.
Ainda exige integração global e apresentação final legível para montagem.

`adapter-origin.json`, `cpu-adapter-origin.json` e os relatórios preservam
origem/transformação/SHA-256. A primeira versão do builder omitia o import ET;
o snapshot está em `development/missing-et`. Uma captura posterior carregou a
fonte já corrigida por ter sido iniciada antes de uma espera do WSL: o log dessa
tentativa é **sucesso**, não a transcrição do erro original. `record.json`
explica a sequência; o rebuild final foi serial e anterior às simulações.

O runner de quadros herdou a data 25/11. O relatório original é preservado em
`development/frame-metadata-date`; o anotador corrigiu somente metadados para
26/11, com hash e razão explícitos. Isso não representa uma segunda execução.

Continuam abertos: relógios físicos, outros ramos CPU/controlador, temporização
global com atrasos mínimos/máximos e sinais reais, programa/quadro completo
temporizado, consumo/fonte/USB-C/isolamento/POR, DAC VGA, firmware de eventos,
união dos esquemas/ERC, footprints/PCB/DRC e protótipo. Reset binário nas duas
fronteiras marcadas não é validação analógica. A falta histórica de
`diagnostic.asm` permanece; o diagnóstico novo não substitui o original.
