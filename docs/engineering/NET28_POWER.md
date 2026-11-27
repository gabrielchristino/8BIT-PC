# NET-28 — inventário de consumo e limites das evidências

26/11/2026. Circuito-base NET26 `f1c6c27d60d921286ed8729cd6f47e90e5948a3b`;
ferramentas de execução NET27 `ba3353f585fff94469d89674a8c1bdfa08ea70f1`.
**Análise documental, sem alteração de circuito ou aprovação da alimentação.**

## O que foi conferido

As sete folhas candidatas contêm 460 CIs e dois módulos ACH. Foram extraídos
os PDFs primários já arquivados das 34 famílias/configurações, com SHA256,
comando, versão do Poppler, páginas e trechos de revisão. Não foi necessário
substituir datasheets nem executar geradores históricos.

`python3 tools/extract_power_evidence.py` extrai os documentos;
`python3 tools/record_power_allowances.py` confere hashes/cobertura e produz
`verification/net28/power-allowances.json`. As ferramentas não alteram modelos
ou fontes do boot temporizado em execução. Os 32 tipos de CIs e os dois tipos
de osciladores ficam separados de resistores, capacitores e conectores.

## Parcelas de referência

| Grupo | Quantidade | Soma das parcelas selecionadas |
|---|---:|---:|
| Lógica, ICC estático com entradas nos trilhos e saídas sem carga | 452 CIs | 38,510 mA |
| EEPROMs de controle, AT28HC64B | 4 | 160 mA |
| EEPROM de programa, AT28C256 | 1 | 50 mA |
| SRAM, AS7C256A | 2 | 150 mA |
| TPS3808, condição RESET não afirmado | 1 | 0,006 mA |
| ACH 100 kHz / 25,175 MHz | 2 módulos | 75 mA |

**473,516 mA é uma soma de referências em condições distintas de datasheet,
não o máximo da placa funcionando.** HC usa valores tabulares conservadores,
incluindo algumas colunas maiores de temperatura/família; não se extrapolou
uma garantia de ICC em 6 V para todo o trilho proposto. Memórias usam ICC ativo
sem corrente de saída: EEPROM em 5 MHz e SRAM no maior bin de corrente a fMax.
Isso não qualifica glitches, cargas, corrente instantânea ou o conversor.
TPS3808 tem condições específicas de VDD/RESET e o código completo ACH segue
pendente. Cada linha do JSON mantém suas condições e o limite de corrente
da placa como `null`.

Os 24 pull-ups da memória são **3,3 kΩ no esquema/XML e builder NET13**;
o `design.json` sozinho não contém seus valores. Não presumir resistores de
10 kΩ a partir de outro bloco. Com Vmáx condicional de 5,48095 V e Rmín de
3.267 Ω, todos baixos acrescentariam até 40,264 mA. O limite exige essa
tolerância: ele não a homologa na BOM. Nas hipóteses explícitas do JSON,
os pull-ups de teclado somam até 0,513 mA, o divisor de sense 4,498 mA e o
pull-up do supervisor 0,056 mA. Correntes de RC e fugas continuam separadas.

## O que ainda impede fechar a fonte

Entradas HCT/AHCT fora dos trilhos têm consumo adicional. Os datasheets dão,
por exemplo, até 3 mA por entrada HCT377/HCT244 no ponto 0,5/2,4 V, e 1,5 mA
para AHCT157 em 3,4 V, com demais entradas nos trilhos e VCC de 5,5 V.
Esses pontos não provam o mesmo limite para toda a faixa TTL válida ou para
todas as entradas simultâneas; não basta somar ICC por pacote.

A [nota TI SCAA035B](https://www.ti.com/lit/an/scaa035b/scaa035b.pdf) distingue
parcelas estáticas, comutação interna e carga externa. CPD típico ajuda a
estimar consumo, mas não foi transformado em máximo garantido nesta análise.
Precisamos relacionar atividade/glitches por rede, cargas reais, níveis de
entrada, temperatura e margens da fonte. Não usamos o limite absoluto de
corrente por pino como previsão de consumo.

Também faltam consumo do DAC e proteções, perdas do conversor/isolador,
USB-C e corrente anunciada, carga inicial da reserva efetiva de pelo menos
4,4 mF, corrente reversa, regulação/transientes/POR e limite térmico.
**1,5 A continua hipótese dos ensaios condicionais de hold-up, não corrente
calculada ou garantida para o sistema.** Não selecionar a fonte somente pela
soma acima e não ligar a reserva diretamente à entrada USB por inferência.

Aceitação futura: orçamento por estado com hipóteses auditáveis e margens,
fonte/proteções reais, simulação correspondente, BOM/temperatura/cargas
qualificadas e medidas do protótipo. Não houve nova regressão de CPU nesta
análise documental; a execução longa NET27 tem fontes e resultado próprios.
