# ISA-1 — Revisão 6.7: RGB332

Formato RRR GGG BB, 160×120, um byte por pixel, VRAM 32 KiB com stride 256. Clock lógico 6,29375 MHz. Alimentação de 12 V removida da arquitetura proposta; monitor alimentado separadamente.

Modelo estático de Thévenin: saídas ideais de 0/VCC com resistência série hipotética de 0/25/50 ohms, carga 75 ohms ±5%, VCC 4,75/5/5,25 V, resistores ±1%. Não são limites garantidos de um CI. Primeira rede 750/1500/3000 e 680/1360 ohms apresentou pico nominal de 0,745 V e 0,710 V; revisada para 820/1640/3280 e 700/1400 ohms. Valores alvo, não BOM comercial fechada. Ver JSON e CSV gerados pelo script.

581 verificações: 256 codificações, unicidade nominal da paleta e 324 cenários de monotonicidade. Não há critério de aprovação de amplitude ou corrente no script. Não é SPICE, ERC ou ensaio físico.

Candidato: registrador octal com blanking ativo para preto, seguido de buffer octal se necessário. Não usar alta impedância como substituto de blanking sem análise. Verificar datasheet de VOH/VOL, corrente por pino e total, capacitância, transientes, tolerâncias e níveis de sincronismo. Medir com carga de 75 ohms e osciloscópio. Conversor VGA-HDMI e Arzopa ainda não validados. Próxima revisão: contadores H/V, arbitragem VRAM e orçamento de alimentação 5 V. RGB332 aprovado como formato digital, DAC ainda não aprovado para fabricação.
