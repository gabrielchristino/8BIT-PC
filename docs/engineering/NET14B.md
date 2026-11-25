# NET-14B — raster e captura a partir dos pinos KiCad

25/11/2026, base NET-14A `ea529d0b7acac89abbbf07b42632f93006fd63af`. Novo circuito candidato em `hardware/video_raster`: 35 CIs, 35 capacitores propostos, 582 pinos e 29 NC. O XML exportado no KiCad 10.0.8 é conferido contra o mapa esperado e convertido em modelos de pacotes/portas. Máximo de quatro entradas internas por sinal; isso não fecha cargas/capacitâncias externas. Folha parcial, sem footprints ou aprovação de fabricação.

## Implementação

Um anel one-hot com quatro flip-flops SN74AHC74 gera as fases 0..3. Após reset a fase 3 é presetada; as demais ficam zeradas. Clocks de emissão e captura vêm das saídas dos FFs, sem decodificar portas diretamente para gerar bordas. Outro FF gera o backend com dois períodos mestre em nível alto. Todos esses FFs usam o mestre de 25,175 MHz como estímulo; um oscilador de produto e sua alimentação/qualidade ainda não foram homologados.

Cinco SN74LV161A guardam H de oito bits e V de dez bits, com clock na fase 0, enables e carga síncrona de zero para os módulos 200/525. O clear assíncrono desses contadores funciona mesmo com o clock dividido parado; o LV163 de clear síncrono não foi usado aqui. Um FF RUN mantém H=0 na primeira emissão após reset, evitando perder o primeiro pixel. Dois FFs anteriores ao reset local fazem afirmação assíncrona e liberação após duas bordas mestre; metastabilidade e MTBF não são provados por HDL.

Dois SN74AHC574 capturam cor e metadados (visível/HSYNC/VSYNC) na fase 3. Os dados vêm do HCT244 da NET-13, portanto de uma saída CMOS após a recepção TTL da SRAM. Não ligar a entrada CMOS AHC diretamente ao VOH TTL mínimo da SRAM. O apagamento preto ocorre depois do registrador, preservando o caminho SRAM→captura sem uma porta adicional; os sincronismos são capturados no mesmo clock. READY e reset impedem expor os registradores sem inicialização. DAC/monitor e diferenças físicas entre caminhos de saída continuam pendentes.

O modelo conserva 160×120 RGB332, quatro linhas físicas por linha lógica, stride de 256 bytes e H=0..199/V=0..524. A janela efetiva de concessão ao controlador continua H=161..192. SLOT é registrado na fase 0 a partir do H anterior 160..191, antes da atualização do contador, deixando tempo para o controlador. O teste verifica as 32 posições de início e a devolução da VRAM antes de pixels visíveis.

## Fontes e limites dos modelos

- [SN74AHC74 SCLS255N](https://www.ti.com/lit/ds/symlink/sn74ahc74.pdf): CLK→Q selecionado 10,5 ns a CL=50 pF; setup de dados 5 ns, hold 0,5 ns e recovery 3 ns na condição de 5 V ±0,5 V. O cenário antecipado usa 1 ns somente na fase 3, mantendo os demais caminhos lentos.
- [SN74LV161A SCLS404F](https://www.ti.com/lit/ds/symlink/sn74lv161a.pdf): clear assíncrono de 12,5 ns; CLK→Q selecionado 11,5 ns, CL=50 pF, 5 V ±0,5 V. O modelo acrescenta conservadoramente 14 ns ao RCO combinacional após Q, portanto não reproduz exatamente o limite direto CLK→RCO do fabricante. Monitores usam setup conservador de 6 ns para entradas síncronas, hold 1 ns e recovery 1,5 ns.
- [SN74AHC574 SCLS244K](https://www.ti.com/lit/ds/symlink/sn74ahc574.pdf): captura por borda positiva; setup 3 ns, hold 1,5 ns e CLK→Q selecionado 12 ns, CL=50 pF, −40..85 °C, 5 V ±0,5 V.

Portas/buffers AHC usam o cenário conservador de 10 ns já empregado na NET-13. PDFs são preservados em bytes originais, com URLs/hashes em `references/video-raster-2026-11-25.json`. O AHCT574 foi consultado como alternativa, porém não usado: o PDF SCLS245N mistura o título/tabela de latch e LE↓ com descrição/diagrama de FF CLK. A alternativa AHC574 tem requisitos explícitos de CLK↑ e recebe o barramento já convertido para CMOS. Nenhum código completo de compra, footprint, disponibilidade ou BOM foi homologado.

As condições de carga da SRAM/Hi-Z continuam as da NET-13. Os modelos não representam rampa de entrada, pads/IBIS, PCB, ruído, temperatura completa ou todas as combinações independentes de mínimos/máximos. O caso de fase 3 rápida é adversarial selecionado, não STA global. A distribuição automática por número de entradas não é uma análise elétrica de clock. Não aplicar a margem do contrato NET-14A sem recontar os caminhos reais.

## Ensaios e correções

`python3 tools/build_video_raster.py`, `python3 tools/run_video_raster.py` e `python3 tools/run_video_raster_checks.py`, no WSL Ubuntu. Os relatórios têm comandos, versões, saídas e hashes.

- Três configurações: ideal, atrasos selecionados e captura antecipada com demais caminhos lentos. Por configuração: dois quadros, 210.000 amostras, 153.600 pixels visíveis, 25.200 amostras HSYNC baixo e 800 VSYNC baixo; 2.012 escritas concorrentes em área não visível e 32 posições de concessão. Nenhum aborto de escrita nesses ensaios.
- Dezesseis cortes digitais entre RESET_N e POWER_GOOD, relógio mestre livre e 512 pixels conferidos após reinicialização. Os oito deslocamentos escolhidos **excluem a abertura de recovery do primeiro sincronizador**. Isso não valida liberação arbitrária próxima à borda, resolução de metastabilidade, MTBF ou brownout analógico. Essas análises continuam obrigatórias.
- Quatro negativos: circuito anterior com SLOT tardio rejeitado por setup no controlador; decodificação serial anterior de HSYNC rejeitada no cenário de captura rápida; CLR de contador aberto e GND de CI ligado a VCC rejeitados pelo conversor.
- Falhas intermediárias e respectivas fontes estão preservadas em `verification/net14b/development`. A fixture inicial não aplicava pulso explícito de reset e permaneceu indefinida. O monitor AHC74 usava hold de 1,5 ns: a conferência do PDF corrigiu para 0,5 ns. Não são aprovações nem falhas ocultadas do circuito final.
- O SLOT inicialmente registrado na fase 1 chegou tarde através das portas do controlador: antecipá-lo para a fase 0 resolveu o caso testado. A cadeia genérica de comparadores de HSYNC chegou tarde com captura rápida; a expressão balanceada H[7:5]=101 e H[4:2] em 1..6 preserva exatamente 164..187 e passou no mesmo cenário.

ERC parcial: 42 violações (duas de alimentação, onze entradas externas sem fonte e 29 etiquetas sem consumidores na folha), retorno nativo 5. Não foram inseridas exceções. O PDF foi renderizado e inspecionado; ainda falta o esquema unido.

## Continuidade

Integrar o raster à CPU e ao diagnóstico, repetindo os testes afetados e a comparação do quadro. MMIO/teclado ainda comportamentais; DAC, oscilador, energia/reset global, cargas/CDC/temporização completos, união de esquemas, footprints, ERC/DRC/layout e protótipo permanecem pendentes. A sincronização de reset local do vídeo não resolve a ordem global WE/bancos/posse/endereço exigida pela memória. Produção não liberada.
