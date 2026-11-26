# NET-23 — Trabalho em andamento: fontes de relógio

26/11/2026. Base publicada `cbb38703c34cf119612f39ecb0255940e670f974` (NET22).
Este documento registra a proposta corrente, não uma etapa aprovada.

## Configuração a construir

Dois módulos Abracon ACH candidatos, 25,175 MHz para vídeo e 100 kHz para CPU,
alimentados pelo trilho interno proposto de 5,392 V, dentro de 4,5–5,5 V.
Pinagem de quatro pinos: 1 enable/NC, 4 GND, 5 saída, 8 VDD. Configuração
proposta L/C/T/A, faixa −40…85 °C, ±50 ppm inicial/temperatura e duty
47,5/52,5%. Enable fica em VDD, sem gate assíncrono pelo reset. Código completo
de compra e garantia específica de jitter/partida sob rampa continuam abertos.

Usar **carga padrão de 15 pF**, evitando atribuir os tempos da tabela padrão
automaticamente à opção de 50 pF. O clock de vídeo recebe uma única entrada
AHC125 de U34; seu orçamento passa a exigir até 5 pF de trilha/pads além dos
10 pF máximos de Ci na condição de 5 V. São limites para o futuro layout,
não capacitâncias medidas ou extraídas.

O clock da CPU alimentava duas entradas de U7, excedendo 15 pF já nos CIs.
Reutilizar o canal0 livre de U1 no reset: uma entrada recebe CPU_OSC e sua
saída CPU_CLK alimenta os dois ramos de U7. Mesmo número de CIs de lógica,
mais dois módulos osciladores e seus capacitores. O ciclo de 10 us da CPU
tolera a etapa adicional; pulsos e sequência de reset serão testados.

Alternativas em investigação: buffer LVC2G125 tem fonte primária TI, mas sua
capacitância de entrada precisa ser lida nas colunas corretas; valor típico
em 3,3 V não é máximo garantido em 5 V. ECS-100X pesquisado é TTL e não é
substituto CMOS direto. Dois osciladores em 3,3 V exigiriam regulação e
tradução, com nova análise de distorção dos pulsos. Nenhuma dessas alternativas
foi homologada ou implementada por haver apenas um PDF disponível.

## Verificação planejada, ainda não concluída

Esquema nativo separado, XML/pinos e orçamento de carga, modelos de oscilador
com partida/ausência de clock explícitas, sequência digital de reset e
integração SRAM/CPU/teclado. Manter supervisor analógico como forcepoint
qualificado; não declarar POR real, MTBF, jitter ou VDD inválido aprovados.
Conferir startup tardio e clock ausente sem liberar escrita, além das margens
dos pulsos e efeitos únicos de COMMIT. Antecessores NET21/22 permanecem intactos.

Continuam necessários: circuitos e análise global, fonte/USB-C/consumo/POR,
DAC, firmware de eventos, união/ERC, footprints/BOM/PCB/DRC e protótipo físico.
