# Ferramentas locais via Ubuntu WSL

Ambiente preparado nesta iteração: Ubuntu 24.04, Python 3.12.3, Icarus Verilog 12.0, ngspice 42 e KiCad CLI 7.0.11. As versões efetivas ficam em `verification/environment.json`.

Dependências instaladas pelos repositórios da distribuição: `iverilog`, `ngspice`, `kicad` e `kicad-symbols`, sem pacotes recomendados desnecessários. Não é necessário reinstalá-las a cada execução.

Executar da raiz do projeto no terminal Ubuntu:

```text
python3 tools/check_environment.py
python3 tools/run_rev9842.py
python3 tools/build_counter_schematic.py
python3 scripts/verify_archive.py
python3 tools/record_engineering_manifest.py --check
```

No PowerShell, prefira comandos sem interpolação de variáveis de shell:

```text
wsl -d Ubuntu -- python3 /mnt/c/Users/gabri/projetos/isa1/tools/run_rev9842.py
```

Após alterar fontes e verificar resultados, gerar novamente o manifesto com `python3 tools/record_engineering_manifest.py`. As compilações HDL usam pastas temporárias Linux; resultados persistentes são salvos em `verification/`. O script de esquema exige as bibliotecas oficiais instaladas em `/usr/share/kicad/symbols` e usa símbolos embutidos no arquivo gerado.

Ngspice foi instalado e sua versão consultada, mas ainda não há simulação elétrica aprovada do circuito. KiCad CLI 7 exporta netlists e desenhos; ERC/DRC continuam pendentes.
