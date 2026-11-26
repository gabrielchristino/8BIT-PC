# ISA-1 — Revisão 4.6 — Auditoria estrutural e orçamento temporal do PC

## Escopo e evidência
Base: `ISA-1_REV45_PINAGEM_PC.md` e `isa1_rev45_nets.json`. O script `isa1_rev46_timing_audit.py` verifica as ligações essenciais do PC e percorre todos os 65.536 estados com contagem habilitada/desabilitada. **Não foi realizada simulação elétrica ou aferição de atrasos com datasheets nesta revisão.**

## Resultado estrutural
- Quatro SN74HC163D com clock compartilhado no pino 2; ENP (pino 7) ligado a `PC_COUNT`; ENT (pino 10) do primeiro ligado a `PC_COUNT` e dos demais ao RCO (pino 15) do contador anterior.
- `/LOAD` comum pino 9; `/CLR` comum pino 1, síncrono; dados D nos pinos 3–6.
- Quatro SN74HC157D selecionam EA ou RET antes dos dados de carga do PC; suas saídas não são tri-state.
- 131.072 casos lógicos de contagem aprovados. Isso não testa tempos de propagação nem os outros modos elétricos.

## Equação para fechar o timing
Para a cadeia de carry, adotar limite conservador:

`Tclk >= tCQ(max) + 3 × tRCO_stage(max) + tSETUP_ENT(max) + tSKEW(max) + tMARGEM`.

A fórmula é um **limite de engenharia simplificado**: é necessário confirmar na folha de dados a definição do caminho de propagação RCO e o comportamento de ENT/RCO, além de outros caminhos potencialmente críticos. Para a carga paralela EA/RET:

`Tantes_borda >= tMUX157(max) + tSETUP_D163(max) + tMARGEM` (acrescentar atraso da fonte EA/RET e do controle SEL).

A tabela JSON contém **dois exemplos aritméticos com números fictícios**, exclusivamente para demonstrar o método. Não servem para definir frequência máxima nem especificação da PCB.

## Requisitos ainda bloqueantes
1. Extrair limites de pior caso da variante exata do fabricante em 5 V e faixa térmica escolhida; computar todos os caminhos críticos, não só carry.
2. Definir a frequência de clock somente após essa análise; considerar clock lento e modo passo a passo para prototipagem.
3. Desenhar supervisor de alimentação e sequenciador de partida que garanta ao menos uma borda válida com `/CLR` ativo, já que o 163 tem clear síncrono.
4. Especificar fontes elétricas dos 16 bits EA e RET, seu fanout e estabilidade antes de `/LOAD`.
5. Verificar glitch/temporização de PC_COUNT, PC_LOAD_N, PC_SEL_RET e PC_CLR_N; não derivar clock por portas combinacionais.
6. Desacoplamento individual e integridade de alimentação; análise de cargas e fanout antes do layout.

## Decisão
**Manter 4 × SN74HC163D como candidatos preferidos**, sem declarar frequência máxima, estabilidade elétrica ou esquemático pronto. A próxima revisão deve incluir o circuito de startup/reset e a especificação dos registradores EA/RET, com verificação do pior caso temporal baseada nos datasheets oficiais.
