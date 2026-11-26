# ISA-1 — Revisão 7.3

## Decisões propostas
Handshake de quatro fases REQ/ACK, com sincronização de dois estágios em cada direção. Manter endereço, banco e dados até ACK reconhecido. Não emitir novo REQ antes de ACK sincronizado voltar a zero. Congelar efeitos arquiteturais da microinstrução pendente, não o clock. Commit único no reconhecimento do ACK.

## Bancada executada
`python isa1_rev73.py`: 51.200 cenários, 6.900 completos com três escritas cada, 44.300 encerrados por reset injetado. Seis relações de período (1,2,3,5,8,13), todas as fases inteiras, 200 posições iniciais e oito opções de reset. Sem falhas de assert. Modelo discreto, não simulação elétrica. Reset encerra o teste; rearme não verificado. PC abstrato; não é microcódigo real. Não testa leitura nem endereços físicos. Janela de início H=161..192; conclusão até H=196. Sincronizadores idealizados; não modelam metastabilidade.

## Próximos passos
Integrar enable de cada registrador e contador, distinguir commit e rearme, testar reset independente e conjunto com recuperação, validar sinais físicos e temporização. Orçamento de alimentação depende da BOM e atividade real. Manter 5 V, sem boost 12 V, monitor separado. USB-C requer detecção da corrente anunciada; não presumir potência do carregador. Não liberar PCB.
