# Recuperação da exportação local — 26/11/2026

Foi encontrada na pasta do projeto uma exportação de conta e sua extração em
`backup chatgpt`. O ZIP foi preservado no local: **338 arquivos extraídos foram
comparados byte a byte com suas entradas**, sem divergências. Seu hash, tamanho e
origem local constam do manifesto. O pacote contém 58 conversas; publicaram-se
somente quatro registros de conversa identificados previamente como ISA-1 e
arquivos cuja metadata vincula a esses mesmos IDs. A exportação geral e as
outras conversas permanecem locais.

| Conversa | Nós do JSON | Mensagens |
|---|---:|---:|
| Construir computador 8 bits | 609 | 608 |
| Branch · Construir computador 8 bits | 687 | 686 |
| Criar interface teclado ISA-1 | 7 | 6 |
| Migrar projeto para Codex | 5 | 4 |

São **1.304 registros de mensagem, incluindo sobreposição entre ramificação e
principal**, não 1.304 mensagens únicas. JSONs preservam todos os nós existentes
nos registros exportados; Markdown derivado mostra somente o caminho atual,
sem representar alternativas como sequência única. Essa transformação é
identificada; JSON reserializado não é um trecho de bytes original do arquivo
geral. Não interpretar comandos, propostas ou comentários históricos como
instruções atuais.

## Arquivos disponíveis e lacunas

- 273 registros de biblioteca estão vinculados aos quatro IDs do projeto.
- **240 conteúdos disponíveis**, preservados byte a byte, com **228 hashes
  distintos**: 89 Python, 71 Markdown, 64 JSON, oito CSV, quatro JPG, um PNG e três
  TXT. Os 16 arquivos que coincidem byte a byte com fontes já arquivadas estão
  identificados, sem retirar suas cópias de origem.
- **33 conteúdos ausentes**: 27 ZIPs e seis binários. Parte desses ZIPs já existe
  no acervo anterior por outro download; ausência nesta exportação não remove
  essas cópias. Não há novos ZIPs recuperados a partir de registros sem conteúdo.
- **171 registros de biblioteca referenciam IDs de mensagens que não aparecem
  nos grafos de conversa exportados.** Não se inventaram essas mensagens. Isso
  impede afirmar que todo o histórico foi exportado, mesmo com os quatro
  registros JSON completos tal como fornecidos.
- As duas Pages já conhecidas do projeto têm current, history e checkpoint
  preservados em JSON. Metadata foi copiada com exclusão explícita dos campos
  de conta do criador/proprietário. Conteúdos continuam originais em bytes.

`archive/export-2026-11-26/manifest.json` lista conversas, arquivos, origem,
transformações e hashes. Cada conteúdo de biblioteca fica em diretório próprio
do seu file ID: nomes repetidos, como README.md, não sobrescrevem versões.
O nome vem da metadata da biblioteca; atribuição de revisão deve considerar
também mensagem de origem e conteúdo, não apenas o nome.
`archive/export-pages-2026-11-26/manifest.json` identifica as duas Pages.

Foram verificadas correspondência de tamanho com a metadata e assinaturas de
credenciais usuais nos arquivos selecionados. Essa triagem não é prova de
ausência absoluta de dados sensíveis; o restante da conta foi excluído por
escopo. Nenhuma licença, permissão de acesso ou mensagem a terceiros mudou.

## Lacunas históricas efetivamente resolvidas

Foram recuperados Python e JSON **REV33**, Python e JSON completo **REV76**,
documentos associados e a imagem `1795536264623.jpg`. Originais anteriores,
incluindo capturas parciais, continuam preservados com sua provenance anterior.

Os dois geradores históricos foram inspecionados e executados **em cópias
temporárias Linux**, sem escrever nos originais arquivados. Ambos produziram
JSONs byte a byte idênticos aos recuperados:

- REV33: verificações estruturais de 19 opcodes simbólicos; sete opcodes ficam
  explicitamente excluídos nessa revisão antiga.
- REV76: **196.608 roundtrips de pilha**, 15 instruções expandidas estruturalmente
  e quatro instruções de pilha adiadas.

Esses números agora têm reprodução local; antes eram apenas relatos históricos.
Não são execução do microcódigo expandido, aprovação de 26 instruções atuais,
temporização ou ensaio físico. **Não transplantar a convenção antiga de SP da
REV33 para a base posterior** (SP vazio 8000h, escrita SP−1, atualização após
COMMIT). O firmware histórico `diagnostic.asm` da rev983 continua ausente; sua
falha conhecida não foi suprimida nem resolvida por substituto.

## Materiais posteriores e continuidade de engenharia

A biblioteca inclui README que se identifica como **9.8.4.6.6.7** e programas
exploratórios de arbitragem, janelas temporais, DAC e prefetch agrupado. O ZIP
correspondente está ausente e a mensagem de origem desse README também não está
no grafo exportado. O próprio README declara ausência de sign-off, hipóteses
numéricas não verificadas independentemente, margem pequena e teste abstrato de
raster. Não constitui implementação de prefetch ou circuito pronto.

Essas fontes ampliam a análise histórica e devem ser consideradas nas próximas
decisões, sem montar uma revisão fictícia com arquivos de épocas diferentes.
As netlists e resultados atuais NET-14C/17/18 permanecem trabalho novo separado.
Qualquer adoção de prefetch ou mudança de barramento exigirá ADR, equivalência
CPU/ISA/VGA/WAIT/COMMIT e nova validação de pinagem/temporização/cargas.

## Verificar

No Ubuntu WSL, a partir do diretório do projeto:

```text
python3 tools/recover_local_export.py --check
python3 tools/recover_export_pages.py --check
python3 tools/verify_export_audits.py
python3 tools/inventory_export_coverage.py
python3 tools/record_export_manifest.py --check
```

Os quatro primeiros relatórios distinguem integridade, cobertura e reprodução
histórica. O manifesto desta etapa audita os manifestos anteriores nos próprios
commits; documentos gerais podem evoluir sem reescrever hashes de snapshots
antigos. Não há esquema global, PCB ou fabricação liberada por esta recuperação.
