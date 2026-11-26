# ISA-1 — Revisão 1.6: risco de contenção e correções arquiteturais
Data: 2026-11-23. Status: estudo de engenharia e simulação abstrata; **não liberado para PCB**.

## Origem auditada
Rev. 1.5 (`ISA-1_REV15_RELATORIO.md`, `isa1_rev15_bus_cycle.py`): o seletor one-hot é verificado em estado estável, mas não inclui atrasos reais de desabilitação/habilitação, glitches, tempos da SRAM nem circuitos por pino. O teste de colisão anterior injeta fontes simultâneas; **não prova ausência de sobreposição durante uma troca real**.

## Falha reproduzida
O modelo de eventos da Rev. 1.6 demonstra um contraexemplo: ao retirar A do barramento e habilitar RAM no mesmo instante, uma saída com atraso de desabilitação de 12 unidades e outra com atraso de habilitação de 7 unidades conduzem simultaneamente por 5 unidades. Valores são **hipotéticos**, não especificações de 74HC ou SRAM. A existência do risco está demonstrada no modelo, mas sua duração real não está quantificada.

## Correção proposta C16-A: barramento interno por multiplexadores
- Preferir caminhos internos de dados selecionados por multiplexadores, em vez de múltiplos drivers tri-state competindo pelo mesmo nó. Isso elimina *contenção entre fontes internas* na topologia, embora glitches na saída do mux e setup/hold dos registradores continuem exigindo análise.
- Candidatos: 74HC153 (dois multiplexadores 4:1, quatro CIs para selecionar 8 bits entre quatro fontes), ou 74HC157 (quatro canais 2:1 por CI, cascata conforme topologia). **Referências funcionais, não pinagem aprovada nem BOM.**
- Não conectar saídas push-pull de múltiplos muxes juntas. Registradores capturam somente depois de seleção estabilizada.

## Correção proposta C16-B: barramento externo RAM com fases explícitas
- Definir fases IDLE/READ/WRITE, com IDLE (drivers inativos) entre troca de direção; durante RESET, SRAM /OE=/WE=1 e drivers CPU desabilitados.
- READ: CPU não dirige dados; SRAM /CE=0, /OE=0, /WE=1.
- WRITE: CPU dirige dados; SRAM /CE=0, /OE=1, /WE=0. Endereço e dados estáveis antes do pulso de escrita e mantidos após, conforme datasheet.
- IDLE: /OE=/WE=1, CPU não dirige dados; /CE pode ser 1 conforme mapa e política de energia.
- Implementar transições em sequenciador **registrado** com estados de guarda; não depender de portas combinacionais com glitches para gerar /OE e /WE. As transições do clock, reset e habilitação precisam de análise temporal.
- O tempo de guarda não é fixado aqui: escolher a partir dos **máximos de desabilitação**, **mínimos de habilitação**, tempos de RAM, tolerâncias, variação de tensão/temperatura e margem. Não inferir que 30 ns bastam a partir do teste abstrato.

## Resultado executado
`python3 isa1_rev16_bus_safety.py`: **PASS 2959 verificações**: um contraexemplo de sobreposição, 1922 cenários de atrasos abstratos (0–30 unidades; lacuna 0 ou 30), três modos da SRAM, nove sequências de fases e 1024 verificações de seleção mux. Esses testes demonstram consistência **do modelo**, não dos CIs.

## Riscos remanescentes
1. Ainda não há esquemático pin-to-pin nem netlist simulável de 74HC153, 74HC574, 74HC245 ou SRAM.
2. Não há validação de tempos de setup/hold, glitches de seleção, cargas, níveis CMOS/TTL, alimentação, desacoplamento ou integridade de sinal.
3. SRAM de 32 KB em mapa descontínuo 0x4000–0xBFFF requer decodificação correta: se selecionada apenas quando A15 XOR A14 = 1, usar SRAM A14 = CPU A15 e SRAM A0..A13 = CPU A0..A13; verificar com modelo de endereços antes de congelar.
4. Arbitragem CPU/vídeo e vídeo composto colorido permanecem em aberto.
5. Sem ferramenta HDL/SPICE/KiCad instalada no ambiente nesta revisão; não alegar simulação elétrica.

## Próximos gates
G1: fechar diagrama de blocos e mapa de memória; G2: selecionar fabricantes/part numbers e conferir datasheets; G3: desenhar netlist real e conferir pinagem; G4: simular atrasos e ciclos SRAM; G5: validar firmware mínimo e integração de vídeo/teclado; G6: ERC/DRC e revisão independente; G7: protótipo físico. **Nenhuma fabricação autorizada.**
