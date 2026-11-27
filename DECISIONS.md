# Decisões

## R01 — Recomeçar com base no Gigatron

Data: 27/11/2026. Decisão expressa do usuário.

O candidato ISA-1 chegou a 460 CIs antes de fechar toda a alimentação e VGA
analógica. Esse custo inviabiliza a direção pretendida. A partir deste ponto,
o trabalho parte do Gigatron, cujo projeto prioriza poucos componentes.

O recomeço não é uma otimização equivalente da antiga CPU. Não se declara
compatibilidade com a ISA-1, nem se transportam suas aprovações para o novo
projeto. As diferenças funcionais serão avaliadas explicitamente.

Alternativas: continuar reduzindo o circuito NET30; manter apenas a antiga ISA
e reprojetar todo o hardware; partir de uma arquitetura pequena existente.
Foi escolhida a terceira direção. FPGA, microcontrolador substituindo a CPU e
mudança de licença não foram autorizados como atalhos para reduzir a contagem.

## R02 — Arquivar antes de limpar

Preservar o último estado em branch histórica, bundle Git verificável e cópia
local dos materiais, inclusive dados que não estavam publicados. Reduzir main
por um commit normal, mantendo todos os ancestrais. Não reescrever o histórico
nem publicar a exportação privada de conta. A execução antiga deve terminar
e ter seu resultado auditado antes de mover suas fontes.

## R03 — Orçamento antes do circuito

Hipótese de trabalho: no máximo oito CIs adicionais à referência Gigatron,
com comparação de mesmo escopo e todos os encapsulamentos contabilizados.
Esse orçamento orienta a seleção de melhorias; não é estimativa já validada.

Aceitação da primeira arquitetura: BOM única com referências e quantidades,
delta explícito sobre a base, requisitos e compatibilidade escritos e modelo
executável correspondente. Não detalhar uma nova placa de centenas de CIs.

As melhorias desejadas ainda são uma questão aberta. O usuário informou que
não lembra quais eram; não foi escolhido vídeo independente, mais cores,
mais memória ou qualquer outro acréscimo por inferência.
