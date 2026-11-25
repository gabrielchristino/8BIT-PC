# Ambiente KiCad de continuidade

25/11/2026. O Ubuntu WSL mantém o KiCad 7.0.11 instalado pelo repositório Ubuntu para reprodução dos snapshots anteriores. Para ERC da NET-10, foi instalado KiCad **10.0.8**, separado, no diretório do usuário; não houve atualização global do sistema.

Origem: [página oficial para Linux](https://www.kicad.org/download/linux/) e seu espelho de distribuição [UNICAMP](https://mirrors.ic.unicamp.br/kicad/appimage/stable/kicad-10.0.8-x86_64-lite.AppImage.tar). Arquivo original de 316.538.880 bytes, SHA-256 `abb59cee9f9782736c1b9a92e3ab08b31320ee01d72a6f9442a07fdef71b87d0`.

O TAR foi validado como contendo um único AppImage, extraído com filtro de dados do Python e expandido com `--appimage-extract`. A distribuição fica em `/home/gabri/.local/opt/isa1-kicad-10.0.8`; `squashfs-root` aponta para `AppDir`. Não se inclui esse binário de aproximadamente 302 MiB no Git. Os arquivos do projeto permanecem em `C:/Users/gabri/projetos/isa1`.

Executável efetivo:

```text
/home/gabri/.local/opt/isa1-kicad-10.0.8/squashfs-root/usr/bin/kicad-cli
```

`version` retorna 10.0.8. Exportação usa `sch export netlist --format kicadxml`; a verificação usa `sch erc --format json --severity-all --exit-code-violations`. Os comandos completos, saídas e versões ficam nos relatórios da etapa. ERC com violações retorna 5 e não equivale a um resultado aprovado. Poppler 24.02 renderiza os PDFs exportados para inspeção visual.
