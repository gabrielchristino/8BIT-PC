# NET-21A — Supervisor candidato e recepção Schmitt

26/11/2026. Base Git `5c8eba51346be08b5f2ed53da111aef970f71133`.
Variante separada de NET-20A, preservada integralmente.
**Orçamentos e simulações condicionais; placa não liberada.**

## Mudança de circuito

A revisão NET-20 expôs um problema real de orçamento: Ci máximo de uma entrada
AHC125 ocupa todos os 10 pF da condição temporal do TPS3703, sem trilha/pad.
Esta variante considera [TPS3808G01DBVR, TI SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf),
com condição temporal de CL=50 pF e pull-up de 100 kohm. A entrada recebe dois
inversores Schmitt AHC14 antes de produzir RAW_BUFFERED; aceita a subida lenta
do pull-up. Reutiliza duas portas antes livres de U2, desabilita o canal antigo
de U1 e não acrescenta pacotes. Todos os demais clocks, resets e caminhos de
payload continuam os de NET-20.

`hardware/schmitt_reset`: **22 componentes, oito CIs, 132 pinos, nove NC**.
O XML KiCad é comparado a cada pino e valor. U6 é explicitamente DBV/SOT-23:
1 RESET, 2 GND, 3 MR, 4 CT, 5 SENSE, 6 VDD. Não confundir com a pinagem DRV ou
o TPS3703 anterior. MR fica em VDD, CT aberto. R2 muda para 1120 ohm, R3 mantém
100 ohm; tolerância efetiva proposta de 0,1%. R4 passa de 10 kohm a 100 kohm.
Footprints e fabricante/lote da BOM ainda não foram homologados.

O orçamento de RESET é **10 pF de Ci máximo a VCC=5 V mais 10 pF de trilhas**,
20 pF no total, contra CL=50 pF da condição do supervisor. Isso encerra o
conflito aritmético da entrada selecionada; não é capacitância extraída de PCB
nem garantia completa em todas as tensões/transições/POR. A projeção digital
continua forçando RAW_SAFE_N, sem modelar o interior analógico do TPS3808.

## Janela elétrica proposta

O TPS3808G01 tem limiar nominal 0,405 V, precisão de ±2%, histerese máxima de
3%, corrente de SENSE de ±25 nA **na condição SENSE=VIT**, detecção máxima de
20 us com 5% de overdrive na condição indicada e atraso CT aberto de 12–28 ms.
Não estender essa corrente a qualquer tensão nem o prazo de detecção a rampas
arbitrárias. O reset digital das bancadas é um forcepoint independente.

A maior dispersão/histerese exige nova janela de regulação. A proposta troca
o feedback TPS63070 de 55,4 kohm para **57,4 kohm / 10 kohm**, referência de
saída nominal **5,392 V interna**. USB continua 5 V. Ainda é cálculo candidato,
não há conversor físico aprovado nem nova execução bem-sucedida do modelo
oficial que falhou em NET-18.

| Limite condicionado | Resultado |
|---|---:|
| Menor limiar de queda | 4,833270 V |
| Maior limiar de retomada, incluindo histerese | 5,200584 V |
| Menor trilho após carga/caminho/ripple orçados | 5,220763 V |
| Maior trilho com ripple orçado | 5,480951 V |
| Margem de retomada | 20,179 mV |
| Margem até 5,5 V | 19,049 mV |
| Piso calculado na acomodação dos bancos | 4,526232 V |

As margens são pequenas e dependem de hipóteses explícitas: referência ±1%,
corrente de feedback ±100 nA, resistores efetivos ±0,1%, carga de **1,5 A
hipotética**, RON do isolador <=45 mohm, trilhas <=10 mohm e ripple/regulação
<=20 mV. Nenhum desses orçamentos substitui transiente real ou consumo calculado.
O máximo de saída do eFuse anterior não protege sozinho o teto lógico de 5,5 V.
Quatro negativos rejeitam janela antiga, referência alta, limiar alto e CL=60 pF.

## Ensaios concluídos

| Bancada | Evidência no escopo executado |
|---|---|
| Reset com mestre de pedidos de teste | 48 cortes ativos RAM/VRAM, duas políticas binárias e RC de 1/19 us; WE inibido em até **94 ns**, orçamento de 100 ns |
| Negativos de segurança | Reset de banco antes de WE e mudança de endereço após SAFE cair são rejeitados |
| Firmware de varredura na CPU com atrasos | Cinco quadros/40 leituras/20 escritas ROW concluídas em cada política 0/1; relógio da CPU parado e leitura pendente cancelada |
| Falha durante escrita da CPU real | Quatro cortes, deslocamentos 0/40 ns em cada política; reinício completo da varredura e oito bytes corretos por tentativa, WE em até 84 ns nesses casos |
| Reserva de energia condicional | 64 cenários ngspice e três negativos; piso analítico de 4,533050 V em WE e 4,526232 V em bancos |
| Pull-up/recepção RC condicional | 24 cenários e um negativo; alto mínimo 4,3687 V, baixo máximo 0,022411 V no proxy resistivo |
| Cargas selecionadas entre blocos | 16 redes de distribuição, até quatro entradas por saída; orçamento de 10 pF/entrada +10 pF de trilhas |
| ERC parcial | 12 violações: duas de alimentação, duas entradas e oito etiquetas isoladas; retorno nativo 5, sem exceções |

O teste de escrita da CPU não troca o epoch da SRAM durante a falha, não apaga
nem reverte o byte interrompido. O programa reiniciado sobrescreve seus próprios
resultados. ROM e microcódigo são carregados como imagens de verificação;
SRAM começa desconhecida. Os 48 cortes do mestre de teste e os quatro da CPU
têm escopos separados; não se somam a milhares de cortes históricos como se
fossem cobertura de uma única revisão.

A matriz do pull-up usa fonte fixa, resistor, capacitor e chave com Ron=400 ohm,
**proxy de engenharia**, não impedância transitória garantida do supervisor.
A fuga que vem da alimentação usa caminho resistivo passivo, evitando a
injeção artificial acima de VDD por uma fonte de corrente ideal. A descida
condicionada após comandar o sink foi <=27,5 ns; a subida, <=10,74 us, é aceita
pelo Schmitt. Não combinar esses números com o prazo do supervisor para alegar
brownout garantido. O negativo de 1 Mohm precisa de tempo adicional para
acomodar antes da comparação DC; a primeira tentativa curta falhou e foi
preservada em `development/reset-line-first-pass`.

## Reprodução e continuidade

```text
python3 tools/build_schmitt_reset.py
python3 tools/prepare_schmitt_checks.py
python3 tools/run_schmitt_memory.py
python3 tools/run_schmitt_scan.py --timed --policy 0
python3 tools/run_schmitt_scan.py --timed --policy 1
python3 tools/run_schmitt_cpu_fault.py
python3 tools/run_schmitt_power_window.py
python3 tools/run_schmitt_hold_up.py
python3 tools/check_schmitt_interface.py
python3 tools/check_schmitt_loads.py
python3 tools/inventory_schmitt_system.py
python3 tools/check_schmitt_reset_erc.py
```

Icarus/ngspice/KiCad executam no Ubuntu WSL, fontes no diretório canônico Windows.
Não repetir a geração das bancadas enquanto uma execução estiver ativa. A falha
inicial do builder por importação ausente foi registrada; não é falha elétrica.

União candidata: **458 CIs/30 famílias**, incluindo o reset de oito CIs, sem
contabilizar ainda USB-C/regulador/isolamento/osciladores/DAC. Corrente estática e
dinâmica globais continuam abertas. O boot/quadro ideal e os 6.886/1.062 vetores
NET-20 são evidência da revisão anterior, não execuções adicionais NET-21.

Continuam necessários: fechamento de fonte/regulação/isolamento/proteções e
POR, relógios físicos, cargas/skew/min/max/PVT/CDC/MTBF, firmware de eventos do
teclado, DAC, esquema global/footprints/ERC, PCB/DRC e protótipo. Membranas
continuam sem medição das unidades; política conservadora não permite NKRO.
Nenhum ensaio desta etapa libera fabricação.
