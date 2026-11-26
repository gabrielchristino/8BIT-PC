# ISA-1 — Revisão 6.0 — Arquitetura preliminar de vídeo composto colorido

## Base anterior
A rev. 5.9 implementou apenas arbitragem lógica de barramento CPU/SRAM/EEPROM/I/O, com estado de alta impedância entre proprietários. Não definiu VRAM, vídeo nem endereços absolutos. Esta revisão propõe arquitetura e testa apenas invariantes digitais.

## Requisitos preservados
CPU própria 8 bits 74HC, endereçamento 16 bits, 32 KiB SRAM, EEPROM removível AT28C256 32 KiB, tela 4,3 pol RCA composto colorido 12 V, PCB principal única, teclado externo.

## Escolha preliminar: VRAM separada 8 KiB
- Framebuffer lógico: 128 × 96 pixels, 4 bits/pixel (16 índices de cor): 6144 bytes. Sobram 2048 bytes para tabelas ou buffers; sua utilização ainda não está definida.
- VRAM dedicada: SRAM 8 KiB × 8 (família 6264, variante exata pendente). A CPU a acessa por janela mapeada; controlador de vídeo lê continuamente.
- 128 pixels ativos por linha lógica; 96 linhas lógicas. Para saída 240p/288p/entrelaçada, escalonamento de linhas e sincronismo ainda precisam ser definidos. Não confundir resolução lógica com resolução física ou padrão PAL/NTSC.
- Uma SRAM 6264 comum tem porta única: **CPU e vídeo não podem acessá-la simultaneamente**. A arquitetura necessita multiplexação de endereço/dados/controles e arbitragem com slots, ou solução alternativa (dual-port / line buffer). VRAM separada isola a SRAM principal, mas não elimina contenção dentro da própria VRAM.
- Recomenda-se avaliar buffer de linha para ler em rajadas e permitir escrita da CPU nas janelas restantes. A contagem de CIs e a capacidade de atualização ainda são pendentes.

## Mapa de 64 KiB candidato, NÃO congelado
| Janela | Uso proposto | Observação |
| --- | --- | --- |
| 0000–7FFF | SRAM principal 32 KiB | Pilha e programas em RAM |
| 8000–9FFF | VRAM 8 KiB | Janela CPU, acesso arbitrado |
| A000–BFFF | I/O, expansão, controle | Descodificação interna ainda indefinida |
| C000–FFFF | ROM/EEPROM 16 KiB visíveis | EEPROM física 32 KiB requer seleção de banco de 16 KiB ou outro mapeamento |

**Questão crítica:** a EEPROM removível de 32 KiB possui layout anterior com código até 77FFh e saves em 7800–7FFFh. A janela ROM de 16 KiB exige dois bancos e um mecanismo seguro de leitura/escrita, além de preservar os dois saves. Não implementar este mapa sem reconciliar boot, acesso aos bancos, gravação e a proteção dos saves. A janela de 8 KiB de I/O é apenas reserva de endereço, não um custo físico de 8 KiB.

## Sinal composto colorido
Gerar pixels indexados de 4 bits **não gera automaticamente vídeo composto colorido**. São necessários: temporização horizontal/vertical estável, níveis analógicos de sincronismo e luminância, crominância com subportadora e fase compatível com PAL ou NTSC, filtro/driver e terminação adequada de 75 Ω. Um codificador RGB→CVBS dedicado é candidato, mas sua disponibilidade, alimentação, interface RGB analógica e oscilador precisam de avaliação. Um DAC resistivo isolado é insuficiente para crominância colorida correta.

O circuito de vídeo deve ter temporização independente da execução de instruções, evitando que a CPU tenha de produzir cada pixel. A taxa de leitura da VRAM, clock mestre e divisão de pixels dependem do padrão escolhido. Não há ainda justificativa para afirmar compatibilidade PAL/NTSC ou ausência de interferência do boost 5→12 V.

## Testes realizados
Executar `python3 isa1_rev60_video_arch.py`. Verifica endereçamento e empacotamento de pixels (dois por byte), varredura lógica, exclusividade de decodificação das quatro janelas e uma arbitragem abstrata por slots. Os pedidos de escrita são enfileirados e o teste mede fila máxima; não modela atrasos elétricos nem vídeo analógico.

## Próxima revisão 6.1 — bloqueios de arquitetura
1. Escolher PAL ou NTSC como formato inicial, com critérios de compatibilidade da tela; definir frequências e número de linhas a partir de documentação técnica.
2. Selecionar codificador CVBS disponível e verificar interface RGB, níveis, clock, sincronismos, encapsulamento e pinagem.
3. Comparar VRAM 6264 porta única + buffer de linha versus VRAM dual-port e quantificar CIs, ciclos de CPU perdidos e complexidade.
4. Reconciliar ROM bancarizada com EEPROM 32 KiB e regiões SAVE A/B; não sacrificar capacidade nem gravação.
5. Só então fechar mapa de memória, netlist e margens temporais para futura validação EDA.

**Status:** arquitetura candidata e testes digitais aprovados no escopo. Não há circuito de vídeo composto validado, esquemático elétrico, simulação de temporização real nem autorização para fabricação.
