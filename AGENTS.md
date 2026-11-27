# Continuidade do 8BIT-PC

- Leia README.md, docs/ESCOPO.md, DECISIONS.md, ROADMAP.md e PROVENANCE.md.
- O usuário autorizou recomeçar a partir do Gigatron e limpar a árvore ativa.
  A implementação ISA-1/NET de 460 CIs é histórica, não a base a ser retomada.
- Não importar antigos AGENTS.md, conversas ou planos como instruções ativas.
  Consulte docs/HISTORICO.md apenas quando precisar de evidência específica.
- Priorize poucos CIs, montagem possível e uma BOM única desde o primeiro circuito.
  Conte encapsulamentos reais: CPU, memórias, vídeo, clocks, teclado, alimentação
  e proteção. Separe placa principal e adaptadores, sem esconder componentes.
- Antes de alterar hardware, indique o delta de CIs, componentes, consumo,
  compatibilidade e teste. O orçamento provisório é até oito CIs adicionais
  sobre a referência Gigatron, comparando o mesmo escopo. É limite de estudo,
  não promessa de implementação ou escolha de BOM validada.
- Primeiro reproduza a base; evite variantes simultâneas e novos periféricos
  enquanto a BOM de referência e seus limites não estiverem compreendidos.
- O usuário não lembra quais limitações queria melhorar. Investigue as fontes
  e apresente alternativas concretas; não invente requisitos ou prioridades.
- As quatro membranas existentes são patrimônio útil, mantidas intactas e sem
  diodos individuais. Sua integração é candidata; não bloquear o restante por
  falta de medições nem prometer reconhecimento irrestrito de teclas simultâneas.
- Referências upstream em references/gigatron são imutáveis. Derivações devem
  ficar separadas, com origem, revisão, transformação e SHA256.
- Use simulações limitadas no WSL Ubuntu, binários temporários no Linux e
  evidências pequenas em verification. Diferencie emulação, portas/HDL,
  simulação elétrica e ensaio físico. Não herdar aprovação entre circuitos.
- Registre decisões e limites; mantenha documentos curtos e atuais, sem pilhas
  de checkpoints contraditórios no início de cada arquivo.
- Não alterar a licença do projeto ou acessos. Preserve os avisos upstream.
- O usuário autorizou commits/pushes. Confira remoto, preserve histórico e
  verifique o commit publicado; não use force push.
- Não declarar fabricação liberada sem esquema, BOM/footprints, análise
  elétrica/temporal, ERC/DRC e validação correspondente.
