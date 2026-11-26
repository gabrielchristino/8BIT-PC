# ISA-1 — Revisão 7.4

## Decisões propostas
Reset global com liberação sincronizada por domínio; bloquear WE e buffers durante reset; limpar REQ/ACK e aguardar VIDEO_READY sincronizado antes de solicitar. VRAM não é apagada pelo reset. Saída preta até inicialização do vídeo. Uma escrita interrompida pode corromper o byte alvo; não há rollback.

## Bancada executada
`python isa1_rev74.py` — 8208 cenários, 9529880 passos temporais, 8151 cenários com reset, 5593 resets com solicitação pendente, zero falhas de asserção. Cinco períodos CPU, três vídeo, fases CPU variadas, reset de 11 passos em instantes de 0 a 994 a cada 7 passos. Sequência W/R/W/R no endereço 17, valores 91 e 203. Verifica janela de acesso, dados lidos, unicidade de escrita por época e conclusão após reset. Memória preservada entre épocas. O teste reinicia a sequência, não retoma a instrução interrompida.

## Limitações
Modelo abstrato com reset ideal simultâneo, relógios discretos, posição horizontal derivada do tempo (não reinicializa contador VGA), memória ideal e payload estável por construção. Não testa saídas físicas, metastabilidade, pulso parcial WE, queda analógica, CPU real, boot real ou todas as posições possíveis de reset. VIDEO_READY modelado por dois ciclos de vídeo e dois estágios CPU; hardware deve incluir reset de contadores e validade do sincronismo. Não é ERC nem simulação elétrica.

## Próxima etapa
Implementar contrato de commit por micro-operação, separar reset de habilitação de escrita, auditar sinais de controle e dimensionar alimentação 5 V após BOM. Reset deve ter prioridade sobre WAIT. Não liberar PCB.
