# ISA-1 — Revisão 7.5 — Contrato de WAIT
Fontes locais consultadas: revisões 3.3, 5.7 e código 7.4. A convenção CALL empilha alto e baixo; RET recupera baixo e alto. A pilha deve ficar na RAM principal.
## Decisão proposta
Separar emissão de requisição, espera, commit único e rearme. Durante espera, bloquear cargas e contagens arquiteturais, mas não o controlador de handshake. Reset tem prioridade. MEM_DONE deve ser evento consumível apenas uma vez; ACK em nível não é suficiente. Endereço e dados devem permanecer estáveis até a conclusão física. Para CALL, preparar SP-1 sem alterar SP, escrever e efetivar SP no commit. Para RET, ler SP e incrementar no commit. O caminho físico SP-1 ainda precisa ser implementado ou usar temporário e microestado separado.
## Bancada
Executar python3 isa1_rev75.py. Modelo abstrato de quatro operações de pilha, com atrasos independentes, sete endereços de retorno, quatro posições de pilha e quatro combinações de flags. Não executa opcodes, não integra o handshake 7.4, não modela reset nem sinais elétricos. A invariância durante WAIT é construída no modelo, não uma prova do circuito. Não testa salto ao destino CALL nem instruções aninhadas. Resultados no JSON adjacente.
## Pendências
Reconciliar tabela de microoperações 3.3 com ISA e datapath; gerar enables reais e testar com modelo independente. HC163: /LOAD e contagem devem ser bloqueados, /CLR tem prioridade. HC377: bloquear enable. Não usar commit para manter /WE ativo. Alimentação: inventário e corrente USB-C ainda pendentes. PCB não liberada.
