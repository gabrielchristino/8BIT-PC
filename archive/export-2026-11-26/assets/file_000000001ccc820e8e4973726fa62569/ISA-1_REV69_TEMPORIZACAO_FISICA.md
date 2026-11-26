# ISA-1 — Rev. 6.9 — Orçamento temporal preliminar

## Decisões
VGA 640x480 nominal, 160x120 RGB332, VRAM 32 KiB com stride 256, lógica 5 V. Alimentação de 12 V removida da proposta; monitor externo separado.

## Fontes primárias
- https://www.ti.com/lit/ds/symlink/sn74hc157.pdf : A/B para Y, 4,5 V, máximos 38 ns (50 pF) e 47 ns (150 pF).
- https://www.ti.com/lit/ds/symlink/sn74hc163.pdf : contador síncrono; setup e cascata ainda precisam de auditoria completa.
- https://www.issi.com/WW/pdf/62-65C256AL.pdf : SRAM 32Kx8 5 V, versões 25/45 ns, interfaces TTL.
- https://www.ti.com/product/SN74HC574 : registrador octal; avaliar HCT para entrada TTL e capacidade de corrente do DAC.

## Bancada
Executar python3 isa1_rev69.py. Resultados em isa1_rev69_results.json. Período 158,8878 ns. Orçamentos hipotéticos de contador 35/50 ns, setup 20 ns e reserva 10 ns; não são limites garantidos. SRAM 55 ns é cenário comparativo, não variante atribuída à ISSI. 7 de 12 cenários cabem no período, 5 não. Candidato 25 ns: 152 ns no cenário conservador, reserva residual 6,89 ns além dos 10 ns alocados.

## Raster e arbitragem
105000 ticks, 76800 buscas de pixel com endereço antecipado em um tick. Janela CPU h=161..196, 36 ticks, nove transações hipotéticas de quatro ticks por linha, 4725 por quadro. Teto 283218,75 bytes/s; não é throughput de CPU. O modelo não implementa transações elétricas nem CDC. Prefetch de x=0 no tick h=199 da linha anterior, inclusive na virada do quadro. A implementação deve alinhar endereço antecipado, latch e blanking, evitar pulso espúrio em HSYNC/VSYNC e provar setup/hold, especialmente na troca de proprietário.

## Pendências bloqueantes
Verificar níveis TTL da SRAM para todos receptores, selecionar HCT ou alternativa compatível; calcular DAC com VOH/VOL e corrente total. Confirmar variante e encapsulamento disponível. Auditar caminhos de controle CE/OE/WE, tempos de alta impedância, hold, reset e sincronização CPU/vídeo com handshake. Definir mapa global e janela VRAM sem perder EEPROM ou RAM. Nenhuma validação física, SPICE ou ERC foi executada nesta revisão.
