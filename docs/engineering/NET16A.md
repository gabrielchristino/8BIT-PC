# NET-16A — Contrato preliminar de ordem de reset

Base NET-15 `f297efb645a7cbaf75f7deee03ce805acce2dd32`, 25/11/2026. Esta etapa é análise anterior ao esquema de alimentação: não escolhe supervisor, capacitor de retenção ou BOM e não aprova uma placa.

## Ordem obrigatória

Uma falha deve primeiro bloquear WE/OE e novos commits por um caminho rápido. Só depois bancos, posse e estados podem ser apagados. Na retomada, clocks devem existir antes da liberação síncrona dos estados; acessos permanecem bloqueados até essa liberação. Usar o mesmo sinal para apagar bancos imediatamente e inibir WE por várias portas não garante essa ordem. Escrita já iniciada pode ser abortada e ficar desconhecida; não se promete rollback.

## Ensaio RC de primeira ordem

`tools/run_reset_order_envelope.py` ensaia uma proposta de atraso analógico, ainda sem circuito nativo: R=10 kohm ±1%, C efetivo=1 nF ±5%, tecnologia C0G ou equivalente com limites comprovados, fuga ±1 uA, fonte ideal em baixo de 0 a 0,3 V e em alto de 4,5 a 5,5 V. Nenhum componente real de R/C/driver foi homologado. Carga/impedância da fonte do sinal, histerese dinâmica, capacitâncias parasitas e implementação do supervisor ainda precisam entrar no esquema/análise.

Usam-se limites globais conservadores do AHC14 nos pontos de alimentação documentados, incluindo histerese mínima de 0,4 V. O cenário inicial de 3,75 V com limiar de queda de 3,35 V limita uma queda logo após a subida, sem presumir capacitor totalmente carregado. A combinação é um envelope conservador; não afirma que extremos independentes coincidam num CI real. Interpolação contínua de alimentação/PVT não foi demonstrada.

128 cenários ngspice passaram no contrato do modelo, com conferência por solução exponencial independente. Atraso mínimo de afirmação: 1,05789 us, maior que o caminho selecionado de inibição de WE de 40 ns mais guarda de 100 ns. Atraso máximo de afirmação: 17,0485 us; carga máxima até o limiar de subida: 20,6614 us. Isso permite explorar uma entrada de reset garantidamente esticada por pelo menos 30 us e liberação posterior por sincronizador. Os 35 ns adicionais considerados para afirmação são máximos selecionados de duas portas e clear, não fechamento global de cargas/mínimos.

Negativos: reduzir a capacitância para 1 pF perde a ordem, com cruzamento em aproximadamente 1,12 ns; pulso bruto de 100 ns não garante apagar bancos através desse filtro. Portanto, o RC isolado não é um circuito de reset completo: é necessário esticar a entrada, manter bloqueio de acessos e implementar liberação sincronizada. O contrato não limita duração analógica de metastabilidade nem aprova MTBF.

## Supervisor e reserva de energia

O PDF TLV803E consultado é SLVSES2J, revisão de maio de 2021; datas de indexação da busca não foram tratadas como revisão do documento. O limiar nominal de 4,63 V tem tolerância de ±2%, e o máximo de propagação citado de 50 us vale na condição de degrau/overdrive descrita na tabela, não em qualquer queda arbitrariamente próxima do limiar. O supervisor é apenas candidato consultado.

Uma triagem deliberadamente otimista aplica 50,04 us após o menor limiar, mesmo sem ter essa garantia perto do limiar. Com 470 uF nominal, tolerância −20% e carga constante de 0,5 A, a conta já leva a aproximadamente 4,471 V antes de inibir escrita, abaixo dos 4,5 V usados nos limites temporais selecionados. Portanto essa combinação simples é rejeitada. A carga de 0,5 A é cenário de estudo, não consumo medido ou orçamento aprovado da placa. A triagem não inclui ESR, quedas, regulação, temperatura, curtos nem retorno de energia; pontos que passam a conta também não recebem qualificação.

O MAX691A foi consultado no leitor web oficial, mas duas tentativas de obter o PDF original local falharam. Não se declara download completo nem seleção desse CI; a indisponibilidade do arquivo não bloqueia estudar outras opções.

## Continuidade

Reproduzir: `python3 tools/run_reset_order_envelope.py` no Ubuntu WSL. Comandos, versão ngspice, fontes/hashes, 129 decks/saídas (128 cenários e um negativo), triagem de dezesseis cenários de retenção e limitações ficam em `verification/net16`. Esta etapa não modifica o circuito CPU nem os ensaios anteriores.

Próximo trabalho: comparar supervisor/monitor com condições garantidas, arquitetura de regulação e isolamento da entrada USB-C, limite de corrente e hold-up; converter a sequência em esquema real e integrar domínios de reset aos controladores/CPU. Só depois repetir os testes de CPU/MMIO/raster com as ligações novas. Medidas das membranas seguem pendentes sem impedir esse trabalho.
