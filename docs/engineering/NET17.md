# NET-17 — Contatos de até 500 Ω e retomada segura do teclado

26/11/2026. Base Git `30648b94d7529fe577d1984f3a8f8ccf108c1acf`. Desenvolvimento novo em `hardware/keyboard_500`, `sim/net17` e `verification/net17`; NET-15 e os originais permanecem intactos. Esta etapa não integra o programa completo da CPU ao teclado nem libera fabricação.

## Informação recebida e alcance da fonte

O usuário informou contato tipicamente entre 10 e 500 Ω e isolação de 100 MΩ a 100 V. A [Eletrogate](https://www.eletrogate.com/teclado-matricial-de-membrana-16-teclas) publica a isolação citada para seu produto. A [Talos Electronics](https://www.taloselectronics.com/products/teclado-matricial-4x4) publica 10–500 Ω para outro teclado genérico semelhante. A atribuição exata à Eng Automação e a página MakerHero de 16 teclas não foram confirmadas nesta pesquisa; não se substituiu uma ficha de 12 teclas pela de 16.

São informações comerciais de referência, sem identificação do lote das quatro membranas. Adotou-se **500 Ω como alvo condicional de projeto**, não como medição ou limite garantido pelas unidades. A especificação de isolação a 100 V não demonstra automaticamente uma característica ôhmica de 100 MΩ em toda a faixa de operação. O modelo assume separadamente isolação ≥100 MΩ a 0–5,5 V; essa hipótese ainda precisa ser qualificada. Fontes, excertos curtos e atribuições pendentes estão em `source-status.json`.

## Variante nativa e compatibilidade

* Colunas: 16 pull-ups de 270 kohm ±5%; linhas: quatro pull-ups de 120 kohm ±5%.
* Quatro resistores de 820 Ω ±1%, entre os drivers baixo/Hi-Z e as linhas comuns, limitam corrente no caminho dos cabos. As quatro membranas permanecem intactas, sem diodos por tecla, com o mesmo conector L1/L2/L3/L4/C1/C2/C3/C4.
* Contador saturante muda de Q13 para Q14: 16.384 ciclos de backend, aproximadamente 2,603 ms. É espera após ROW/habilitação, não debounce e não detecção de uma tecla que muda depois dessa espera.
* Um AHC74 adicional sincroniza a retomada de ACCESS_SAFE no backend. Sua saída e a condição anterior de reset/escrita de ROW mantêm o temporizador apagado até os drivers poderem funcionar. A porta adicional usa um canal antes livre do AHC08 U33 e um ramo existente de clock com carga disponível.

Total final: **41 CIs, 41 capacitores propostos, 24 resistores e quatro conectores**, 110 componentes/806 pinos/40 NC. Há um CI a mais que na NET-15, justificado pela retomada segura. O aumento da espera não acrescenta contador. Entradas internas por net ≤4 nesta folha; clocks, cargas globais e footprints não estão aprovados.

Preservam-se endereços, dados, BOOT_OFF pegajoso, bancos, COMMIT e as funções da CPU/ISA/X/pilha/flags/VGA. Leituras de colunas podem aguardar mais tempo. A política nova de eventos é deliberadamente mais conservadora para três ou mais teclas e ainda é referência no host, não firmware da CPU.

## O que o modelo elétrico demonstra

A NET-15 impunha LOW também a um caminho agregado de sete contatos. Não se ampliou aquela aprovação de 150 Ω para 500 Ω. Aqui se usa a rede distribuída entre vinte nós comuns de linha/coluna, com pull-up e capacitância para terra em cada nó, resistores de contatos e isolação, fugas e seleção de linha por resistor série. Não é uma extração distribuída dos cabos/PCB nem modelo dos pads.

Hipóteses adicionais: até 10 Ω por perna do caminho direto da tecla, capacitância efetiva ≤1 nF por net comum (a linha compartilhada inclui os quatro módulos), fuga intrínseca de linha ≤3 µA e de coluna ≤1,25 µA. Incluindo contatos abertos, os orçamentos são 4 µA e 1,5 µA, respectivamente. Driver usa limite VOL de 0,44 V nas condições selecionadas do AHC125; limiares conservadores do AHC14 são 1,35/3,85 V. Partes e condições vêm dos PDFs TI já preservados; nenhum CI ou resistor constitui BOM homologada.

O limite de corrente estática agregado é 0,576063 mA. Mesmo atribuindo toda essa corrente ao caminho direto mais desfavorável, a coluna de uma **tecla realmente pressionada na linha selecionada** fica abaixo de 1,216648 V. Uma coluna fora do componente conectado por contatos fechados fica acima de 3,996 V, pelo princípio do mínimo na rede passiva e pelos orçamentos locais de fuga. Colunas alcançadas apenas por caminhos de ghosting podem ficar entre limiares: não se promete reprodução elétrica de todo o fechamento booleano para acordes arbitrários.

Para o modelo de vinte capacitâncias diagonais, cada uma com seu próprio pull-up, o erro máximo de acomodação é limitado por `6 V × exp(-t/283,5 µs)`. Em 2 ms, é ≤5,181 mV, deixando margens conservadoras de **128,173 mV em baixo e 140,820 mV em alto**. A espera nativa é maior, aproximadamente 2,603 ms. A prova supõe contatos estáticos no intervalo; capacitâncias mútuas, nós internos sem pull-up, pad I/V, ruído, carga local dos drivers e contatos mudando durante a amostragem não receberam aprovação física.

O limite de 7,391 mA calculado para a corrente transitória é **do caminho através do resistor série**, supondo diferença de tensão ≤6 V e resistência mínima de 811,8 Ω. Não limita a corrente interna do CI nem a corrente de sua capacitância local de saída, cujo orçamento separado é 50 pF e continua dependendo do layout e da análise correspondente.

768 cenários ngspice passaram: doze padrões, duas transições de linha, contatos de 10/500 Ω, duas alimentações, tolerâncias de pull-up, sinais de fuga e tolerâncias do resistor série. Incluem vazio, pares, L entre módulos, retângulo, caminho longo, 64 contatos e gargalo resistivo. As leituras em 2 ms e no tempo da espera nativa são confrontadas com uma solução nodal independente e seu resíduo. Três cenários fora do orçamento são rejeitados: resistência excessiva, isolação insuficiente e capacitância excessiva. Aprovar esses cenários de modelo não mede nem certifica as membranas.

## Leitura conservadora de até duas teclas

Com zero, uma ou duas teclas estáticas, não há ghosting por contatos fechados e os limites anteriores permitem a leitura exata. Com três ou mais, todas as teclas reais continuam sendo observadas dentro do envelope; portanto o quadro completo contém pelo menos três bits, mesmo se fantasmas distantes não alcançarem LOW. Isso permite bloquear o quadro sem depender da leitura de todos os fantasmas.

`sim/net17/keypad_policy.py` implementa um **contrato de referência no host**: startup exige vazio estável; três quadros completos iguais para admitir até duas teclas; mais de duas cancela imediatamente; CANCEL/ALL_UP libera estado lógico e bloqueia até novo vazio estável. Há eventos ordenados, releases antes de presses, e cancelamento atômico se a fila encher. Não há repetição automática. O objetivo de até duas teclas e bloqueio global consta do planejamento histórico do teclado, mas a decisão de adotá-lo nesta variante é nova, não uma instrução executada do arquivo arquivado.

A referência posterior rev983 usa rejeição por retângulos e é mais permissiva para alguns acordes com três teclas. Ela foi preservada. O novo contrato restringe esses acordes, sem afirmar que o decoder antigo estivesse errado no seu modelo booleano original. Essa restrição faz parte da aceitação condicional de 500 Ω; não se pode usar essa aceitação como garantia de NKRO ou de leitura bruta de todos os fantasmas.

A bancada passou 43.745 conjuntos de zero a três teclas, 87.490 observações extremas, 10.000 quadros maiores com fantasmas parciais e 100.000 passos aleatórios de debounce/fila/consumo. Testa bounce, cancelamento, reset, retenção até vazio e overflow. Um contraexemplo registra a limitação: quadros sequenciais iguais não provam simultaneidade física. O firmware real ainda precisa coletar os quatro ROWs e os dois bytes por ROW, respeitar KEY_READY, implementar o contrato e medir sua latência/jitter. Três quadros com a espera nova podem alongar a resposta para algumas dezenas de milissegundos; não há latência física aprovada.

## Bancadas digitais e retomada

XML KiCad é conferido pino a pino; resistores série são `tran` apenas no modelo lógico, com valores/efeitos elétricos testados separadamente. Dois modos, ideal e com atrasos, passaram 5.681 padrões/22.724 varreduras cada, com 23.504 escritas e 45.969 leituras. O ensaio de MMIO direto não espera o contador a cada padrão e não demonstra tensões de ghosting.

Decoder/controlador/MMIO passaram onze transações em cada modo: quatro leituras longas, sete acessos curtos e reset com pedido retido. Menor espera observada no cenário temporizado: 2.603.301,650 ns. O controlador da NET-15 é reutilizado, sem nova alteração.

A revisão encontrou que ACCESS_SAFE podia ficar baixo após BANK_RESET_N subir, por exemplo durante pausa do domínio da CPU. O temporizador antigo amadureceria antes de ativar as linhas. A bancada nova reproduz isso ao reverter apenas as quatro ligações de clear dos contadores. A variante final reinicia a espera em duas habilitações tardias por configuração, com mais de vinte mil ciclos desabilitada, e verifica leitura correta depois. Há três configurações positivas e um negativo de ligação antiga.

Os dois novos FFs U41 usam apenas na fronteira externa a hipótese binária da NET-14C. Duas políticas temporizadas exercitam dois eventos de recovery por estágio. A variante estrita continua sendo rejeitada por recovery. Isso mantém a lacuna física de metastabilidade/MTBF; os monitores a jusante não foram desativados. Outros negativos rejeitam bypass de KEY_READY, troca de conector, driver alto e resistor série contornado.

ERC parcial: 25 violações (12 entradas sem fonte, duas alimentações sem fonte, onze etiquetas isoladas), retorno nativo 5, sem waivers. PDF e preview foram inspecionados; esquema unido, ERC de sistema e DRC de PCB continuam pendentes.

## Reprodução, intermediários e continuidade

No Ubuntu WSL: `python3 tools/build_keyboard_500.py`, `python3 tools/prepare_keyboard_500_checks.py --write`, `python3 tools/run_keypad_500.py`, `python3 tools/run_keyboard_500.py`, `python3 tools/run_key_settle_500.py`, `python3 tools/run_keyboard_resume.py`, `python3 tools/run_keypad_policy.py` e `python3 tools/check_keyboard_500_erc.py`. Ferramentas, comandos, versões, hashes, saídas e transformações estão em `verification/net17`.

`development` preserva: a primeira tentativa com driver ideal sobre capacitância e corrente contaminada por ringing numérico, sem afirmar sobrecorrente medida em silício; a variante de 8.192 ciclos com menor margem; um caminho de XML incorreto antes de compilar; e a variante anterior à proteção da habilitação tardia. São intermediários identificados, não resultados finais. Os originais NET-15, NET-16, históricos e imagens não foram alterados.

Próximo: supervisor/energia e união dos domínios de reset ao sistema, integração CPU/MMIO/raster e implementação do firmware do teclado. Continuam obrigatórios medir as quatro membranas, qualificar proteção/consumo/temporização/PCB, definir BOM/footprints, resolver ERC/DRC e ensaiar o protótipo. A ausência atual das medições permanece explícita sem impedir esses trabalhos independentes.
