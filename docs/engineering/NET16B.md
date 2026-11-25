# NET-16B — Esquema candidato para separar bloqueio e reset

25/11/2026, mesma base NET-15 da [análise preliminar](NET16A.md). `hardware/reset_domains` tem cinco CIs, cinco capacitores de desacoplamento propostos, R de atraso e C de atraso: doze componentes, 84 pinos e treze NC. É uma folha parcial nova, ainda sem supervisor, alimentação completa ou união com a CPU.

AHC125 isola a carga RC da fonte RAW_SAFE_N. R1 de 10 kohm ±1% e C6 de 1 nF efetivo ±5%, C0G ou equivalente qualificado, alimentam dois inversores Schmitt AHC14. Esse caminho afirma o clear dos dois pares de AHC74 depois do atraso. Um par libera BANK_RESET_N no clock de backend; outro libera CPU_RESET_N no clock da CPU. ACCESS_SAFE exige RAW_SAFE_N e os dois domínios liberados. A CPU não pode compartilhar simplesmente o sincronizador do backend, pois os clocks diferem. Raster/gerador de backend deverá usar seu domínio de partida separado, para não depender da própria liberação que precisa gerar.

RAW_SAFE_N deve vir de um circuito real que garanta níveis, tempos, pulso mínimo, supervisão de tensão e reserva de energia. Esta folha não o fornece. A afirmação de reset deve permanecer ativa por pelo menos 30 us neste contrato. O atraso RC dá tempo para inibir WE antes de modificar bancos; a retomada aguarda clocks e dois estágios por domínio. Clocks parados não impedem a afirmação assíncrona atrasada e impedem a liberação do domínio correspondente.

## Envelope analógico atualizado para o buffer

`run_reset_buffered_envelope.py` é uma transformação identificada do ensaio NET-16A. As fontes de tensão agora representam limites de saída do candidato AHC125: baixo de 0 a 0,44 V e alto de 3,94 a 5,5 V. O RC exige menos de 0,6 mA durante a carga/descarga nestas condições, inferior à condição de corrente usada para os limites do buffer. Fuga do Schmitt é limitada a ±1 uA no modelo. Isso não é modelo de transistor nem homologação do CI/encapsulamento/capacitor.

128 cenários dentro do envelope do modelo passaram: afirmação mínima de 1,05789 us, máxima de 18,2919 us e carga máxima de 41,3128 us. A versão digital usa limites conservadores de afirmação de 1 e 19 us e carga de 2 e 42 us, separados dos atrasos de buffer/Schmitt/FF. O envelope analógico de primeira ordem não cobre memória de carga em trens de pulsos curtos, ruído, clamp, rampa abaixo da faixa, capacitância real, ESR ou PVT contínuo. O sinal de entrada precisa ser esticado por supervisor real; não é seguro substituir isso por um filtro isolado.

## Bancadas por pinos e suas fronteiras

XML KiCad é conferido pino a pino, incluindo endpoints e valores de R/C; o HDL segue as conexões. Apenas o trecho RC é abstraído por atraso inercial e os quatro FFs de fronteira usam a hipótese binária de resolução explicitada na NET-14C. Não foi removido monitor de recovery do modelo estrito. A exportação mostra no máximo quatro entradas internas por net, sem aprovar fanout global de reset/clock ou carga de PCB.

Dezesseis combinações de modelo ideal/temporizado, duas políticas de resolução e extremos de atraso executaram 32 cortes cada. Cada combinação também pausou a CPU onze vezes e o backend onze vezes; acessos ficaram bloqueados até ambos voltarem. Registradores HC174 de ensaio mantêm monitores temporais estritos a jusante. São registradores representativos, não o circuito completo da CPU ou suas memórias.

Uma bancada adicional posicionou dez liberações perto das bordas dos dois clocks, em cada política binária. Cada estágio de cada domínio registrou três eventos dentro da abertura de recovery, e os registradores a jusante retomaram. A variante com fronteira estrita é rejeitada por `AHC74 reset recovery violation`: isso conserva a lacuna física de metastabilidade/MTBF, não converte o problema em aprovação.

Negativos de ligação observada na fixture também rejeitam reset de estado diretamente por RAW_SAFE_N antes de WE ficar inativo e liberação de acessos sem esperar o domínio da CPU. Eles calibram os monitores; não são variantes nativas aprovadas. As falhas de sintaxe da primeira bancada de abertura, o candidato inicial só com backend e a exportação inicial fora da grade foram preservados em `development` com fontes/hashes e explicações. A posição de passivos foi corrigida na grade; bancada pertinente foi repetida.

ERC final: seis violações — três entradas sem fonte, duas alimentações sem fonte e uma etiqueta isolada. Retorno nativo 5, sem waivers. PDF/preview foram inspecionados quanto a símbolos, labels e cortes; isso não resolve as fontes globais nem aprova fabricação.

Reproduzir, no Ubuntu WSL: `python3 tools/build_reset_domains.py`, `python3 tools/run_reset_buffered_envelope.py`, `python3 tools/run_reset_domains.py`, `python3 tools/run_reset_apertures.py`, `python3 tools/check_reset_domains_erc.py`. Ambiente, comandos, fontes e resultados estão em `verification/net16`.

## Pendências antes de integrar e fabricar

Selecionar supervisor/regulação/isolamento/hold-up e fechar cenários de alimentação; ligar resets da CPU, controle de memória, bancos e MMIO aos domínios correspondentes sem apagar endereço/posse antes de bloquear WE; manter gerador de clock independente dessa espera. Recontar cargas e fechar mínimos, setup/hold/removal/recovery e MTBF. Depois repetir instruções, WAIT/COMMIT, cortes, boot/diagnóstico e quadro com MMIO nativo. Esquema unido, proteção, BOM/footprints, ERC/DRC e protótipo continuam pendentes.
