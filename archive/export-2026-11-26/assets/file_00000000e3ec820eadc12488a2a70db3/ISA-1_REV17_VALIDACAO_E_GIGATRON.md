# ISA-1 — Rev. 1.7: arbitragem do barramento e lições do Gigatron
Data: 2026-11-23. Status: **modelo lógico/temporal abstrato aprovado; hardware não validado**.

## Auditoria da Rev. 1.6
O teste anterior verificava uma lacuna de 30 unidades com atrasos de desligamento até 30 unidades e contava igualdade como ausência de sobreposição. A igualdade de eventos não é uma garantia física. Na Rev. 1.7 tratamos igualdade como fronteira insegura, de modo conservador.

## Experimento executado
Com `python3 isa1_rev17_turnaround.py`, enumeramos 1.764 cenários de transição, com atraso de desligamento e de habilitação de 0 a 20 unidades abstratas, e lacunas de 0, 10, 20 e 21 unidades. Cenários de possível condução simultânea: 231, 66, 1 e 0, respectivamente. Foram aprovadas 29 verificações adicionais de estados e sequências de controle. **Esses valores não são nanossegundos nem dados de 74HC/SRAM.** A simulação apenas prova que, sob esses limites assumidos, uma guarda maior que o máximo atraso de desligamento evita a sobreposição no modelo. Para o circuito real, acrescentar incertezas, skew, margens, tempos de estabilização de endereço/dados e limites de SRAM.

## Correção arquitetural provisória
1. Barramentos internos: multiplexadores em vez de juntar saídas push-pull; a saída única evita contenção entre fontes, mas não elimina glitches nem violações de setup/hold.
2. Barramento externo D[7:0]: estados IDLE, READ, WRITE_SETUP, WRITE_PULSE, WRITE_HOLD. SRAM /OE desabilitado antes de a CPU dirigir; CPU desabilitada antes de SRAM /OE habilitar. /WE só pulsa após dados e endereço estáveis. Transições de direção passam por IDLE com tempo de guarda a calcular.
3. Reset: /CE=/OE=/WE inativos e buffer de escrita da CPU desabilitado, com atenção a comportamento durante subida da alimentação.
4. Sinais críticos registrados ou habilitados por fases de clock estáveis; análise de hazards e temporização obrigatória.
5. Não fixar a frequência de clock nem o número de ciclos por instrução antes de datasheets e netlist.

## Como o Gigatron aborda o problema
A documentação oficial apresenta caminhos separados: ROM de instruções, barramento de dados selecionado entre RAM, AC, imediato D e entrada IN via buffers tri-state; barramento de resultado da ALU distinto. A unidade de controle seleciona os drivers por sinais de habilitação. O projeto também organiza a escrita da RAM na segunda fase do clock, após estabilizar endereço na primeira fase. Assim, **reduz a disputa arquitetural e temporiza a escrita**, mas não é correto afirmar que nunca exista possibilidade de contenção por atrasos ou que use um único mux para todos os dados.

Fontes:
- https://gigatronttl.eu/media/Gigatron-manual.pdf (esquemáticos, apêndice A)
- https://gigatronttl.eu/posts/482.html (blocos BUS-IN/BUS-AC/BUS-D e RAM)
- https://hackaday.io/project/20781-gigatron-ttl-microcomputer/log/56269-testing-the-ram-write-control-logic (escrita da RAM na segunda fase)
- https://cdn.hackaday.io/files/20781889094304/2018-HaD-Belgrade-GigatronTTL.pdf (arquitetura de caminhos separados)

## Próximos gates
A. Escolher SRAM e buffers SOIC específicos, obter limites de tDIS/tEN, tOE, tHZ, tLZ, tWC, tWP, tDS, tDH, tAS, tAH e condições de alimentação.
B. Criar tabela de sinais por pino e esquemático KiCad; verificar /OE, /WE, /CE, enable do 74HC245 e polaridades.
C. Simulação com tempos de datasheet, pior caso de temperatura/tensão e margem; testar transições, reset e clock.
D. Prototipar, medir com osciloscópio/analisador lógico, antes de liberar a PCB final.

A placa única SMD SOIC e a CPU funcional completa continuam decisões de projeto. Nenhum CI foi homologado nesta revisão.
