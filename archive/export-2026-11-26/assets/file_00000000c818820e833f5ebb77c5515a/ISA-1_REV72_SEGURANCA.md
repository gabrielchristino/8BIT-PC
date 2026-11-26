# ISA-1 — Revisão 7.2

## Contrato proposto
Preservar PC, SP, flags, registradores, microsequenciador e pedido durante WAIT. Não bloquear o clock por lógica combinacional. A confirmação deve liberar exatamente uma micro-operação. REQ e ACK precisam de sincronização e retorno a zero antes de novo pedido.

## Proteção
WE_N = NOT(POWER_GOOD AND RUN AND GRANT AND WRITE AND ACCESS). A implementação deve impedir glitches, respeitar setup/hold e bloquear novas escritas no reset. Escrita interrompida pode corromper o byte. Reset deve abortar ambos os lados do handshake e impedir confirmação antiga. Saídas SRAM e buffer devem ser desabilitadas antes de alterar direção ou endereço. Supervisão de alimentação não garante proteção até zero volts.

## Máquina proposta
WAIT, SELECT, ACCESS, RELEASE, RESTORE, ACK. Início permitido H=161..193; retorno ao vídeo até H=197. H=199 reservado para prefetch. A janela não comprova tempos elétricos. ACK mantido até REQ desativado; rearmar somente após ACK baixo. Candidatos: HC74 sincronizadores, HC163 sequenciador, HCT245 interface, HCT574 leitura. Não fechar BOM antes de verificar temporização e equações.

## Teste executado
isa1_rev72.py: 168400 cenários, 28099352 asserções, 108288 concluídos, 60112 abortados. Falhas injetadas nas fronteiras dos ciclos; CPU imutável por construção; sem teste de transações consecutivas, CDC, metastabilidade, reset analógico, ou circuito real. Não constitui ERC ou liberação de PCB.

## Pendências
Integrar WAIT ao microcódigo real, testar pedidos consecutivos e reset/rearme, verificar sinais registrados e tempos de SRAM/buffers, revisar orçamento USB-C 5 V e supervisor. Sem linha 12 V. Manter RGB332 e CPU completa.
