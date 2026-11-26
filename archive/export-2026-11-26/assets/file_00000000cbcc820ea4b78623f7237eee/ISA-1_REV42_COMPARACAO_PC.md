# ISA-1 — Revisão 4.2 — Comparação de PC com 74HC163 e 74HC283

**Resultado: 74HC163 é a opção preferida para detalhamento, mas ainda não está aprovada eletricamente.**

## Premissas
PC de 16 bits, reset em zero, incremento com wrap-around, retenção e carga arbitrária e atômica para JMP/CALL/RET. Foram inspecionados os relatórios das revisões 4.0 e 4.1. Não houve validação de datasheets ou simulação elétrica nesta revisão.

## Arquitetura A — registrador + somador
- Dois registradores octais para PC (candidatos 74HC273/377, conforme requisito de reset).
- Quatro 74HC283, em cascata, para PC+1.
- Mux 3:1 de 16 bits para PC+1, EA (JMP/CALL) e retorno reconstruído (RET): oito 74HC157 em duas camadas, antes de otimização.
- **Subtotal preliminar: 14 encapsulamentos**. A seleção de carga, reset e clock pode exigir lógica adicional.

## Arquitetura B — quatro contadores 74HC163
- Quatro contadores síncronos de 4 bits, com carga paralela, compõem PC[15:0].
- Incremento simultâneo por nibble com habilitação do nibble superior condicionada a todos os nibbles inferiores serem `0xF` *antes* da borda do clock.
- Mux 2:1 de 16 bits para EA versus retorno reconstruído: quatro 74HC157. O incremento é interno aos contadores; não ocupa entrada do mux.
- **Subtotal preliminar: 8 encapsulamentos, mais lógica de habilitação de carry** (ao menos um encapsulamento de portas, dependente da implementação), decodificação e controle. A economia estimada é **até cerca de cinco encapsulamentos** nesta subfunção, sem incluir demais caminhos.
- O 74HC163 é um contador com *clear síncrono* na variante clássica: **não presumir reset assíncrono**. É necessário verificar o fabricante/part number e a estratégia de reset antes de escolher o componente definitivo.

## Teste de regressão
`python3 isa1_rev42_pc_comparison.py` compara duas implementações independentes contra uma referência. Executa LOAD+INC para **todos os 65.536 valores** de PC; bordas e overflow; e 200.000 transições pseudoaleatórias de INC/HOLD/JMP/CALL/RET/RESET. As implementações foram modeladas em nibbles e somadores separados, mas **não** em portas elétricas reais.

## O que ainda impede aprovação da PCB
1. Conferir o datasheet **do fabricante e sufixo de compra exatos** para 74HC163: pinos, prioridade de /LOAD, /CLR, ENP/ENT, ripple terminal count, tempos máximos, setup/hold e comportamento de reset.
2. Comprovar que o sinal de carry de cada nibble chega estável ao próximo **antes da borda**, e que as habilitações não mudam durante a janela crítica.
3. Especificar PC carregando simultaneamente os bytes de EA e RET, sem competição de barramento.
4. Testar microcódigo real com JMP, CALL, RET e flags; o teste atual não exercita a pilha física.
5. Definir clock alvo e orçamento de atraso; simular/medir reset e sequenciamento antes do layout.

## Decisão
**Promover a arquitetura 74HC163 para candidata preferida**, condicionada à validação de datasheet, lógica de habilitação e integração com CALL/RET. Manter 74HC283 + registradores como alternativa de menor dependência de controle de carry, não como vencedora de BOM.
