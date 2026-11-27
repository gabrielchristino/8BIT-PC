# NET33 — raster nativo ligado à projeção digital dos DACs

27/11/2026. Base `052928f344e1fad6f6d43f380345793f60b748ff`.
**Variante experimental separada, sem promoção ao sistema NET30 ou
liberação para fabricação.** A resposta analógica dos DACs não foi simulada.

## Circuitos e economia de componentes

`hardware/dac_packet_video` deriva da folha de vídeo NET30. Quatorze pinos
de canais antes livres mudam, e U38 SN74AHC174 com seu desacoplamento é
acrescentado. As demais conexões do raster permanecem iguais. Vídeo passa
de 37 para 38 CIs nesta variante; CPU, ISA, X, SP, flags, ROMs, memórias,
teclado e os arquivos do candidato NET30 permanecem intactos.

| Canal | Função nova |
|---|---|
| U27 AHC32 canais 2/3 | Buffers OR com entrada fixa zero para os dois bits azuis |
| U35 AHC125 canal 3 | Buffer de P1 para DAC_CLK |
| U32 AHC04 canais 1/2 | Converter H/V negativos em pedidos ativos altos |
| U38 AHC174 bits 0/1 | Capturar esses pedidos na mesma borda DAC_CLK dos DACs |
| U32 AHC04 canais 3/4 | Restaurar H/V negativos após a captura |

Capturar níveis ativos altos permite que o clear do novo registrador
produza H/V inativos altos após os inversores. CLR usa **BUF_1_2**, que
passa de duas para três entradas. Não ligar o novo clear diretamente a
LOCAL_RESET_N: essa rede já alimentava quatro entradas de buffers.
P1 passa de três para quatro cargas; DAC_CLK alimenta os três DACs e U38.

`hardware/vga_dac_rgb332` deriva da folha experimental NET32. Os bits de
R/G são replicados como `abcabcabca`; os de B como `ababababab`. Cada bit
azul alimenta dois pinos diretamente e a entrada do buffer; a saída do
buffer alimenta os outros três. Isso evita cinco entradas diretas em
cada saída azul. Nenhum diodo ou mudança no teclado está envolvido.

Os dois XMLs foram confrontados com referências, valores, funções/tipos,
números de pinos e conexões. A união **somente dessas duas folhas** tem
100 componentes: 38 CIs de vídeo, três DACs, 53 capacitores e seis resistores.
Não é uma união CAD de toda a placa. O máximo contado é quatro entradas
digitais por rede; o orçamento uniforme de 10 pF por entrada mais 10 pF de
trilhas continua hipótese. O AD9760 só oferece Cin típico na tabela usada.

## Modelos e limites temporais

A projeção do raster preserva byte a byte as instâncias/conexões antigas
do modelo NET30, acrescentando as portas e canais extraídos do novo XML.
O novo registrador usa o modelo AHC174 anterior, baseado em SCLS425H:
setup 4,5 ns, hold 0,5 ns, recovery 2,5 ns e pulsos de 5 ns nas condições
documentadas. CQ de 10,5 ns ou 1 ns são escolhas de simulação, não um par
de extremos mínimos/máximos garantidos de toda a placa.

A projeção dos DACs vem da numeração dos pinos no XML, usando o latch
comportamental NET31 com atraso típico selecionado de 1 ns. C/R, ganho,
offset, settling, compliance, ESD e proteção não fazem parte desse modelo.
H/V ainda são sinais internos de 5 V; não estão ligados a um conector VGA.
Driver externo, trilho de 3,3 V, DDC e proteção continuam abertos.

O teste compara os níveis de H/V e as cores 35 ns após a borda DAC_CLK e
também verifica, antes dela, que H/V mantêm o pacote anterior. Isso detecta
a ligação direta dos sincronismos, que mudaria cedo demais. Não prova que
o DAC analógico e o driver de sincronismo mudem no mesmo instante; atrasos
de saída, dispersão, skew, trilhas e jitter precisam de orçamento próprio.

## Ensaios executados no Ubuntu WSL

```
python3 tools/build_dac_video_adapter.py
python3 tools/run_video_dac_checks.py
python3 tools/check_video_dac_native.py
```

Passaram quatro cenários com atraso selecionado: duas políticas binárias
de resolução herdadas do reset e duas opções de captura precoce. Cada
cenário executa dois quadros, separados por um novo reset digital:
210.000 amostras, 153.600 pixels visíveis, 25.200 amostras HS, 800 VS e
todas as 256 cores. O reset é mantido por 50 us e verifica preto/H/V
inativos na condição de alimentação qualificada.

Os estímulos de vídeo são **dados sintéticos**, gerados das coordenadas;
não há SRAM, CPU, programa ou oscilador ACH instanciados nessa bancada.
O master externo é nominal de 25,175 MHz; reset/alimentação são forcepoints
digitais. Duas políticas binárias não constituem prova de metastabilidade,
MTBF ou duração máxima de resolução.

Dois negativos funcionais foram rejeitados pelos motivos esperados:
sincronismo ligado diretamente, antes da borda DAC, e troca dos dois
buffers azuis. Outros oito XMLs com alterações fora do contrato foram
rejeitados pelo verificador de pinagem. Eles incluem clock em outra fase,
clear sem buffer, dados de sincronismo com polaridade errada, bits trocados,
bypass de buffer e alterações de SLEEP/IOUTB. Nem toda alteração de pinagem
é, por si só, prova de defeito funcional; o verificador impede mudanças
silenciosas da variante ensaiada.

ERC permanece sem aprovação e sem exceções: **49 itens no vídeo**
(2 alimentação, 13 entradas, 34 labels isolados) e **15 no DAC**
(11 entradas, 2 alimentação, 2 conflitos entre saídas IOUTB aterradas,
cuja ligação é permitida na aplicação single-ended). São ERCs separados,
não fechamento global após conectar as folhas.

A primeira visualização cortava componentes por herdar papel A1. Após
terminarem todas as simulações NET33, a folha passou a A0. A versão antiga
foi preservada em `verification/net33/development/page-A1`; grafos elétricos
e hashes dos dois modelos compilados são iguais antes/depois. Novos XMLs
e previews foram conferidos, sem alegar reexecução dos quadros depois de
uma alteração funcional. A apresentação atual mostra todos os componentes.

## Próximos critérios

O ganho e o resistor de diagnóstico de 2,32 kohm continuam os da NET32;
não representam branco final calibrado. Qualificar saída sem monitor,
proteção/ESD/conexão, níveis, SLEEP e partida com alimentação real; fechar
interface H/V e temporização/cargas; integrar o novo vídeo ao sistema
CPU/memória; então repetir as regressões pertinentes. ERC global,
footprints, consumo/energia, PCB/DRC e protótipo permanecem abertos.
Os dois boots completos temporizados em andamento continuam usando suas
fontes congeladas NET26/NET30; seus progressos não aprovam esta variante.
