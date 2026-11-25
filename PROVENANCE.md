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

NET-12 (25/11/2026), base 3cac9fca256377186960d106d08d7ccd0ca6c6dc: novo hardware/memory_access e sim/net12. XML KiCad gera o controlador com HC/HCT/AHC; PDFs anteriores preservados. Adaptador conserva interface/funções de memória da RTL-01 e troca as FSMs de acesso/arbitragem por pinos; armazenamento, MMIO, raster, concessão e retorno de dados continuam modelos. Fixtures novas distinguem commit físico MMIO da confirmação à CPU. Falha inicial do monitor na preparação da fixture e rodada anterior ao cache de colunas estão preservadas, com fontes anteriores identificadas por hashes em verification/net12/development. Nenhum material novo é apresentado como original recuperado. Manifesto audita os doze snapshots anteriores nos respectivos commits.


NET-11 (25/11/2026), base 52bb48901fda92848add95f01097b704472d397e: novo hardware/memory_decode e sim/net11; nenhum arquivo anterior foi sobrescrito. XML KiCad gera o decodificador. O adaptador copia a memória comportamental da RTL-01 e substitui somente a captura de região/endereço; demais periféricos continuam modelos. Runner derivado da NET-10 e hashes em adapter-origin.json. Onze PDFs oficiais novos são preservados sem transformação, com URLs/hashes/status de candidato em references/system-candidates-2026-11-25.json. Manifesto audita os onze snapshots anteriores nos respectivos commits.


NET-10 (25/11/2026), base 5020e30394303971c4c0c1852a81d635365b4fee: nova CPU global em hardware/cpu_global, sem alterar os oito bancos de origem. Adicionados 17 buffers HC125; XML exportado e verificado pino a pino. Modelos ideal/com atrasos e falhas intermediárias preservados por suas fontes. KiCad 10.0.8 instalado separadamente, com origem/hash em docs/engineering/KICAD_ENVIRONMENT.md; ERC ainda apresenta 56 violações, sem exceções adicionadas. Manifesto audita os dez snapshots anteriores nos respectivos commits.


NET-09 (25/11/2026), base 4f2584e7e3d07b0872ecb62eae694eae13a7fd4c: hardware/x_register_bank e sim/net09 são novos; hardware/cpu_execution_glue é variante nativa separada de NET-08. X procedural é substituído por pinos; ligações EXEC_ACCEPT/WRITE_MODE são exportadas/checadas em XML. A rodada anterior à explicitação dessas ligações é preservada como baseline-before-pin-glue.json, identificada por suas próprias fontes/hashes. A rodada final foi repetida. Manifesto audita nove snapshots anteriores e preserva datasheets existentes. Instalação separada de KiCad 10 para trabalhos posteriores não altera registros das exportações desta etapa feitas no KiCad 7.


NET-08 (25/11/2026), base 50a923cd3d60bb4943030934140d8336be4ddf42: hardware/execution_bank e sim/net08 são novos. Guardas/estados/fault da NET-07 viram HC174/portas a partir de XML KiCad. Fixtures temporárias semeiam STACK_CHECKED físico. Relatórios final/isolado têm fontes/hashes; logs de integração e rastreamento anteriores preservam o erro de polaridade corrigido, não alegam aprovação atual. Datasheets reutilizados, fontes anteriores intactas. Manifesto audita oito snapshots anteriores nos respectivos commits.


NET-07 (25/11/2026), base d876dc6499c49b937c2dfd318abe605eea0497e3: hardware/address_bank e sim/net07 são trabalho novo. Pinagens TI já preservadas -> KiCad -> XML -> pacotes/portas; adaptador substitui PC e seleção de endereços da NET-06. Fixtures temporárias semeiam Q de PC; fontes anteriores não mudam. verification/net07 registra ferramentas/saídas/fontes/hashes e audita sete snapshots anteriores. Duas imagens e FAQ recebidas do usuário hoje estão documentadas em KEYPAD_CONNECTOR.md; imagens originais em references/user/2026-11-25, com manifesto próprio e sem inferência de licença ou medição física.


NET-06 (25/11/2026), base 18a3cdc2ab83cb8af51177b8116b0320a4a4f5b8, acrescenta hardware/register_bank, sim/net06 e ferramentas novas derivadas da infraestrutura anterior. Pinagens TI existentes -> esquema KiCad -> XML -> banco de pacotes conectados. A CPU NET-05 é transformada substituindo A/B/EA/Z/C e seleção de dados; fixtures temporárias semeiam Q dos pacotes correspondentes, sem modificar as bancadas originais. verification/net06 registra fonte/hashes/transformação, versão/comandos/saídas, testes normais e negativos e audita seis snapshots anteriores. initial-reset-fixture-failure.json preserva uma falha intermediária de preparo; seus hashes identificam aquele ensaio, não as fontes finais. Datasheets são reutilizados byte a byte. Nenhum arquivo novo é apresentado como revisão histórica recuperada.


NET-05 (25/11/2026), base 179b06ed6aa80ab1658022657638ef571888d6a7, cria hardware/alu_bank e sim/net05. Ferramentas novas derivam da infraestrutura anterior, sem alterá-la: pinagens já documentadas TI -> KiCad -> XML -> ALU de portas/somadores; a CPU NET-04 é adaptada substituindo apenas a ALU combinacional. Os PDFs TI existentes são reutilizados com hashes/origens explícitos. verification/net05 registra fontes, transformação, comandos/versões/saídas, limites selecionados de caminhos, testes negativos e manifesto; audita cinco snapshots anteriores nos respectivos commits. Não são materiais históricos recuperados. A primeira rodada foi interrompida para ajustar a folha gráfica; a aceitação foi reiniciada com os arquivos finais.


NET-04 (25/11/2026), base Git b5e46593fab55b8679254f9004e5711cd1ffa2c5, acrescenta hardware/microcode_bank, sim/net04 e ferramentas novas. Esquema de pacotes -> XML KiCad -> netlist de portas/FF/ROM; CPU e candidato X derivam das bases anteriores por transformações identificadas com SHA-256. Não altera imagens de microcódigo nem fontes anteriores. Novos datasheets oficiais TI/Microchip são preservados; AT28C64B é evidência de alternativa rejeitada, AT28HC64B-120 é candidata não homologada para compra. Manifesto, logs, versões, transformações e auditoria dos quatro snapshots anteriores nos próprios commits ficam em verification/net04. A falha inicial DEX e sua correção estão registradas no relatório NET04. Arquivos novos não são recuperação de revisões históricas.


NET-03 (25/11/2026), a partir de `60c097c`, acrescenta `hardware/transaction_bank`, `sim/net03` e ferramentas novas, sem editar as fontes da RTL-01/NET-02. Pinagem de HC174/74/08/32 foi conferida em datasheets TI arquivados; HC377/04/125 reutilizam documentos já preservados. O modelo de transação é gerado dos nós de pinos do XML exportado pelo KiCad. O adaptador CPU substitui somente a interface de transação/payload/MDR; o SP continua da NET-02. Transformações de fixtures são descritas no relatório, incluindo observar o início interno no teste de guardas porque REQUEST passa a ter latência. O manifesto e os logs em `verification/net03/` separam regressões funcionais, cenário de atrasos selecionados e falhas intencionais. Manifestos anteriores são conferidos nos respectivos commits originais, preservando seus hashes e a evolução legítima dos documentos gerais.

NET-02 (25/11/2026) acrescenta `hardware/stack_bank`, `sim/net02`, ferramentas de construção/adaptação/teste e seu relatório. Símbolos de pacote novos foram desenhados com pinagem transcrita de datasheets TI; o HDL de SP é transformado do XML exportado pelo KiCad. O adaptador CPU deriva da RTL-01 sem alterar sua base. Novos PDFs TI têm URLs e hashes em `verification/net02/manifest.json`. Os manifestos anteriores abrangem também documentos de visão geral que evoluem: sua integridade é verificada contra o snapshot Git `6bbac52`, registrado em `verification/net02/baseline-integrity.json`; não se reescrevem hashes antigos para encobrir mudanças posteriores. Novas saídas e transformações têm manifesto próprio. Nenhuma licença ou autorização de acesso foi alterada.

RTL-01 é desenvolvimento novo, separado em `sim/rtl`, `sim/tests` e `firmware`. `tools/run_rtl.py` transforma as quatro ROMs originais em uma imagem temporária para Icarus e usa o emulador arquitetural recuperado como referência. O boot/diagnóstico novo e as imagens resultantes não são arquivos históricos recuperados. `verification/rtl01/` registra fontes, resultados e hashes desta integração; ver docs/engineering/RTL01.md. A execução inicial anterior à integração de X está identificada como `baseline-rtl-results.json`, um registro intermediário com hashes das fontes daquele ensaio, posteriormente substituídas; não é uma revisão histórica recuperada.

O desenvolvimento novo 9.8.4.2 está separado dos snapshots históricos: `sim/hdl/`, `hardware/counter_load_candidate/`, `tools/` e `docs/engineering/`. Datasheets TI foram obtidos das URLs oficiais, com documentos e avisos preservados em `references/`. A biblioteca gráfica KiCad é identificada por versão/hash e seus créditos foram preservados. `verification/rev9842/manifest.json` registra a origem e os hashes dos artefatos desta iteração; logs de execução e escopo das validações constam do relatório de engenharia.

Na nova conferência, o acervo foi copiado para `C:/Users/gabri/projetos/isa1` sem sobrescrever os materiais já existentes. Arquivos locais adicionais, duplicatas e placeholders vazios têm inventário separado em `archive/local-additions-manifest.json`; ver `docs/RECHECK_SHARED_CHATS.md`. A pasta estava vazia na inspeção inicial descrita abaixo, mas recebeu arquivos posteriormente. A origem imediata dos acréscimos é a pasta local, sem presumir mecanismo ou autoria do download.

- `archive/pages/*.md` é o Markdown retornado pela API, não uma reconstrução de um arquivo `.md` anterior.
- `archive/browser-captures/` registra conteúdo exibido na interface, com identificação da conversa e do tipo de captura. Extrações de código removem apenas a coluna visual de números de linha; não possuem garantia dos bytes originais.
- Fragmentos virtualizados são mantidos como capturas/fragmentos e não promovidos a fontes completas.
- README, AGENTS, ARCHITECTURE, DECISIONS, ROADMAP, CHANGELOG e documentos de migração foram escritos nesta migração a partir das fontes identificadas.
- `scripts/` é ferramenta nova de verificação e inventário; `verification/results.json` contém execução local nova. Resultados dentro de `revisions/` são os registros originais, sem sobrescrita.
- A pasta de trabalho e `C:/Users/gabri/projetos/isa1` estavam vazias; não foi encontrado histórico Git local. Busca por nomes do projeto em Downloads/Documentos não encontrou um acervo anterior relevante. A inspeção não equivale a uma busca de todos os discos ou backups.

O remoto estava público e vazio: Contents respondeu «This repository is empty», e a listagem de commits respondeu «Git Repository is empty». Nenhum arquivo ou commit anterior precisou ser substituído. Os commits de migração registram o momento da publicação, sem simular datas ou autores de revisões antigas.
