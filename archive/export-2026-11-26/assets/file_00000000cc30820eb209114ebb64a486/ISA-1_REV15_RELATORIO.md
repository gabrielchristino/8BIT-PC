# ISA-1 — Rev. 1.5 — Ciclo de barramento e registradores
Data: 2026-11-23

## Decisões preservadas
CPU discreta de 8 bits com endereçamento de 16 bits, flags, pilha e CALL/RET; uma PCB SMD preferencialmente SOIC; teclado de 64 teclas separado; vídeo composto RCA com cor ainda sob investigação. Não reduzir recursos da CPU para copiar o Gigatron.

## Execução reproduzível
```
python3 isa1_rev14_logic_sim.py
python3 isa1_rev15_bus_cycle.py
```
Nesta execução, o primeiro comando passou 786.432 casos de ALU e 100.000 transições de estado. O segundo passou **61 casos determinísticos** de seleção de fontes, carregamento simultâneo dos registradores, manutenção de flags, reset e detecção abstrata de cargas inválidas. Os 61 casos incluem 40 combinações de controles, 5 resets e 16 colisões injetadas.

## O que o novo modelo estabelece
- Um barramento de dados interno de 8 bits pode ter fontes mutuamente exclusivas A, B, ALU e RAM, com seleção one-hot.
- Registradores capturam simultaneamente o valor anterior do barramento na borda de clock, evitando que um registrador recém-carregado altere o valor visto por outro na mesma borda.
- Um carregamento de registrador com barramento sem fonte é rejeitado pelo teste.
- Reset conceitual domina os carregamentos; ainda falta escolher entre reset síncrono e assíncrono no circuito real.
- O modelo rejeita seletores inválidos e verifica que nenhuma fonte é ativada durante reset.

## Limitações críticas
O código **não é uma simulação elétrica, não é uma netlist pin-to-pin e não valida nenhum CI comercial**. Ele não modela tempo de habilitação/desabilitação do 74HC245, setup/hold de 74HC574, glitches do decodificador, nível elétrico de um barramento flutuante, nem consumo e ruído. O modelo de reset é apenas uma regra lógica, não uma implementação aprovada. Os componentes 74HC283, 74HC245 e 74HC574 são **candidatos**, não BOM congelada. Não foram encontrados executáveis `iverilog`, `ngspice` ou `kicad-cli` neste ambiente nesta sessão.

## Risco de arquitetura identificado
Mesmo quando o seletor lógico é one-hot, a troca de fonte A→RAM pode produzir sobreposição transitória dos /OE reais por atraso de propagação. Portanto o próximo controlador precisa de uma fase de desabilitação (*break-before-make*) ou de uma estratégia equivalente demonstravelmente segura. Além disso, se a RAM externa compartilhar o barramento, sua /OE e /WE exigem intertravamento para impedir leitura e escrita simultâneas ou condução durante escrita.

## Próxima entrega — circuito real
1. Fixar uma proposta de registradores e barramento, com referências exatas de CIs e encapsulamentos disponíveis.
2. Consultar datasheets do fabricante para pinagem, tempos, tensão e carga; gerar tabela pin-to-pin e esquemático KiCad.
3. Projetar o sequenciador de fases do barramento e verificar intertravamento durante reset e troca de fonte.
4. Simular a netlist lógica com atrasos e o caminho crítico; testar a SRAM com /CE, /OE e /WE.
5. Somente depois aprovar a primeira PCB de teste. Nenhuma placa está liberada para fabricação.
