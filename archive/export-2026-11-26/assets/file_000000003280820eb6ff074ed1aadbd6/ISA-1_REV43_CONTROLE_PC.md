# ISA-1 — Revisão 4.3 — Controle síncrono do PC

## Escopo
Validação **comportamental**, não elétrica, de quatro contadores de 4 bits formando PC de 16 bits. Modelo testável: `isa1_rev43_pc_control.py`.

## Decisão provisória
Quatro 74HC163 continuam candidatos. O PC precisa de quatro ações mutuamente definidas: `CLEAR`, `LOAD` (JMP/CALL/RET), `COUNT` (busca sequencial) e `HOLD`. O modelo assume prioridade `CLEAR > LOAD > COUNT > HOLD`, **a confirmar na ficha técnica da variante adquirida**. O clear é **síncrono**: não zera o PC sem borda de clock.

## Carry entre nibbles
Todos os quatro contadores recebem a **mesma borda de clock**. A habilitação do nibble `i` depende de todos os nibbles inferiores terem valor `F` **antes** da borda. Não encadear clocks por ripple. As condições combinacionais são: `E0=COUNT`, `E1=COUNT & (Q0==F)`, `E2=COUNT & (Q0==F) & (Q1==F)`, `E3=COUNT & (Q0==F) & (Q1==F) & (Q2==F)`.

## Pontos ainda não resolvidos
1. Pinagem e tabela verdade do **part number exato** de 74HC163 e suas opções SMD.
2. Temporização real da cadeia de habilitação: atraso máximo, setup/hold, skew e margem com frequência escolhida.
3. Origem física dos 16 bits de carga do PC, inclusive retorno da pilha e endereço EA, sem contenção.
4. Reset de alimentação: supervisor, oscilador, ciclos garantidos antes de liberar a CPU.
5. Conexão dos contadores ao MAR e ao microsequenciador; netlist pino a pino, ERC e simulação elétrica.

## Testes
O script cobre os 65.536 valores iniciais de PC para incremento e retenção e 100.000 amostras de prioridades de controle. Detecta um caso artificial de habilitação incorreta. Não prova comportamento elétrico, estabilidade de barramento ou PCB.

## Critério de avanço
Aprovar a alternativa 74HC163 somente após datasheet, netlist, orçamento de temporização e testes de integração de CALL/RET. A estimativa de progresso do projeto completo não deve ser confundida com percentual de validação elétrica.
