# Relatório da recuperação e publicação

Data: 24/11/2026, São Paulo. Destino autorizado: gabrielchristino/8BIT-PC.

## Inspeção

- Pasta de trabalho e pasta local `projetos/isa1` vazias; sem histórico Git anterior encontrado nessas pastas.
- Repositório remoto público e vazio, confirmado por Contents e listagem de commits e, posteriormente, por `git ls-remote`.
- Quatro conversas relacionadas e duas páginas acessíveis consultadas. A página de engenharia do teclado foi recuperada integralmente.
- Três ZIPs originais recuperados e preservados, com 55 entradas extraídas sem alteração de bytes.
- Texto adicional de interface preservado separadamente; o JSON REV76 exibido estava incompleto e foi mantido como fragmento.

## Verificações locais

`verification/integrity.json` registra a conferência de hashes e de todas as entradas dos ZIPs. `verification/results.json` registra as bancadas: 22 de 23 passaram; a falha conhecida exige `diagnostic.asm`, ausente do pacote. As quatro lanes de ROM foram geradas novamente com `sequencer.py` em uma cópia temporária, sem reaproveitar os binários presentes na cópia, e coincidiram com os originais.

Não houve modificação corretiva em código histórico. Não houve validação física, SPICE, HDL ou ERC/DRC de placa nesta migração.

## Acesso e histórico Git

A tentativa de criar README pelo conector GitHub retornou 403 «Resource not accessible by integration», sem criar commit. O Git local foi usado como alternativa de publicação com a identidade já configurada no computador. Não foram alteradas permissões do repositório ou criadas credenciais.

O histórico de migração começa agora; não se fabricaram commits para revisões antigas. A regra `.gitattributes` preserva bytes de `archive/` e `revisions/`. A verificação final compara a referência remota ao commit local e confere objetos Git e arquivos publicados.

## Completude

Esta publicação reúne o material efetivamente recuperado. A migração integral continua dependente das lacunas em [LACUNAS.md](LACUNAS.md), principalmente exportação completa da conversa, revisões individuais, imagens e arquivos ausentes. Uma exportação de dados da conta permite separar as conversas do ISA-1 sem incluir os demais chats no repositório.
