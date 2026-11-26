# ISA-1 — Revisão 1.8: comparação arquitetural executável
Data: 2026-11-23

## Decisão em avaliação
Comparar (A) barramento compartilhado com fontes tri-state e (B) seleção de operandos por multiplexação com caminho de resultado separado, sem alterar os recursos arquiteturais pretendidos do ISA-1. PCB única, SMD SOIC, CPU 8-bit, flags, pilha, endereçamento 16-bit, RAM/ROM/EEPROM e vídeo RCA permanecem requisitos.

## Execução reproduzível
`python3 isa1_rev18_compare.py` gera `isa1_rev18_results.json`. Rodado com Python 3 nesta sessão. Semente fixa 1801.

## Resultados
- 50.000 instruções pseudoaleatórias (MOV, ADD, ADC, SUB, AND, OR, XOR, LOAD, STORE, CALL, RET, BRZ): estados arquiteturais idênticos entre os dois modelos, incluindo quatro registradores de trabalho, flags Z/C, SP, PC e 64KiB de memória de teste. **Limitação importante:** os dois modelos compartilham a mesma implementação abstrata das operações. Isto não constitui verificação independente de datapaths ou ISA.
- Proxy conceitual de atividade: modelo compartilhado registrou 41.713 mudanças de fonte interna e 95.852 ativações de fonte; modelo dividido registrou 95.852 seleções de mux. **Não é estimativa de consumo, ciclos, área nem contagem de CIs.**
- Controlador SRAM: 40.034 verificações de estados IDLE, READ, WRITE_SETUP, WRITE_PULSE, WRITE_HOLD; nenhum estado permitiu simultaneamente SRAM em leitura e CPU dirigindo barramento, nem /WE ativo sem condições de escrita.
- Transição temporal abstrata: atrasos de habilitação e desabilitação de 0 a 20 ticks, 441 combinações por guarda. Casos conservadoramente inseguros para guardas 0/5/10/15/20/21: 231/136/66/21/1/0. **Ticks não são nanossegundos.** O modelo só mostra o efeito de uma guarda maior que a latência de desligamento assumida.

## Avaliação
A alternativa B tem vantagem estrutural para evitar disputa *entre saídas internas* quando o mux é corretamente ligado, pois as fontes não compartilham diretamente o mesmo nó de saída. Isso não elimina glitches, violação de setup/hold, riscos no barramento externo ou problemas de fanout. O teste não prova maior clock, menor número de CIs nem superioridade definitiva. A alternativa A pode ser segura com arbitragem e controle temporal corretos.

## Correções e pendências
1. Manter **provisoriamente** a alternativa B como candidata preferida para a CPU, sem congelar a arquitetura.
2. Separar interface externa de SRAM com sinais de direção, /CE, /OE, /WE; definir fases de guarda e tempos de setup/hold com datasheets e margens.
3. Definir uma ISA mínima formal e microoperações; implementar datapaths **independentes** com netlist de CIs, não apenas um modelo funcional compartilhado.
4. Selecionar números de peça e variantes SOIC verificadas; avaliar 74HC157/153, 74HC245, 74HC574, somadores e SRAM conforme alimentação e tempos, sem homologar ainda nenhum.
5. Gerar esquemáticos KiCad com pinos reais; ERC, análise de temporização com pior caso, simulação HDL/portas e ensaio físico.
6. Não liberar PCB nem anunciar frequência, custo ou contagem de CIs antes dessas verificações.

## Limites dos testes
Nenhum simulador de portas com modelos de fabricantes, SPICE, temporização por datasheet ou circuito físico foi executado nesta revisão. O controlador foi testado por estados estáticos, **não** por transições com atrasos reais. A memória de 64KiB no modelo é uma abstração para exercitar endereços, não uma alteração no plano físico de 32KiB de SRAM.
