# NET32 — folha experimental dos três DACs

27/11/2026, base `793d391819712b85bae46fd2d6e9f9d9092b21c7`.
**Circuito parcial experimental, separado da NET30. Não é uma saída VGA
completa, BOM adotada ou placa liberada.**

## Circuito construído

`hardware/vga_dac_experiment` contém esquema/projeto/biblioteca KiCad,
JSON e CSV de pinos. São três AD9760ARUZ, quinze capacitores de 100 nF
e seis resistores: **24 componentes, 126 pinos, quinze NC**. O XML
exportado foi confrontado com todas as funções/tipos de pinos, referências,
valores e conexões. A numeração vem da transcrição da Rev. B em NET31;
o PDF ADI continua sem bytes locais, com essa ausência preservada.

Por canal: IOUTA vai ao resistor local de 75 ohm, IOUTB ao terra; REFLO e
SLEEP estão em terra. REFIO e COMP2 têm capacitores ao terra, COMP1 tem
capacitor a AVDD; os dois trilhos recebem desacoplamentos próprios.
Os retornos analógico e digital unem-se a GND nesta folha; isso não é
aprovação da distribuição de correntes no futuro layout.

As entradas são trinta bits RGB10 e DAC_CLOCK externo. Expansão RGB332,
buffers, retiming H/V, conector, proteção e alimentação qualificada **não
estão implementados nesta folha**. SLEEP fixo baixo também não garante
preto durante a partida: a integração deve resolver inibição até haver
alimentação, clocks e dados válidos. Nenhuma dessas conexões foi incorporada
ao candidato digital NET30, cuja contagem continua sendo 460 CIs.

RSET é **2,32 kohm ±0,1% para estudo de diagnóstico**. No modelo agregado
de ganho ±10% da etapa anterior, isso mantém IFS calculado até 18,225122 mA;
branco nominal em carga nominal é 0,620084 V. Não atende ao branco final
de 0,7 V e não foi adotado como implementação final do VGA. O resistor
nominal de 2.055 ohm estudado na NET31 pode ultrapassar 20 mA no canto de
ganho positivo; além do erro de amplitude já rejeitado, esse canto sai da
faixa de corrente operacional usada como premissa. Ajuste/calibração e
comportamento em temperatura continuam com critérios próprios.

## Carga conectada e desconectada

Exigir simultaneamente branco de 0,7 V em monitor de 75 ohm, corrente
de até 20 mA e saída sem monitor dentro de 1,25 V não pode ser resolvido
apenas escolhendo outro resistor local:

- A condição sem monitor exige resistor local de até **58,928571 ohm**.
- A corrente operacional, incluindo fator 1023/1024, exige pelo menos
  **65,745383 ohm** para chegar ao branco com o monitor conectado.
- Mesmo no maior resistor permitido pela primeira condição, a corrente
  de branco necessária seria **21,212121 mA**.

Essas inequações não exigem que uma saída sem monitor reproduza cores
corretas. Elas rejeitam a tentativa de manter também essa condição dentro
da faixa linear com apenas um resistor. Faixa linear e limite absoluto
são critérios diferentes; limite absoluto não é condição recomendada.

Com a **hipótese independente** de corrente positiva limitada a 20 mA e
resistor local de 75 ohm ±1%, KCL limita a tensão DC a 1,515 V. Esse valor
fica abaixo de AVDD mínimo proposto +0,3 V = 5,52076 V, mas não demonstra
segurança real: a faixa IFS não é um limitador de proteção, e a hipótese
não cobre alimentação inválida, sequência de ligamento, carga armazenada,
reflexões do cabo, transientes negativos, conexão/desconexão ou ESD.
Fora da compliance, a transferência ideal não prevê a tensão real do CI.

Um clamp de precisão e uma saída com buffer foram considerados como
alternativas, sem adoção. Um clamp exige verificar capacitância, fuga e
resposta transitória; um buffer exige margem de saída no preto, carga,
alimentação, offset e settling. Não atribuir essas verificações a um
nome de componente ou a parâmetros típicos.

## Verificação executada no WSL

```
python3 tools/build_dac_leaf.py
python3 tools/check_dac_leaf.py
```

KiCad 10.0.8, Icarus 12.0 e ngspice 42; comandos, versões, limites próprios,
hashes e saídas constam de `verification/net32`.

- A projeção digital gerada do XML passou 1.024 códigos distintos em cada
  um dos três canais. Usa o latch comportamental NET31 com atraso típico
  selecionado de 1 ns e guards de entrada; não simula o DAC analógico.
- Oito XMLs defeituosos foram rejeitados: bits trocados, IOUTB redirecionado,
  COMP1 no trilho errado, resistor local ausente, SLEEP alto, NC conectado,
  função do símbolo alterada e pino físico inexistente.
- 12.288 avaliações racionais cruzam RGB332, ganho, RSET, resistor local e
  monitor. São cálculos condicionais; o modelo de ganho é o da NET31,
  sem transformar dados caracterizados em 5 V em garantia a 5,392 V.
- Três redes ngspice, derivadas da terminação do XML, varrem 1.024 códigos
  em três canais: monitor de 75 ohm, aberto representado por 1 teraohm e
  curto representado por 1 miliohm. A comparação com KCL passou.
  **São fontes de corrente ideais, não modelo vendor do AD9760.**
  Não há settling, offset, compliance não linear, cabos ou ESD nesse proxy.

O ERC permanece **não aprovado**, com 65 itens sem exceções: 31 entradas
sem driver, dois pinos de alimentação sem fonte, trinta labels de entrada
isolados e dois conflitos de tipo entre IOUTB unidos ao terra. Essa última
ligação é permitida na aplicação single-ended do datasheet, mas o símbolo
de saída de corrente exige tratamento documentado no ERC global; não foi
silenciado nesta etapa. Não usar o código de saída zero da ferramenta para
declarar aprovação elétrica.

O primeiro desenho tinha mais 24 avisos de grade. A versão e seu gerador
foram preservados em `development/initial-native`; a correção move somente
coordenadas e não muda o grafo elétrico. A primeira verificação de seis
negativos também foi preservada antes de acrescentar as duas verificações
de metadados/pino inexistente. Um nome de caso que dizia “floats”, embora
redirecionasse IOUTB ao nó analógico, foi corrigido para descrever a injeção.
Não apresentar essa versão intermediária como o ensaio final de oito casos.

A primeira preparação do commit foi rejeitada pelo verificador de espaços
nos SVGs nativos do KiCad. A saída completa dessa rejeição foi preservada
em `development/stage-generated-svg`. A regra de preservação foi restrita
a esses SVGs e ao log original; seus bytes não foram reformados. A segunda
preparação conferiu os hashes dos arquivos no índice e passou. Isso não
altera o estado não aprovado do ERC.

## Continuidade

Qualificar política de ganho e operação sem monitor/proteção; resolver
alimentação, preto na partida, níveis e margem temporal; construir expansão
RGB332 e retiming H/V nativos; então testar a integração com o raster NET30.
Footprints não foram atribuídos. ERC global, consumo/energia, STA/PVT/CDC,
PCB/DRC e protótipo continuam abertos. Os dois boots completos temporizados
NET27/NET30 seguem separados, com entradas congeladas e sem aprovação por
progresso. Resultados nativos deste bloco não substituem os ensaios deles.
