# Escopo do recomeço

## Direção estabelecida

- Computador de 8 bits com CPU de lógica discreta, baseado no Gigatron.
- Poucos componentes e montagem viável; evitar complexidade acrescentada sem
  benefício mensurável. BOM e contagem acompanham cada decisão de hardware.
- Começar pela referência existente, sem copiar todo o acervo upstream.
- Melhorias incrementais. Limite provisório: oito CIs extras no mesmo escopo.
- Preservar a possibilidade de usar as quatro membranas intactas, sem tornar
  a falta de medições um bloqueio para compreender a base.

## Questões abertas

O usuário lembra que havia limitações a melhorar, mas não quais eram.
Precisamos comparar prioridades e custo antes de adotar novos requisitos.

| Tema para investigar | Pergunta a responder |
|---|---|
| Vídeo por software | Quanto tempo resta para aplicações, e o que uma melhoria custaria? |
| Memória | Qual capacidade é necessária e quais expansões já existem? |
| Teclado | Adaptar as membranas ou manter uma interface de referência? |
| Programas | Como carregar e salvar sem circuitos excessivos? |
| Compatibilidade | Manter software Gigatron, criar extensões ou outra interface? |

Resolução/cores, vídeo independente, hardware de pilha/flags e antiga ISA não
são requisitos automaticamente herdados. Também não estão aprovados como
recursos removidos de uma futura variante: a referência e os objetivos ainda
serão comparados antes de desenhar nosso circuito.

## Critério para prosseguir

Uma proposta precisa mostrar sua lista de materiais e como será testada.
Quantidade pequena de CIs não dispensa limites elétricos, pinagem ou segurança
de escrita na presença de reset e alimentação inválida.
