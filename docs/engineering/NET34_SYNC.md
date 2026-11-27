# NET34 — saída candidata de sincronismo em 3,3 V

27/11/2026, base `8aa26ed00ec94f87f3f21fa8cd93f4b1abf1e14b`.
**Folha experimental separada. Não fecha alimentação transitória,
proteção VGA, compatibilidade universal ou fabricação.**

## Circuito construído

`hardware/vga_sync_3v3`: quatro CIs, cinco capacitores e oito resistores,
17 componentes/50 pinos. XML, funções/tipos, números, valores e conexões
foram conferidos. Preview inspecionado; footprints ainda não atribuídos.

| Componente | Função e condição relevante |
|---|---|
| TPS70933DBVR | Regulador 3,3 V com proteção reversa nas condições do datasheet; EN deixado aberto intencionalmente, conforme recomendação; não ligar EN a VIN |
| TPS3808G33DBVR | Supervisão local; MR/SENSE em 3,3 V, CT aberto para atraso de liberação de 12..28 ms |
| SN74LVC1G132DBVR | NAND Schmitt para habilitar somente com VIDEO_READY e reset local liberado |
| SN74LVC2G125DCTR | Dois buffers com entradas tolerantes a 5,5 V e Ioff especificado com VCC=0 |

OE tem pull-up de 10 kohm, reset local tem pull-up de 4,7 kohm. VIDEO_READY
e as duas entradas H/V têm pull-downs de 47 kohm para definir fontes
desconectadas. Os dois resistores de **75 ohm são série**, não terminações
de 75 ohm ao terra como nas saídas de cor. Um resistor de 10 kohm garante
carga superior a 100 uA no trilho qualificado, condição usada no cálculo
da regulação. Resistores são hipóteses de ±1%, ainda sem BOM homologada.

Cin=4,7 uF e Cout=22 uF são valores nominais; os componentes precisam
preservar a capacitância efetiva mínima exigida pelo regulador depois de
tensão, temperatura e tolerância. O alvo transitório de 10 uF efetivos
na saída não foi qualificado. Capacitores de 100 nF desacoplam os outros CIs.

A folha termina em H_OUT/V_OUT. Não inclui conector VGA, DDC ou proteção
IEC/ESD. O candidato NET30 não foi alterado e não recebe automaticamente
a contagem desses quatro CIs. As folhas NET33 também permanecem intactas.

## Seleção e alternativas

O SN74LVC125A consultado aceita 5,5 V nas entradas, mas não oferece a
mesma especificação Ioff procurada para esta etapa. Essa propriedade não
foi inferida pelo nome da família. O SN74LVC2G125 a especifica e oferece
exatamente os dois canais necessários. O NAND Schmitt aceita a subida
lenta da linha de reset com pull-up; um gate comum não foi tratado como
equivalente nessa condição.

TPS731 e TPS7A20 foram considerados. O TPS731 exige EN baixo antes de
remover VIN para garantir seu bloqueio reverso, e sua precisão de 1%
considera carga mínima de 10 mA. O TPS7A20 exige atenção à corrente reversa
e ao limite VOUT versus VIN. Não foram adotados. TPS709 foi escolhido
como candidato, preservando suas próprias limitações: a proteção reversa
não cobre indiscriminadamente toda a região abaixo de 1,8 V, e o valor
de 10 nA citado para fuga é típico, não máximo universal.

Três PDFs novos foram capturados com hashes e extração Poppler em
`references/net34`: NAND, TPS731 pesquisado e TPS709. Buffer e supervisor
reutilizam os PDFs originais de NET23/NET20. O acervo histórico não mudou.

## Contas elétricas condicionais

O envelope preliminar soma ±1% de precisão do TPS70933, 10 mV máximos de
linha e 50 mV máximos de carga: **3,207..3,393 V**. As parcelas têm
condições de ensaio identificadas no datasheet; a soma não substitui
qualificação multivariada ou resposta transitória. O pior limiar de retomada
calculado do supervisor é 3,193951 V: sobra apenas **13,04875 mV** nesse
envelope. Ripple, queda no caminho e transientes ainda precisam caber.

O limite de 20 us de detecção do supervisor corresponde à condição de
overdrive especificada. Cinco por cento abaixo do menor limiar calculado
já fica abaixo de 3 V. Portanto esse número **não prova** que a saída seja
desabilitada antes de perder as condições lógicas de 3 V. A região de
alimentação intermediária continua aberta; não é uma sequência de energia
aprovada por este estudo.

O perfil de receptor aceito nas contas usa limiares TTL 2,0/0,8 V,
resistência de pelo menos 2,2 kohm para terra, corrente adicional de até
100 uA absorvida em nível alto e até 2 mA fornecida ao driver em nível
baixo. Em 32 combinações, com resistores série e cargas identificados,
os limites DC de saída calculados atendem aos limiares e ficam abaixo
de 16 mA. **Não é garantia para qualquer monitor.** Carga de sincronismo
de 75 ohm ao terra é rejeitada. Pull-up arbitrário a 5,5 V enquanto o
buffer está ativamente alto também não está qualificado.

A primeira análise permitia esse último pull-up no receptor. A matemática
do divisor era correta, mas não qualificava a corrente de retorno ao
trilho do driver: Ioff vale para alimentação desligada, não prova capacidade
de absorver corrente em nível alto. A análise inicial e seu script estão
preservados em `development/receiver-profile`, como perfil rejeitado na
revisão. O perfil atual restringe a direção da corrente por estado lógico.

## Testes executados no WSL

```
python3 tools/build_vga_sync.py
python3 tools/run_sync_checks.py
python3 tools/check_sync_electrical.py
```

- Dois cenários de atrasos selecionados passaram 14 verificações de
  estados cada: habilitação, inibição, fonte desconectada/indefinida,
  alimentação exatamente desligada e retomada. Um negativo que ignora
  VIDEO_READY foi rejeitado pelo monitor.
- Dois cenários com raster e DAC digitais NET33 passaram cada um por
  dois quadros/épocas de reset, 210.000 amostras, 153.600 visíveis e 256
  cores, agora através da projeção do estágio H/V externo.
- Oito XMLs fora do contrato foram rejeitados: canais/pinos, trilho errado,
  SENSE, bypass da habilitação, OE no terra, EN ligado a VIN, resistor série
  e pull-down alterados.
- Três proxies RC ngspice com 50/250/1000 pF passaram a comparação de
  níveis nos intervalos definidos. A fonte ideal de 3,3 V e Ron de 37,5 ohm
  são hipóteses; não há transistor vendor, linha distribuída, clamp ou ESD.

O modelo funcional distingue VCC=0, trilho qualificado de 3,0..3,6 V e
transição não qualificada, que produz X deliberadamente. Esperar esse X
não valida o comportamento real na rampa. Regulador e liberação do
supervisor são **forcepoints**, não modelos analógicos. A projeção usa
pinagem confrontada com XML; não é um elaborador genérico de circuitos.
Fuga Ioff e impedâncias não são simuladas por um Z digital ideal.
As janelas de avaliação de 30 ns da bancada não medem nem garantem tempo
de isolamento na queda de VCC. Nos quadros, H/V são observados na saída
lógica dos buffers, antes dos resistores série; o terminal externo é
tratado somente nas contas DC e nos proxies RC.

Os atrasos seguem condições selecionadas: NAND de 2/6,5 ns no teste de
50 pF, e buffer com tempos de dados/habilitação/desabilitação identificados.
Um atraso ativo comum cobre dados e habilitação; não é uma reprodução
exata de cada arco. O destaque de 5,3 ns do NAND corresponde a outra carga
de teste e não foi usado como máximo universal a 50 pF.

ERC: dois pinos de alimentação sem fonte global e dois labels de saída
isolados, **quatro itens sem exceções e sem aprovação global**. Não há
CPU, SRAM, fonte ACH ou resposta RGB analógica nessas novas bancadas.

Próximos critérios: resolver a janela de desligamento/retomada e transientes,
capacitores reais, níveis/carga do receptor, proteção e conector; integrar
CPU/memória e repetir as regressões necessárias. Ganho RGB, SLEEP/POR dos
DACs, fonte global, consumo, STA/CDC/PVT, ERC global, PCB/DRC e protótipo
continuam abertos. As duas simulações completas NET27/NET30 seguem com
entradas congeladas e não aprovam automaticamente esta folha.
