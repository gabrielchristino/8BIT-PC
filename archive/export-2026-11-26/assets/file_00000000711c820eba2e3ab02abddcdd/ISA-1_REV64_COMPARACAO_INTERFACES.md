# ISA-1 — Revisão 6.4: comparação de interfaces de vídeo

## Decisão provisória
**Priorizar a avaliação de TFT com GRAM interna e barramento paralelo de 8 bits (8080/I80), como módulo com ILI9341, em vez de desenvolver NTSC discreto.** Não escolher módulo por nome do controlador: confirmar no anúncio/esquema que os pinos I80 estão realmente expostos. A alternativa SPI permanece como plano B para atualizações parciais. Não encomendar PCB ainda.

## Fontes técnicas
- Datasheet ILI9341: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2018/02/ILI9341_v1.11.pdf — GRAM interna, interfaces SPI e I80, lógica 1,65–3,3 V.
- Módulo Elecrow SPI: https://m.elecrow.com/pages/shop/product/details?id=208108 — 2,4", 320×240, pinos SPI, lógica 3,3 V; **não** assumir I80 neste módulo.
- Tela RGB 4,3" Adafruit: https://www.adafruit.com/product/1591 — 480×272, RGB de varredura contínua, sem GRAM; não é equivalente a TFT com controlador de comandos.
- Tela RGB 4,3" Winstar: https://www.winstar.com.tw/products/tft-lcd/module/480x272-resolution.html — RGB TTL 24 bits, sem placa controladora.

## Hipóteses da bancada matemática
128×96 pixels lógicos, 4 bpp = 6.144 bytes de framebuffer local; envio RGB565 = 2 bytes/pixel; escala 1× (128×96) ou 2× (256×192) feita pelo transmissor. Velocidades SPI 4/8/12 MHz e I80 equivalente a 1 ou 2 MB/s são **cenários assumidos**, não taxas garantidas por circuitos 74HC. Transferência é limite inferior, sem comandos, esperas, conversão, sincronização de escrita ou atualização de linhas.

## Resultado principal
Para 128×96 em RGB565, são 24.576 bytes por atualização; SPI a 8 MHz precisa no mínimo 24,576 ms (40,69 quadros/s ideal). Para 256×192, 98.304 bytes; SPI a 8 MHz precisa 98,304 ms (10,17 quadros/s ideal). I80 a 2 MB/s daria 12,288 ms e 49,152 ms, respectivamente, como limites ideais. Os valores reais serão piores. Para imagens estáticas ou janelas pequenas, a GRAM reduz muito o tráfego.

## Arquitetura candidata
CPU 74HC de 8 bits e SRAM 32 KB a 5 V -> interface de E/S mapeada -> FIFO/registradores de comando e pixel -> conversão 5 V para 3,3 V com buffers adequados -> módulo TFT com GRAM interna (preferencialmente I80 8 bits). A CPU não precisa refrescar pixels continuamente; para não monopolizar a CPU durante grandes atualizações, um motor de transferência com DMA ou FIFO autônomo deve ser estudado. **Sem esse motor, a CPU pode ficar ocupada escrevendo pixels**, apesar de a tela não apagar.

## Riscos e verificações pendentes
1. Escolher módulo I80 real, disponibilidade, preço total entregue ao Brasil e interface elétrica.
2. Definir lógica 5 V/3,3 V e /WR, /RD, /CS, D/C, RESET, temporizações e fanout.
3. Resolver formato 4bpp -> RGB565 (paleta de 16 entradas) e eventual escala 2×.
4. Dimensionar FIFO ou DMA e arbitrar SRAM principal versus framebuffer; não assumir que 8 KB bastam para quadros 256×192.
5. Reavaliar 4,3" com controlador e GRAM: telas RGB TTL de 4,3" sem GRAM não simplificam o ISA-1.
6. Validar dados no protótipo físico com analisador lógico e módulo real.

## Status
12.308 asserções matemáticas concluídas, nenhuma falha. Não é simulação elétrica, prova de clock, disponibilidade comercial ou orçamento fechado.
