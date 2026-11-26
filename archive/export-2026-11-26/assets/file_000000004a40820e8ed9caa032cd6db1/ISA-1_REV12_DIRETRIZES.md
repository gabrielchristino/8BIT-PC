# ISA-1 — Revisão 1.2 — Diretrizes de identidade
Data: 2026-11-23
Status: decisões de projeto; não constituem validação elétrica.

## Decisões aprovadas
D34 — O ISA-1 não será uma cópia do Gigatron. Ele é referência para soluções de engenharia, não uma especificação a reproduzir.
D35 — Não remover capacidades úteis da CPU apenas para reduzir o número de CIs. A otimização deve preservar funcionalidade e capacidade de programação.
D36 — Manter como objetivos: CPU discreta de 8 bits, espaço de endereçamento de 16 bits, flags úteis (incluindo zero e carry), pilha e chamadas de sub-rotina, acesso à RAM, firmware de inicialização, quatro teclados matriciais 4x4 (64 teclas), programas salvos sem PC e vídeo RCA compacto.
D37 — Avaliar vídeo composto colorido com circuito de codificação apropriado, sem presumir que os seis bits RGB do Gigatron possam ser conectados diretamente ao RCA.
D38 — Estudar aumento de frequência apenas após orçamento temporal dos CIs e das memórias. A meta de clock é consequência do circuito validado.
D39 — Redução de CIs é critério secundário a funcionalidade, robustez, disponibilidade e custo total.

## Questões em aberto
- Microarquitetura da CPU: microcódigo ou lógica de controle combinacional, comparadas por contagem real, desempenho e complexidade de PCB.
- Organização exata de ROM, RAM e EEPROM de armazenamento; interface de programação inicial e atualização segura.
- Solução de vídeo RCA colorido, padrão compatível com a tela e orçamento de tempo/acesso à VRAM.
- Frequência de operação e margens elétricas verificadas com datasheets.

## Critério de liberação
Nenhuma placa é considerada pronta para fabricação sem esquemático completo, revisão de pinagem, análise de temporização, verificação de conflitos de barramento, testes de software/microoperações e plano de prototipagem.
