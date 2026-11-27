# NET31 — contrato candidato para a saída analógica VGA

27/11/2026. Base digital NET30, commit
`4b74c8c6681d43bc0329e29ce4ab93f5ab4787f6`.
**Estudo de viabilidade e proposta funcional; sem novo esquema nativo,
adoção de BOM ou liberação para fabricação.** CPU, ISA, X, pilha, flags,
memórias, teclado e fontes dos ensaios completos permanecem preservados.

## Escolha para a próxima investigação

Investigar três canais AD9760, um por cor. A página oficial lista
[AD9760ARUZ em produção](https://www.analog.com/en/products/ad9760.html).
Isso não homologa compra, encapsulamento, disponibilidade ou alimentação.
O [datasheet impresso Rev. B](https://www.analog.com/media/en/technical-documentation/data-sheets/AD9760.pdf)
permite alimentação de 2,7 a 5,5 V e clock de qualquer duty que cumpra a
largura mínima de latch. A tabela digital caracteriza níveis em 3 e 5 V;
não se extrapolam automaticamente para toda a janela interna proposta.

Alternativas consultadas:

| Opção | Restrição relevante | Destino nesta etapa |
|---|---|---|
| ADV7123/7125 | Páginas ADI indicam não recomendado para projetos novos; versão 5 V não cobre o teto interno proposto | Não adotar como atalho |
| THS8136 | 3,3 V analógico/1,8 V digital; duty 40–60%; latência de 7,5 clocks | P1 direto de 25% rejeitado; precisaria outra interface |
| AD9748 | Em produção, mas alimentação até 3,6 V e tradução de níveis | Alternativa, sem circuito |
| Rede resistiva histórica | Modelo ideal de 5 V e resistência de saída hipotética; não fecha limites de drivers | Preservar original; não promover a prova elétrica |
| AD9760 | Erro de ganho máximo ±10%, settling apenas típico e restrições da saída | Contrato investigado, com lacunas explícitas |

Fontes primárias adicionais: [ADV7125](https://www.analog.com/en/products/adv7125.html),
[ADV7123](https://www.analog.com/en/products/adv7123.html),
[THS8136](https://www.ti.com/product/THS8136),
[AD9748](https://www.analog.com/en/products/ad9748.html).
Os fatos consultados e os downloads são separados em `references/net31`.
Seis PDFs TI foram preservados com hash e extração Poppler; os downloads
ADI falharam por timeout. A leitura pelo navegador web não fornece os bytes
originais: não existe PDF AD9760 local nesta etapa.

## Contrato verificável

`engineering/net31/dac_contract.json` registra fatos com páginas, pinagem de
28 pinos transcrita da fonte, hipóteses e condições abertas. Não é netlist.
Formato RGB332: R=7:5, G=4:2, B=1:0. Para ocupar dez bits sem perder branco,
replicar `abcabcabca` em R/G e `ababababab` em B. Zero-fill nos bits baixos
não mantém a mesma escala de branco.

Proposta de sincronismo: capturar H/V junto com a cor em P3 e transferir o
pacote no P1 seguinte. A distância nominal é 79,443893 ns, com P1 alto por
39,721946 ns. Esses períodos não constituem orçamento com atrasos mínimos,
máximos, skew, jitter, trilhas, slew ou partidas. AHC174/driver H/V e a
distribuição dos bits ainda precisam de esquema real e análise de cargas.

O modelo `sim/net31/dac_packet_contract.sv` é somente comportamental:
concatenação de bits, captura, guards de setup 2 ns, hold 1,5 ns e pulso
alto 3,5 ns. O atraso de saída selecionado de 1 ns é típico; não é máximo
garantido. Também não representa a dispersão real entre DAC e driver H/V.
O estímulo raster é sintético, seguindo os mesmos limites 200×525,
visível 160×480, HS em 164..187 e VS em 490..491. Nenhuma CPU, SRAM ou
folha NET30 é instanciada nesse ensaio.

## Contas de amplitude e contraexemplos

Com 75 ohm local em paralelo com monitor de 75 ohm, carga equivalente
37,5 ohm, código 1023/1024 e alvo de 0,7 V:

- Corrente de escala cheia nominal: 18,684914 mA.
- RSET nominal calculado: 2.055,133929 ohm, usando referência nominal 1,2 V.
- RSET fixo de 2.055 ohm gera 0,630041..0,770050 V no modelo de ganho ±10%.
  Não atende ao alvo preliminar de ±5%; referência interna não é somada
  outra vez ao erro de ganho que já a inclui.
- Hipótese de ajuste: 1,82 kohm ±0,1% em série com trimpot de 1 kohm ±20%,
  cursor unido à extremidade. Dezesseis cantos cruzam ganho, resistor local
  ±1%, resistor série e monitor ±5%, após calibrar em monitor nominal.
  A faixa do ajuste cobre esses cantos e a mudança do monitor fica abaixo
  de 3% nesse modelo. Isso não garante ganho versus temperatura ou carga.
- Partida no máximo do trimpot limita a corrente calculada a 16,133345 mA;
  ajuste mínimo pode chegar a 23,232023 mA, acima de 20 mA. Não aceitar
  qualquer posição do ajuste como condição válida de operação.
- Retirar o monitor leva a extrapolação ideal a 1,4 V, acima da compliance
  tabelada de 1,25 V. Não é previsão da tensão real fora da região linear,
  nem demonstra dano. Proteção/limitação, conexão/desconexão e alternativas
  com buffer continuam abertas antes de construir a saída final.

A aplicação de ganho multiplicativo ao IFS ajustado é hipótese de projeto;
as especificações de INL/DNL foram obtidas em terra virtual, não nesta carga.
Settling de 35 ns e capacitância de entrada de 5 pF são típicos, sem máximos
disponíveis nas tabelas consultadas. Não fechar timing ou carga com eles.

## Ensaios executados no Ubuntu WSL

```
python3 tools/check_dac_contract.py
python3 tools/run_dac_packet_contract.py
```

Python 3.12.3 e Icarus 12.0, versões/saídas e hashes nos relatórios:

- `verification/net31/contract-results.json`: 256 códigos, 16 cantos
  condicionais e cinco atalhos rejeitados; sem falhas do auditor.
- `verification/net31/packet-results.json`: 256 códigos e um quadro
  sintético de 105.000 amostras, 76.800 visíveis, 12.600 HS e 400 VS.
  Quatro negativos separados rejeitam setup, hold, pulso curto e H/V
  atrasado em um pacote. Compilação e execução têm limites próprios de
  memória, CPU, tempo e saída; os negativos não são casos físicos aprovados.

NET27 e NET30 completos temporizados continuam em processos separados,
com suas fontes congeladas. Os snapshots de integridade desta etapa
registram progresso, não aprovação. Não transferir os testes sintéticos
NET31 para o circuito NET30.

## Próximo critério de aceitação

Resolver saída sem monitor/proteção, qualificar níveis e trilho de alimentação,
definir H/V em 3,3 V e política de conector/DDC; então criar uma variante
nativa separada e confrontar XML/pinagem, cargas e simulação integrada.
IOUTB não pode ficar solto; referência/COMP1/COMP2 exigem as ligações do
datasheet. Não ligar o trilho interno de 5,392 V ao pino de +5 V DDC.
Não há alteração da contagem de 460 CIs do candidato NET30 nesta etapa.
Energia, STA/CDC/PVT, ERC global, footprints, PCB/DRC e protótipo conservam
os critérios de aceitação próprios.
