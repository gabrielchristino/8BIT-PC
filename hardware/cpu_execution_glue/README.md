# Controle com ligações explícitas NET-09

Variante separada da NET-08, sem alterar aquela base. Expõe o nó físico EXEC_ACCEPT e usa o inversor livre U48, pinos 5/6, para WRITE_MODE a partir de MEM_N_2. Mesmo número de CIs. Gerar com `tools/build_cpu_execution_glue.py`; evidências em verification/net09/execution-glue-check.json e [NET09.md](../../docs/engineering/NET09.md).
