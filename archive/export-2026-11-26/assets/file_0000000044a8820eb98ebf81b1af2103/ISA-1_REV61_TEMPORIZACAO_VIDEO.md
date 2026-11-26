# ISA-1 — Revisão 6.1 — Vídeo, temporização e VRAM

## Decisão provisória
Adotar **NTSC-M como alvo de desenvolvimento**, com saída CVBS de 75 ohms, sem declarar ainda compatibilidade elétrica com a tela de 12 V (modelo não identificado). A tela poderá aceitar PAL e NTSC, mas isso precisa ser confirmado no anúncio/manual. O padrão PAL permanece opção de revisão posterior.

## Referência temporal nominal (não medida)
NTSC-M convencional: frequência horizontal aproximada 15.734 kHz (período ~63,56 µs), 59,94 campos/s, 525 linhas por quadro entrelaçado; subportadora de cor ~3,579545 MHz. A geração de 240 linhas progressivas compatíveis com receptores analógicos ('240p') é uma estratégia prática não formalizada como o padrão entrelaçado; **a compatibilidade com a tela precisa ser testada**. Usar aproximadamente 52 µs de região ativa por linha apenas para orçamento inicial, não como especificação definitiva.

128 pixels lógicos / 52 µs = 2,46 Mpixels/s; com dois pixels por byte, 64 leituras por linha lógica = 1,23 Mleituras/s durante a região ativa. A repetição vertical de 96 para ~240 linhas exige cadência não uniforme (2 e 3 linhas físicas por linha lógica, se não houver reamostragem); não assumir uma relação inteira. Um buffer de linha de 64 bytes permitiria ler a VRAM uma vez por linha lógica e repetir os dados, desde que a arquitetura suporte a saída contínua.

## Alternativas de acesso à VRAM
A) 6264 de 8 KiB, porta única, multiplexação de endereço e acesso por slots. Vantagem: SRAM comum e custo previsível. Desvantagem: arbitragem, mux e margens de temporização; CPU pode esperar.
B) 6264 + buffer de linha (64 bytes): reduz pressão de leituras repetidas na VRAM, mas requer armazenamento adicional e lógica de preenchimento/saída. O número exato de CIs depende da implementação do buffer (shift registers, SRAM auxiliar ou registradores).
C) SRAM dual-port: simplifica a disputa, mas disponibilidade, preço, encapsulamento e consumo não estão comprovados. Não aprovada.

**Escolha para prototipagem lógica:** opção A, com possibilidade de evoluir para B. Não declarar que A atende temporização real até escolher SRAM, clock e lógica.

## Cor analógica — bloqueio principal
O índice de cor de 4 bits precisa virar níveis RGB ou YUV e ser modulado em crominância e luminância com sincronismo. O codificador CVBS dedicado **ainda não foi escolhido**. Um candidato de pesquisa é a família AD724/AD725, mas disponibilidade, alimentação, níveis RGB, necessidade de clock e encapsulamento exigem datasheet e fornecedor antes de entrar na BOM. Não assumir que um DAC resistivo RGB simples produza NTSC colorido.

## Testes reproduzíveis
`python3 isa1_rev61_video_timing.py`: 67.127 verificações de indexação de framebuffer, endereços de EEPROM em dois bancos e arbitragem sintética de 256 slots/linha (64 reservados ao vídeo, 192 disponíveis à CPU). A fila de escritas é sintética, sem garantias de vazão física. Não há modelo de temporização de SRAM, encoder ou nível analógico.

## EEPROM e mapa de memória
Preservar 32 KiB da AT28C256 e os dois saves nos últimos 2 KiB físicos. Se usar janela de 16 KiB, banco 0 = EEPROM 0000–3FFF, banco 1 = 4000–7FFF; SAVE A 7800–7BFF e SAVE B 7C00–7FFF físicos, visíveis somente no banco 1 em offsets 3800–3FFF. O reset deve selecionar banco de boot conhecido; operações de gravação exigem proteção adicional e não podem depender somente da seleção do banco.

## Bloqueios antes da PCB
1. Identificar tela RCA 12 V e seus padrões de vídeo.
2. Escolher codificador RGB→CVBS com datasheet e fornecedor verificáveis.
3. Selecionar variante de SRAM 6264 e calcular tempos de acesso, desabilitação e margem de arbitragem.
4. Definir clock mestre e derivação do pixel clock e subportadora de cor sem jitter excessivo.
5. Fechar mapa de memória e registrador de bancos EEPROM, incluindo boot e SAVE.
6. Testar saída composta com carga de 75 ohms, integridade de sincronismo e interferência do boost.

**Status:** revisão digital e orçamento temporal preliminar; não é simulação elétrica, nem ERC, nem aprovação de fabricação.
