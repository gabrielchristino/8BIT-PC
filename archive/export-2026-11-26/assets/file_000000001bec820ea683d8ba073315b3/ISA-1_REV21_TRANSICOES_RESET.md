# ISA-1 — Revisão 2.1 — Transições, reset e requisitos de hardware
Data: 2026-11-23. Status: **modelo lógico parcial; PCB NÃO liberada**.

## Evidência executada
Arquivo `isa1_rev21_transition_verify.py`, executado com Python 3.
- Transição direta READ → WRITE_SETUP: 16 combinações de atrasos independentes de 0..3 ticks para os sinais alterados; pelo menos um contraexemplo de disputa SRAM × buffer.
- Transições protegidas READ ↔ WRITE_SETUP e estados repetidos: 330 combinações por fases, sem conflitos **dentro das regras do modelo**.
- Teste negativo de `/OE` da SRAM ativo durante `/WE` baixo foi detectado.
- Ticks são abstratos; **não representam ns**. Fases são consideradas totalmente estabilizadas antes da próxima. Não há SPICE, modelo elétrico, clock real ou validação física.

## Correção de engenharia candidata
1. **Reset / power-on:** manter `/CE=1`, `/OE=1`, `/WE=1`, `74HC245 /OE=1`; gerar níveis inativos por circuito de reset confiável, sem depender de firmware. Travar escrita enquanto reset está ativo.
2. **Leitura:** CPU libera o lado A do 245; `DIR=0` (lado SRAM B → CPU A); SRAM `/WE=1`; habilitar `/CE`, `/OE` e o 245 apenas após endereço estável. Não assumir que o processador deixa o lado CPU livre sem um controle explícito.
3. **Leitura → escrita:** desabilitar SRAM `/OE` e transceptor `/OE`; aguardar limites de desabilitação; alterar `DIR=1` com 245 desligado; garantir dados de CPU estáveis; habilitar transceptor e `/CE`; só depois emitir `/WE=0` respeitando setup e largura de pulso; desabilitar `/WE` e manter hold antes de nova transição.
4. **Escrita → leitura:** finalizar `/WE` e hold; desabilitar 245 e SRAM; aguardar; alterar `DIR=0`; CPU libera barramento; preparar endereço; habilitar leitura.
5. **Sequenciador:** fases de guarda devem ser implementadas por estados registrados, não por combinações de sinais suscetíveis a glitches; decodificação de endereço não pode gerar pulsos espúrios de `/WE`.

## Problema adicional identificado
A tabela de seis estados da Rev. 2.0 **não demonstra** que o lado CPU do 74HC245 está em alta impedância durante READ. Se algum registrador/buffer da CPU continuar dirigindo o barramento A, haverá disputa **no lado CPU** mesmo que a SRAM e o 245 não disputem o lado B. Precisamos de sinal CPU_BUS_OE e teste para essa interface. Também precisamos verificar como o multiplexador interno recebe dados da RAM.

## Atenção à escolha do 74HC273
O 74HC273 tem `/CLR` assíncrono e saídas push-pull permanentes. Isso é adequado para alimentar entradas de multiplexadores, mas NÃO para ligar várias saídas diretamente ao mesmo barramento. A retirada do reset deve ser sincronizada e compatível com os tempos de recuperação/remoção do componente; não há ainda circuito de reset dimensionado.

## Próximos marcos obrigatórios
- Escolher CI de supervisor de reset ou circuito equivalente e especificar clock seguro.
- Conferir em datasheets os valores de tDIS/tEN do 74HC245, tempos da SRAM tAA/tOE/tHZ/tWC/tWP/tDW/tDH e atrasos do decodificador para tensão, temperatura e carga escolhidas.
- Definir CPU_BUS_OE, intertravamento de escrita, sequência de estados registrada e tabela completa de pinos dos componentes de controle.
- Criar esquema/netlist KiCad e executar ERC/DRC; simular modelo HDL de pinos com atrasos de datasheet e analisar vídeo/ruído.
- Fazer protótipo e medir; nenhuma simulação elimina a necessidade de testes físicos.

## Decisão
**Aprovar somente o princípio** da desabilitação antes de mudar direção; não aprovar duração da guarda, frequência da CPU, circuito completo ou fabricação.
