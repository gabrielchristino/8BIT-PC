# ISA-1 — Revisão 7.1
## Contrato preliminar CPU–VRAM
Mantidos RGB332, 160×120, VRAM 32 KiB, clock de vídeo 6,29375 MHz e alimentação 5 V.
Handshake de quatro fases: REQ sobe, ACK sobe após restauração, REQ desce, ACK desce. Nova solicitação somente após ACK baixo sincronizado. Endereço, banco, direção e dados permanecem estáveis até confirmação. Leitura requer registro de retorno estável até reconhecimento. CPU deve congelar avanço de microestado e efeitos colaterais durante WAIT, sem bloquear clock por lógica combinacional.
Estados VIDEO, SELECT, ACCESS, RELEASE, RESTORE. Admissão conservadora H=161..193; busca de vídeo H=0..158 e 199 (prefetch). Modelo reserva quatro ciclos após admissão; duração 635,55 ns. Acesso físico exige intervalos de alta impedância antes da mudança de direção e validação de OE/WE, setup, hold, SRAM e mux. ACK não significa que nova solicitação já pode começar.
## Resultados
12.800 casos isolados, 2.479.018 iterações, zero falhas nas assertivas. Períodos CPU em ticks 1,2,3,5,8,13; todas as fases inteiras; 200 posições de chegada; leitura/escrita. Verifica exatamente uma operação e confirmação, exclusão lógica e ausência de conflito com prefetch. Não simula dados reais, tráfego consecutivo, reset, metastabilidade, atrasos elétricos ou quadro vertical completo. Não é ERC nem simulação elétrica.
## Próximos passos
Validar transações consecutivas, reset em cada fase, registro de leitura, CDC de dados agrupados e congelamento de microestado. Candidatos: 74HC74 para sincronizadores (dois encapsulamentos para quatro FF), 74HCT245 para interface TTL/CMOS, 74HCT574 para registro de retorno; quantidades e temporização pendentes. Inibir WE durante reset e perda de alimentação. Não liberar fabricação.
