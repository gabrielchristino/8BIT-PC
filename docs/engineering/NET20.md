# NET-20A — Domínios de reset ligados ao sistema

26/11/2026. Base Git `8af86e361e6eb510ff32c5f4c45cabc7ae633c85`.
Fontes novas, separadas dos originais e das etapas NET-16/18/19A.
**Integração digital condicional; nenhuma liberação de placa.**

## Circuito

`hardware/system_reset` deriva da folha NET-18: 22 componentes, oito CIs,
132 pinos e dez NC. Dois AHC125 adicionais distribuem relógios e resets;
portas antes livres fornecem qualificadores separados para barramento e teclado.
O XML exportado pelo KiCad é conferido pino a pino antes da projeção digital.
Supervisor e passivos permanecem no esquema; a projeção digital força RAW_SAFE_N
externamente, sem simular o interior analógico do supervisor.

O reset da CPU agora é afirmado rapidamente quando RAW cai. Sua liberação
depende primeiro do reset dos bancos e depois de duas bordas de CPU. Os bancos
que alteram memória, posse de VRAM, decoder e MMIO continuam atrás do atraso RC.
O inibidor rápido desabilita WE antes da limpeza desses bancos. O backend nasce
do raster e continua sem clear assíncrono no divisor, preservando NET-14C.
RUN não recebe uma porta assíncrona nova.

Isso refina a ordem conservadora anterior: a CPU pode limpar seu endereço vivo
antes do fim de WE, pois SRAM recebe endereço/dado **retidos nos HC377 do
controlador**, que não têm clear. Os bancos que realmente alteram seleção e
endereços físicos precisam esperar. Não se permite essa antecipação se uma
integração futura voltar a ligar endereço vivo diretamente à SRAM.

`sim/net20/isa1_memory_reset.sv` liga as saídas reais aos blocos:
CPU usa CPU_CORE_CLK/CPU_RESET_N; controlador e frontend usam BANK_MEMORY_N;
decoder usa BANK_DECODE_N; MMIO usa BANK_KEYBOARD_N. SAFE_MEMORY e SAFE_KEYBOARD
são distribuídos separadamente. Os estímulos de relógio ainda são externos.

## Verificação

`run_reset_memory.py` exercita RAM e VRAM com falhas em seis deslocamentos
após a queda de WE: 0, 1, 7, 20, 40 e 100 ns. Cruza duas hipóteses binárias de
liberação e dois extremos de afirmação RC, 1/19 us: **48 cortes de escrita**.
Cada cenário também para o relógio da CPU e o mestre, verificando retomada sem
liberação prematura ou replay do handshake antigo.

Monitores independentes observam os pinos de endereço e WE das SRAMs mesmo
quando SAFE lógico já caiu. Essa diferença é necessária: o capacitor de reserva
deve manter a alimentação válida nesse intervalo, enquanto os modelos antigos
condicionam seus próprios checks a SAFE. Em todos os cortes selecionados,
**WE ficou alto em até 80 ns**, dentro do orçamento de 100 ns. Reset dos bancos
ocorreu depois do bloqueio; endereço/dado retidos sobreviveram à retirada do
pedido vivo. Não se exige dado de I/O estável desde o início de WE: permanece o
contrato de escrita do chip; um byte interrompido pode ficar desconhecido.

Dois negativos devem falhar: ligar reset do banco diretamente a RAW viola a
ordem WE/banco; alterar endereço físico 60 ns após RAW, já com SAFE interno baixo
e WE ainda ativo, é rejeitado pelo monitor independente. Essa segunda rejeição
não depende de habilitar artificialmente o monitor antigo da SRAM.

O raw scan executa firmware na CPU, sem semear CPU/MMIO/SRAM, com cinco quadros,
40 leituras de coluna e 20 escritas ROW concluídas. Há uma tentativa adicional
abortada por reset. A pausa da CPU não impede o vídeo/ACK; leitura pendente é
cancelada e reinicia. Foram executados modo ideal e duas políticas binárias
temporizadas. Essas políticas não são prova de duração de metastabilidade.

Os vetores arquiteturais usam seeds somente após os domínios ficarem prontos;
reset temporizado foi alongado para seis ciclos da fonte da CPU. Não se
transfere automaticamente para esta variante a contagem antiga de milhares de
cortes: a bancada de 48 cortes acima tem outro escopo. Consulte os relatórios
em `verification/net20` para as contagens efetivamente concluídas.

Regressão arquitetural concluída: **6.886 casos / 13.406 transações** no modo
ideal e **1.062 casos / 1.821 transações** no cenário temporizado reduzido.
O setup observado nos três registros de estado do controlador foi
54,888 / 38,944 / 48,944 ns. Esses valores incluem a distribuição selecionada,
sem transformar o deslocamento favorável de fase em garantia global de skew.

O boot/programa/quadro ideal completo também passou: **132.197 instruções,
232.576 transações e 76.800 pixels**, imagem PPM idêntica à referência, com
SRAM inicialmente desconhecida. Não foi executado programa completo temporizado.

O hold-up foi repetido com orçamento de **20 us** até bancos/decoder acomodarem,
incluindo a distribuição adicional: 64 cenários e três negativos. O limite
analítico condicionado é 4,561977 V no bloqueio de WE e 4,555159 V após bancos,
com piso de 4,5 V. Permanecem C efetivo >=4,4 mF, ESR <=20 mohm, carga hipotética
<=1,5 A, reverso <=0,5 A/50 uC e demais condições NET-18. **Não é consumo
calculado da placa nem resposta garantida a curto/rampas arbitrárias.**

A contagem de cargas junta os pinos selecionados dos seis blocos: 14 redes de
distribuição, no máximo quatro entradas por saída. Usa orçamento explícito de
10 pF por entrada mais 10 pF de trilhas, até CL=50 pF; não é extração de PCB,
revisão elétrica de todas as famílias ou fechamento independente de skew/PVT.
O clock sem distribuição teria oito cargas nesse grupo, orçamento de 90 pF.

ERC da folha parcial: **12 violações**, duas de alimentação, duas de entrada e
oito de etiqueta isolada; retorno nativo 5, sem exceções. PDF/preview preservados.

## Limite encontrado no supervisor

O [AHC125 TI](https://www.ti.com/lit/ds/symlink/sn74ahc125.pdf) tem Ci máximo de
10 pF. O limite temporal adotado para
[TPS3703](https://www.ti.com/lit/ds/symlink/tps3703.pdf) foi especificado com
CL=10 pF. Uma única entrada já consome todo o valor; sobram **zero pF** para
trilha/pad. Portanto a condição de carga NET-18 continua **não satisfeita como
garantia física**. Os ensaios após RAW e a matemática condicional de hold-up
não fecham essa interface. Não se reescrevem os relatórios históricos para
transformar esse achado em aprovação anterior.

Datasheets de alternativas foram preservados, com extrações e hashes. AHC1G125
também tem máximo de 10 pF; o valor típico de LVC1G125 não comprova limite máximo
menor. TPS3808, TPS3700, TPS3890 e TPS3840 são pesquisa, **não peças adotadas**.
A próxima revisão pode considerar maior carga especificada e entrada Schmitt,
recalculando limiares, janela de regulação, atrasos e reserva; não basta trocar
um nome de componente no modelo.

## Reprodução e limites

No Ubuntu WSL, a partir do diretório canônico do projeto:

```text
python3 tools/build_system_reset.py
python3 tools/make_reset_system.py
python3 tools/prepare_reset_checks.py
python3 tools/run_reset_memory.py
python3 tools/run_reset_scan.py --timed --policy 0
python3 tools/run_reset_scan.py --timed --policy 1
python3 tools/run_reset_scan.py --policy 1
python3 tools/run_reset_vectors.py
python3 tools/run_reset_vectors.py --timed --quick
python3 tools/run_reset_program.py
python3 tools/run_system_hold_up.py
python3 tools/check_reset_loads.py
python3 tools/check_system_reset_erc.py
```

Ideal escala RC para 1/4 ns; não representa frequência física. Temporizado usa
afirmação 1/19 us e liberação 42 us, fontes 25,175 MHz e 100 kHz. Modelos RC
continuam inerciais, sem carga acumulada de trens de pulsos. RAW deve cumprir
o contrato qualificado anterior; não se concluiu POR abaixo de VDD válido,
supervisor analógico, fonte USB-C/regulador/isolamento, corrente real, clock
físico, skew/PVT/MTBF global, DAC, esquema único, footprints, PCB/DRC ou protótipo.
Debounce/fila/cancelamento seguem política host, ainda não firmware de eventos.

`development/first-pass` preserva o primeiro ensaio bem-sucedido com aviso de
declaração implícita de backend, suas fontes alteradas e a primeira calibração
do negativo de endereço. A aceitação final usa declaração explícita, cruza os
dois extremos RC e desloca a falha de endereço para depois de SAFE cair.
