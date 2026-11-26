# ISA-1 — Revisão 6.5 — seleção de display e controlador

## Escopo e origem
Continuação da revisão 6.4, inspecionada antes desta revisão. Pesquisa pública de datasheets e ofertas em 23/11/2026. Os valores anunciados não são preços finais entregues. A bancada é Python comportamental, não circuito físico.

## Comparação técnica
- **ILI9341**: 240×320, GRAM integrada de 172.800 bytes, SPI e barramento I80 de 8 bits conforme modo de configuração do CI. A interface exposta varia conforme a placa comercial. Datasheet: https://www.digikey.com/htmldatasheets/production/1640716/0/0/1/ILI9341-Datasheet.pdf
- **ILI9488**: 320×480, GRAM e interface I80 de 8 bits suportada no chip (IM[2:0]=011), mas um módulo SPI não necessariamente permite mudar de interface. Datasheet: https://downloads.4dsystems.com.au/wp-downloads/2025/08/ILI9488-Datasheet.pdf
- **Tela RCA 4,3 polegadas**: preço de monitor baixo, mas codificador CVBS, sincronismo, crominância, alimentação 12 V e framebuffer elevam custo e risco. Não descartar como possibilidade futura.
- **TFT RGB TTL sem GRAM**: requer fluxo de pixels contínuo; rejeitar por ora como solução simplificada.

## Decisão provisória
Preferir um módulo ILI9341 com **I80 8-bit realmente exposto**. Não aprovar a compra antes de obter fotos legíveis de ambos os lados, pinagem e confirmação do controlador. Manter um módulo ILI9341 SPI como plano B de bancada e uma alternativa ILI9488 I80 se houver vantagem de tamanho e custo demonstrada. A preferência não constitui especificação definitiva de tela.

## Interface proposta
CPU 74HC 5 V -> endereço de E/S -> registrador de comando/dados -> transceptor/buffer apropriado 5 V para 3,3 V -> DB[7:0], /CS, D/C, /WR, /RD, /RESET do display. A saída da tela, se lida, requer translação 3,3 V para 5 V e buffer bidirecional seguro. Não ligar 74HC de 5 V diretamente aos pinos do controlador de 3,3 V. A tensão VCC de uma placa com regulador 5 V não implica que seus pinos de sinal sejam tolerantes a 5 V.

Protocolo I80: configurar D/C, dados e /CS, baixar /WR, respeitar tempos de setup/hold e subir /WR para registrar o byte. A bancada apenas verifica a ordem lógica; não verifica ns do datasheet nem ruído.

## Modelo de atualização
Framebuffer opcional local 128×96, 4bpp, 6144 bytes, 16 entradas de paleta RGB565. Transmissão de pixels RGB565 exige 2 bytes/pixel. A tela conserva a imagem na GRAM; atualizações por retângulos evitam transmissões integrais. Escala 2× por software ou motor de cópia precisa duplicar cada pixel horizontal e verticalmente, com custo de tráfego quadruplicado.

## Desempenho ideal — sem overhead
128×96 RGB565: 24.576 bytes; SPI 8 MHz = 24,576 ms; I80 a 2 MB/s hipotéticos = 12,288 ms.
256×192 RGB565: 98.304 bytes; SPI 8 MHz = 98,304 ms; I80 a 2 MB/s hipotéticos = 49,152 ms.
32×32 RGB565: 2048 bytes; SPI 8 MHz = 2,048 ms; I80 2 MB/s = 1,024 ms.
Os números são limites inferiores de tráfego, não FPS reais. Não incluem comandos, CPU, FIFO, espera e transferência de memória.

## Testes executados
Script `isa1_rev65_display_bench.py`, resultados `isa1_rev65_results.json`, tabela `isa1_rev65_transfer_budget.csv`. 68.884 verificações, zero falhas: decodificação 4bpp, paleta RGB565, retângulos aleatórios, contagem de bytes, sequência abstrata de pulso /WR e orçamento matemático.

## Riscos abertos
1. Nenhum módulo I80 específico teve sua pinagem física confirmada; não comprar por anúncio genérico.
2. Verificar datasheet de buffers (ex.: família 74LVC compatível) e direção de leitura; dimensionar corrente de backlight e alimentação 3,3 V.
3. Definir se VRAM 8 KB é necessária: para atualização direta por comandos talvez possamos remover a VRAM dedicada, mas isso exige analisar jogos, desenho, CPU e possíveis buffers de linha. Não reduzir memória sem provar funcionalidade.
4. Dimensionar motor de transferência autônomo se for exigida animação rápida sem monopolizar CPU.
5. Testar no hardware real com analisador lógico e osciloscópio antes de fechar PCB.

## Próximo gate de aprovação
Módulo com modelo, interface, pinagem, tensão lógica e custo final verificados; simulação temporal do adaptador I80; decisão sobre VRAM/FIFO e taxa de atualização necessária.
