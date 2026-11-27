# NET35 — alternativa para a janela de alimentação H/V

27/11/2026, base `e2d466193a4f2e83e251ebb9c7ea985405907e9d`.
**Alternativa experimental, não promovida à BOM ou ao sistema completo.**
O resultado é uma janela condicional viável; não é validação elétrica do
regulador, supervisor, partida ou placa.

## Problema e mudança

O envelope da NET34 não fecha o contrato de desabilitar antes de 3 V
usando apenas outro limiar, com as mesmas tolerâncias, histerese e condição
de detecção a 5% de overdrive. As inequações exigem simultaneamente um
limiar nominal mínimo maior que o máximo permitido pela retomada. Esse
contraexemplo não afirma que todos os outros supervisores sejam inviáveis;
rejeita a simples troca do limiar dentro daquele contrato.

Foi construída uma nova folha `hardware/vga_sync_window`, preservando
NET34 e todos os predecessores:

- LT3042IMSE#PBF, nominal de **3,51 V**, RSET=35,1 kohm.
- TPS3808G01DBVR com divisor de 14 kohm/2 kohm, nominal de 3,24 V.
- Mesmos NAND Schmitt e buffer duplo. O trilho ainda está dentro da faixa
  de 3,0..3,6 V usada nas condições de teste desses componentes.
- Carga mínima de 2,2 kohm, SET com 0,47 uF, capacitor cerâmico de saída
  de 10 uF e bulk nominal de 100 uF.

São **22 componentes, quatro CIs, 66 pinos**. XML, funções/tipos, valores
e conexões foram confrontados. O pad exposto 11 do LT3042 está em GND e
deve ser soldado. OUTS deve ter ligação Kelvin ao capacitor/retorno.
PG fica aberto; PGFB e EN/UV vão a IN, ILIM ao terra, conforme a aplicação
sem essas funções. Isso não qualifica entrada negativa em PGFB nem
substitui a revisão de layout, proteção e dissipação.

Não há aumento do número de CIs em relação à folha NET34, mas há cinco
passivos adicionais. Não houve comparação de preços nem homologação de
disponibilidade ou footprint. CPU/ISA/X/SP/flags/ROMs/memórias/teclado,
NET30, NET33 e NET34 não foram alterados.

## Limites usados e resultado

O LT3042 tem ±1% inicial, mas a tabela de temperatura completa permite
ISET de **98..102 uA**. Essa segunda faixa e offset de saída ±2 mV foram
usados, sem transformar o valor inicial em garantia de toda a faixa.
RSET e os dois resistores de sense exigem erro total de até ±0,1%, incluindo
temperatura e demais condições; não basta escolher só a tolerância inicial.

Com reserva adicional de ±10 mV para caminho/ripple, o envelope calculado
é **3,4243602..3,5957802 V**. A margem até 3,6 V é somente **4,2198 mV**.
O maior limiar de retomada calculado é 3,4102677 V, deixando **14,0925 mV**.
São margens pequenas, já com os orçamentos explicitados, não folga para
ignorar parasitas, deriva ou transientes.

O menor limiar de queda, incluindo referência, resistores e fuga de sense,
é 3,1692993 V. A análise de descarga começa **depois de atingir 5% abaixo
desse limiar**, e não na primeira passagem pelo valor nominal. A saída
deve permanecer acima de 3 V durante mais 20,1 us. Foram cruzadas 128
combinações com as seguintes premissas:

| Premissa | Limite da análise |
|---|---|
| Corrente total drenada do capacitor | Até 10 mA, inclusive demais caminhos de descarga |
| Capacitância efetiva | Pelo menos 47 uF; o valor nominal de 100 uF não prova isso |
| ESR | Até 50 miliohm |
| Detecção + caminho de inibição | Até 20,1 us, a qualificar na alimentação/carga reais |
| Forma de queda | Descarga monotônica limitada por corrente; sem curto/clamp externo abrupto |

A menor tensão calculada na inibição é **3,0060577 V**. Esse número não
é uma medição. O limite temporal do supervisor e a transição de sua saída
precisam ser qualificados nas condições desta folha, incluindo VDD=3,51 V,
carga e capacitância. A reserva de caminho/ripple na tensão em regime não
autoriza degraus arbitrários durante a queda. Um evento fora do envelope
invalida essa conta.

O LT3042 requer capacitância/ESR/ESL e conexões Kelvin apropriadas para
estabilidade. O cerâmico deve manter pelo menos 4,7 uF efetivos, ESR abaixo
de 50 miliohm e ESL abaixo de 2 nH nas condições aplicáveis. Esses itens,
a estabilidade com o bulk, a corrente máxima real e a partida ainda não
foram qualificados. O ISET especificado usado pressupõe carga acima de
1 mA; o resistor de 2,2 kohm atende a isso em regime nesse envelope.

## Verificações executadas

```
python3 tools/build_sync_window.py
python3 tools/check_sync_window.py
```

- Pinagem/valores e 128 casos condicionais de descarga passaram.
- Dois cenários funcionais de 14 estados passaram; o negativo que ignora
  VIDEO_READY foi rejeitado. O modelo de estados qualificados é idêntico
  ao da NET34 após renomear o módulo; os dois quadros completos não foram
  novamente executados nem recontados como ensaio NET35.
- Oito XMLs fora do contrato foram rejeitados, incluindo pad, OUTS, SET,
  PGFB, divisor, carga mínima e habilitação.
- Quatro proxies ngspice de descarga dentro do envelope ficaram acima
  de 3 V no instante escolhido. Dois negativos, com capacitância insuficiente
  ou corrente excessiva, ficaram abaixo e foram corretamente rejeitados.
  São capacitores, ESR, fonte de corrente e temporização ideal, **não
  modelos vendor do LT3042/TPS3808**.

ERC continua com quatro itens sem exceções: dois de alimentação e dois
labels isolados. Não é ERC global aprovado. Não há ensaio físico ou nova
execução de CPU/SRAM/boot nessa etapa.

Fontes: LT3042 Rev. C lida pela ferramenta web; tentativa de download local
falhou por timeout e foi preservada como falha, sem reconstruir um PDF.
TPS3890/TPS3899 pesquisados têm PDFs/extrações/hashes preservados, mas não
foram adotados. O TPS3808 mantém o PDF primário já arquivado em NET20.
Versões, comandos, limites, saídas e hashes constam de `verification/net35`.

Próximos critérios: confirmar margens e envelopes com modelos/ensaios
adequados, selecionar passivos/footprints e revisar Kelvin/estabilidade;
qualificar receptor, conector/proteção e energia. Ganho RGB/SLEEP, integração
global/CPU, consumo, STA/CDC/PVT, ERC/PCB/DRC e protótipo permanecem abertos.
As duas simulações completas NET27/NET30 continuam com suas fontes congeladas.
