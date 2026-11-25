# Membranas 4×4 — referência de conector

Fonte: duas imagens e FAQ fornecidas pelo usuário em 25/11/2026. Imagens originais preservadas em `references/user/2026-11-25`, com nomes de anexos, SHA-256 e crédito visível no manifesto. O diagrama credita Gustavo Murta, 2019. Não foi fornecida licença ou identificação verificável do fabricante; nenhum desses dados equivale a medição das quatro unidades.

Na orientação da foto — face das teclas voltada ao observador, cabo saindo por baixo — os contatos da esquerda para a direita são **L1, L2, L3, L4, C1, C2, C3, C4**. Esta é a numeração de referência proposta para J_K1 a J_K4, pinos 1 a 8. Uma vista pelo lado oposto pode ficar espelhada; conferir marca de pino 1 e continuidade antes da montagem.

| Pino de referência | Função | Teclas da linha/coluna |
|---|---|---|
| 1–4 | L1–L4 | 1/2/3/A; 4/5/6/B; 7/8/9/C; */0/#/D |
| 5–8 | C1–C4 | 1/4/7/*; 2/5/8/0; 3/6/9/#; A/B/C/D |

FAQ informada pelo usuário: 77,0×70,0×0,8 mm; cabo 86 mm; peso 10 g; conector de 8 pinos, passo 2,54 mm; adesivo; limites citados de 35 VDC/100 mA, isolamento 100 MΩ a 100 V, contato 5 ms, um milhão de ciclos por tecla e 0–70 °C. Preservam-se como afirmações da FAQ, sem reinterpretar 5 ms como garantia de debounce, 100 mA como corrente recomendada ou 35 V como alimentação do teclado. Trata-se de matriz de contatos, não periférico alimentado por esses limites.

O projeto mantém as quatro membranas intactas, sem diodos individuais. Linhas correspondentes podem formar as quatro linhas de varredura e cada módulo fornece quatro colunas, total de 16. Linhas não selecionadas devem ficar Hi-Z; é necessária proteção e limitação de corrente dimensionadas, pull-ups, tempo de assentamento e debounce. Não há reconhecimento irrestrito de teclas simultâneas: manter tratamento de ambiguidade/ghosting da engenharia de teclado.

Antes da liberação: confirmar nas quatro unidades a continuidade das 16 teclas, orientação física/passo do cabo, resistência de contato, capacitância/cabo e comportamento de bounce. Um teste simples é 1 fechar L1–C1, A fechar L1–C4 e D fechar L4–C4; completar todas as teclas. As imagens resolvem a referência de pinagem, mas não substituem esses ensaios nem o esquema/validação da interface.
