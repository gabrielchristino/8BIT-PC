# ISA-1 — Revisão 6.2 — Codificação CVBS e clock

## Decisões
- Manter tela econômica RCA de 4,3 polegadas alimentada em 12 V, preço informado pelo usuário ~R$67. Modelo, PAL/NTSC e consumo ainda não confirmados. Alternativa de fonte independente preservada.
- Manter CPU e memória em 5 V, 128×96 pixels, 16 índices de cor, VRAM de 8 KiB com 6144 bytes para framebuffer.
- Referência para prova de conceito de codificador RGB analógico → CVBS: **AD725**, SOIC-16, +5 V; **não aprovado para BOM** porque fabricante marca Last Time Buy em 2026.
- Considerar AD724 (também Last Time Buy), AD723 (TSSOP-28, também Last Time Buy) e ADV7391 (LFCSP, 1,8/3,3 V e interface digital complexa, Not Recommended for New Designs). Nenhum é substituto de produção já aprovado.

## Interface proposta
VRAM 6264 (8 KiB) → byte de dois pixels → seleção de nibble → paleta de 16 cores → DACs analógicos RGB calibrados → AD725 RGB + HSYNC/VSYNC → saída CVBS com terminação conforme datasheet → RCA da tela.

O AD725 **não** aceita índices de paleta diretamente: necessita níveis RGB analógicos e sincronismo com temporização correta. Não ligar diretamente os quatro bits de cor aos pinos RGB. A saída composta nominal depende da carga e da terminação de 75 Ω; conferir componentes de acoplamento e resistores no circuito de referência.

## Pinagem AD725 segundo datasheet Analog Devices
1 STND (HIGH NTSC); 2 AGND; 3 4FSC; 4 APOS +5 V; 5 CE; 6 RIN; 7 GIN; 8 BIN; 9 CRMA; 10 COMP; 11 LUMA; 12 YTRAP; 13 DGND; 14 DPOS +5 V; 15 VSYNC; 16 HSYNC.
Pinagem informativa: não constitui netlist pronta. Verificar acoplamentos e valores no esquema recomendado.

## Clock: orçamento matemático testado
Fonte candidata: 14.318180 MHz = 4 × 3.579545 MHz. Linha de 910 ticks = 63.55556 µs (15,734.26 Hz). Divisão por 5: 2.863636 Mpixels/s. 128 pixels × 5 ticks = 640 ticks = 44.6984 µs. Restam 270 ticks = 18.8571 µs para regiões não ativas. A escolha de posições de sincronismo, back/front porch, burst e fase de campo NÃO foi validada. Divisor por 5 precisa de projeto síncrono próprio e análise de duty cycle. O AD725 requer entrada 4FSC estável; o divisor é apenas para a lógica de pixels.

## Validação executada
`python3 isa1_rev62_video_clock.py` passou 19.072 asserções de endereçamento, empacotamento e encaixe dos pixels na linha. Resultados em JSON e tabela de slots em CSV. Não testa conformidade NTSC, nem o 240p, nem sinais elétricos, nem desempenho da SRAM, nem decodificação pela tela.

## Problemas abertos (bloqueiam fabricação)
1. Confirmar modelo de tela barata, se aceita NTSC e PAL e seu consumo a 12 V.
2. Encontrar codificador em produção, soldável em casa e com fornecedor confiável; não aceitar peças descontinuadas sem plano de estoque/substituição.
3. Projetar paleta e DACs RGB de 16 cores e calcular impedâncias, níveis, acoplamento e sincronismo.
4. Projetar gerador horizontal/vertical e compatibilidade 240p/525i; validar oscilador e relação entre clocks.
5. Integrar a arbitragem de VRAM e estimar tempos de acesso e desabilitação.
6. Verificar ruído do boost 5→12 V e manter alternativa de fonte separada.
7. Validar com osciloscópio em carga 75 Ω e teste real da tela antes da PCB final.

## Fontes oficiais
- AD725: https://www.analog.com/en/products/ad725.html
- AD725 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/AD725.pdf
- AD725 evaluation board: https://www.analog.com/media/en/technical-documentation/evaluation-documentation/ad725_eval_board_instructions.pdf
- AD724: https://www.analog.com/en/products/ad724.html
- AD723: https://www.analog.com/en/products/ad723.html
- ADV7391: https://www.analog.com/en/products/adv7391.html

**Status:** conceito de interface e orçamento digital testados; codificador definitivo não selecionado; não há esquema elétrico validado.
