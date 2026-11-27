# Origem dos materiais

Recomeço autorizado em 27/11/2026. O histórico anterior continua no mesmo
repositório Git; a limpeza não reescreve commits nem cria uma licença nova.
Identidade da preservação: docs/HISTORICO.md e verification/restart.json.

## Referência Gigatron

- Autores: Marcel van Kervinck e Walter Belgers.
- Projeto oficial: https://gigatronttl.eu/
- FAQ/decisões de arquitetura: https://gigatronttl.eu/posts/160.html
- Manual e esquema: https://gigatronttl.eu/media/Gigatron-manual.pdf
- BOM oficial: https://gigatronttl.eu/bom
- Software: https://github.com/kervinck/gigatron-rom
- Revisão capturada: `ec6495f374042b7f938da518502009d7052738d9`.

references/gigatron contém apenas BOM original, emulador C, ROMv6 e licença
do software. Bytes, URLs, revisão e SHA256 constam de sources.json. Os arquivos
não foram alterados. A BOM não tem revisão Git inferida: veio do site oficial,
identificada pela data de captura e hash. Não inferir a licença da BOM a partir
da licença do software; LICENSE-software é preservada com esse escopo.

O teste usa uma cópia temporária do emulador, fixando a semente rand em 1 e
limitando a execução a 100 milhões de ciclos e 1.024 mensagens de HSYNC.
A impressão de caracteres de pixels é omitida, preservando o contador do
observador. A transformação exata está em
scripts/check_baseline.py e no relatório. Não é teste de uma nova CPU física.

Nenhuma evidência NET anterior aprova um circuito novo baseado no Gigatron.
A ausência do diagnostic.asm histórico e demais lacunas antigas permanecem
no arquivo histórico, sem serem transformadas em aprovações.
