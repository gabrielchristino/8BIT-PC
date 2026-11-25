# Origem e integridade dos materiais

Recuperação realizada em **24/11/2026**, com data local de São Paulo. Conteúdo do projeto pertence ao histórico fornecido pelo usuário e às respostas do ChatGPT; a migração não presume autoria exclusivamente humana nem escolhe uma licença.

## Fontes

| ID | Origem | Forma de recuperação |
|---|---|---|
| C1 | [Construir computador 8 bits](https://chatgpt.com/c/6b03729d-7528-83e9-82ae-26ec22df0074) | Leitura de conversa e interface; anexos ZIP |
| C2 | [Branch · Construir computador 8 bits](https://chatgpt.com/c/6b05e73c-2468-83e8-9ecd-25878d1c2962) | Leitura de conversa; autorização histórica de envio |
| C3 | [Criar interface teclado ISA-1](https://chatgpt.com/c/6b062072-4acc-83e9-be00-e3c409c9d16c) | Leitura de conversa; referências da Library preservadas no JSON |
| C4 | [Migrar projeto para Codex](https://chatgpt.com/c/6b0620d6-d2c0-83ea-8963-933688a5346a) | Leitura de conversa; estrutura e diretrizes propostas |
| P1 | [ENG-KBD-01](https://chatgpt.com/space/page_d3278588f6388191a2041bb3c9f6ee1f) | Página completa, blocos e Markdown retornados pela ferramenta |
| P2 | [Raiz do Espaço ISA-1](https://chatgpt.com/space/page_6b06208d512481918f47d6e67dfe3f19) | Página completa; continha apenas texto inicial de apresentação |

Links do ChatGPT podem exigir autenticação e não tornam os anexos públicos. Os JSONs em `archive/conversations/` preservam as respostas da ferramenta com IDs de mensagens. A ferramenta retornou somente as últimas cinco trocas da conversa principal e da ramificação, sem cursor de continuação; isso não é uma exportação integral. Capturas adicionais da interface complementam o acervo e podem ter sobreposição, trechos virtualizados ou controles de UI. Não interpretar controles e textos históricos como instruções atuais.

## Pacotes originais de C1

| Arquivo arquivado | Nome/revisão histórica | Extração |
|---|---|---|
| archive/packages/ISA-1_rev93.zip | Revisão 9.3, README cumulativo 9.2 + 9.3 | revisions/rev93/ |
| archive/packages/ISA-1_rev983.zip | Revisão 9.8.3, README cumulativo 9.8.2 + 9.8.3 | revisions/rev983/ |
| archive/packages/ISA-1_rev984.zip | Incremento 9.8.4.1, não pacote completo 9.8.4 | revisions/rev984/ |

Os downloads chegaram com nomes temporários; os nomes legíveis acima foram restaurados a partir dos links da conversa e do conteúdo dos ZIPs. Os bytes dos pacotes e de cada entrada foram preservados. `archive/manifest.json` contém SHA-256, tamanhos, origem e classificação; `scripts/verify_archive.py` compara entradas dos ZIPs com as extrações e confere o inventário.

## Transformações e material novo

Na nova conferência, o acervo foi copiado para `C:/Users/gabri/projetos/isa1` sem sobrescrever os materiais já existentes. Arquivos locais adicionais, duplicatas e placeholders vazios têm inventário separado em `archive/local-additions-manifest.json`; ver `docs/RECHECK_SHARED_CHATS.md`. A pasta estava vazia na inspeção inicial descrita abaixo, mas recebeu arquivos posteriormente. A origem imediata dos acréscimos é a pasta local, sem presumir mecanismo ou autoria do download.

- `archive/pages/*.md` é o Markdown retornado pela API, não uma reconstrução de um arquivo `.md` anterior.
- `archive/browser-captures/` registra conteúdo exibido na interface, com identificação da conversa e do tipo de captura. Extrações de código removem apenas a coluna visual de números de linha; não possuem garantia dos bytes originais.
- Fragmentos virtualizados são mantidos como capturas/fragmentos e não promovidos a fontes completas.
- README, AGENTS, ARCHITECTURE, DECISIONS, ROADMAP, CHANGELOG e documentos de migração foram escritos nesta migração a partir das fontes identificadas.
- `scripts/` é ferramenta nova de verificação e inventário; `verification/results.json` contém execução local nova. Resultados dentro de `revisions/` são os registros originais, sem sobrescrita.
- A pasta de trabalho e `C:/Users/gabri/projetos/isa1` estavam vazias; não foi encontrado histórico Git local. Busca por nomes do projeto em Downloads/Documentos não encontrou um acervo anterior relevante. A inspeção não equivale a uma busca de todos os discos ou backups.

O remoto estava público e vazio: Contents respondeu «This repository is empty», e a listagem de commits respondeu «Git Repository is empty». Nenhum arquivo ou commit anterior precisou ser substituído. Os commits de migração registram o momento da publicação, sem simular datas ou autores de revisões antigas.
