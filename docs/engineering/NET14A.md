# NET-14A — contrato de relógio, raster e captura

25/11/2026, base NET-13 `9fae1298a3cd74844d294464bfdd0541241815af`. Pré-projeto e teste de integração de um contrato executável; não é um novo circuito de raster por pinos, nem fechamento elétrico da placa. Os esquemas e modelos NET-13 permanecem intactos.

## Contrato proposto

Estímulo ideal de 25,175 MHz; cada pixel lógico ocupa quatro períodos, preservando 160 × 120, passo de linha de VRAM de 256 bytes e quatro linhas físicas por linha lógica. H percorre 0..199 e V, 0..524. Visível: H<160 e V<480. HSYNC baixo em H=164..187; VSYNC baixo em V=490..491. A referência de timing é o material primário de [Stephen A. Edwards, Columbia University, Video, 2023, páginas 26–28](https://www.cs.columbia.edu/~sedwards/classes/2023/4840-spring/video.pdf); bordas são incorporadas aos intervalos de apagamento. Frequência de fonte e tolerância de oscilador ainda não são uma escolha de BOM.

Na fase 0, o modelo emite o endereço; na fase 2, sobe o clock do backend de memória; na fase 3, captura dados, visível e sincronismos com as mesmas coordenadas. O backend cai na próxima fase 0. A concessão ideal usa H=161..192. Essa separação cria tempo para acomodação dos dados e mantém o contrato de backend próximo ao período de 158,89 ns da NET-13, mas o gerador real de clocks e SLOT ainda deve ser implementado/validado sem hazards.

## Orçamento condicional e alternativas

O [SN74LV163A SCLS405G, seção 4.11](https://www.ti.com/lit/ds/symlink/sn74lv163a.pdf) informa CLK→Q máximo de 11,5 ns com CL=50 pF, VCC=5 V ±0,5 V, na faixa recomendada de temperatura. É o atraso de emissão usado neste contrato; não foi construído um contador LV163 completo e decodificado nem demonstrada sua carga final. Somando 11,5 ns + mux 12 ns + SRAM 20 ns + receptor HCT244 42 ns + setup 25 ns + orçamento proposto de incerteza 5 ns, a captura em três quartos do período lógico tem margem de cerca de 3,66 ns. A meia fase tem margem negativa, cerca de −36,06 ns. Os limites de cada memória/buffer continuam sujeitos às condições de carga registradas na NET-13.

Os 5 ns são um orçamento de projeto, não skew/jitter medido ou extraído. O modelo de vídeo não aplica essa incerteza às formas de onda; o cálculo a desconta separadamente. O teste funcional de captura usa 25 ns de setup e 5 ns de hold. Com mínimo de contaminação conservador igual a zero, o cálculo deixa cerca de 29,72 ns após hold e incerteza na fase 3; isso não substitui a análise real de clocks, caminhos rápidos e reset. Com CLK→Q de 20 ns, o orçamento de setup já falha: há pouca margem para acrescentar lógica antes do endereço.

O [SN74HCT574 SCLS177H, seção 4.5](https://www.ti.com/lit/ds/symlink/sn74hct574.pdf) exige setup 25 ns, hold 5 ns, pulso mínimo de 20 ns e clock até 24 MHz a 4,5 V. O [SN74HC74 SCLS094F, seção 6.7](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf) permite até 25 MHz e pulso mínimo de 20 ns a 4,5 V, −40..85 °C. Logo, ligar qualquer um diretamente ao estímulo de 25,175 MHz não é qualificado por esses limites: o meio período é cerca de 19,86 ns. Uma captura dividida em 6,29375 MHz, com pulso de um período mestre, cabe nesses dois limites do HCT574, mas ainda exige um circuito real e análise de clock. Não aprovar componentes a partir de valores típicos, nem substituir a análise por um clock combinacional decodificado.

Alternativas: meia fase foi rejeitada para o caminho atual; clock mestre direto nos HC74/HCT574 citados foi rejeitado pelos limites; captura em fase 3 é candidata condicional. Se o circuito real consumir a margem, reavaliar receptor/captura, pipeline e alinhamento de sincronismos, mantendo o mapa de vídeo e a arbitragem. Nenhum CI novo é homologado nesta etapa.

## Testes executados

`python3 tools/run_video_contract.py`, no WSL Ubuntu, com Icarus 12 e fontes identificadas por SHA-256 em `verification/net14a/results.json`.

- Raster/clock/captura comportamentais ligados ao decoder, controlador e barramento NET-13 derivados dos pinos KiCad. Memória com atrasos selecionados e ativação antecipada de drivers.
- Dois quadros: 210.000 amostras, 153.600 pixels visíveis, 25.200 amostras de HSYNC baixo e 800 de VSYNC baixo. Confere coordenadas, bordas, apagamento preto, endereço e padrão de dados independente; sem deslocar imagem em um pixel/linha.
- 2.012 escritas de CPU simulada em região não visível da VRAM, sem abortos, enquanto o vídeo é lido. Percorre todas as 32 posições de início da concessão. Não é execução de firmware da CPU.
- Negativos: captura em meia fase deve dar erro de dados; emissão com 25 ns deve violar setup; perturbação injetada 1 ns após captura deve violar hold. O terceiro calibra o monitor, não representa um modelo analógico de pad.
- Primeiro ensaio preservado em `verification/net14a/development`: pixels/sincronismos passaram, porém o tráfego saturado cobriu apenas parte das posições de concessão. A fixture final acrescenta varredura explícita da chegada do pedido; o ensaio inicial continua registrado como falha.

O conteúdo da VRAM é explicitamente semeado para esta fixture. Não se presume SRAM inicializada no produto, não há novo boot de CPU nesta etapa e não se altera o boot completo já aceito na NET-13. O registrador de captura é ideal com monitores de abertura, sem atraso CLK→Q de saída, DAC ou carga de monitor. Reset é estímulo digital inicial; falhas/rampas e ordem WE/bancos/posse permanecem pendentes.

## Próxima implementação

Construir contador/divisão/decodificação e captura em CIs reais e KiCad, usando este contrato como referência de equivalência. Rever o atraso desde o clock até endereço, fanout, pulso mínimo, inicialização, concessão/SLOT e alinhamento de RGB/sincronismos. Em seguida integrar à CPU e tratar DAC, MMIO/teclado e reset/alimentação. Estado consolidado em [VALIDATION_STATUS](VALIDATION_STATUS.md). Produção não liberada.
