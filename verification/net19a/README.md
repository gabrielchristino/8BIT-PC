# Evidências NET-19A

Leia `docs/engineering/NET19A.md` antes de interpretar os resultados.

## Aceitação atual, por escopo

- `verified-cpu-ideal.json`: 6.886 instruções/casos de vetor, com controlador AHC174 e monitor de COMMIT amostrado.
- `verified-cpu-timed-quick.json` e `verified-cpu-early-timed-quick.json`: 1.062 casos cada, CQ selecionado máximo/antecipado, demais modelos preservados.
- `verified-safety-ideal.json`: 4.562 cortes de reset/PG digitais.
- `timed-safety-batches.json`: sete intervalos completos, 1.692 cortes e índices 0–25 exatamente; não somar a quantidade fixa de opcodes impressa por cada lote.
- `system-program-ideal.json`: boot/programa completo e PPM igual, controlador AHC174; SRAM desconhecida. Esse programa não usa o monitor de vetores antigo.
- `system-scan-timed.json` e `policy0/system-scan-timed.json`: firmware de varredura na CPU, cinco quadros por configuração, pausa de clock e reset de leitura pendente; configuração binária de reset explícita, sem cobertura exaustiva de aperturas/MTBF.
- `native/schematic-check.json` e `native/equivalence-check.json`: pinos exportados e somente três classes de FF substituídas; mesma lógica/passivos/quantidade.
- `native/ahc174-model-results.json`: dois cenários de atraso e cinco violações temporais propositais.
- `native/erc-summary.json`: **ERC parcial reprovado**, 135 violações/retorno5, sem exceções. Não é lista de erros da placa unida.

## Rejeições esperadas

- `verified-cpu-negative-bank-ideal-quick.json`: alteração de registro sem escrita autorizada amostrada é detectada.
- `verified-cpu-legacy-state-timed-quick.json`: retorno aos três HC174 reproduz setup inválido no caminho de SLOT.
- `system-scan-ideal-negative.json`: bypass de KEY_READY é rejeitado por leitura prematura.

Esses arquivos aprovam a capacidade de **detectar** o defeito; não aprovam a
variante defeituosa. Exigem compilação bem-sucedida, saída não zero e mensagem
específica, não qualquer falha/timeout.

## Intermediários preservados

`cpu-*`, `program-ideal.json`, `scan-ideal.json`, `system-cpu-*` e as primeiras
fixtures `tb_rtl_*`/`system-tb_rtl_cpu-*` são iterações iniciais. Algumas passaram
em escopo ideal, outras rejeitaram setup, monitor de nível ou ordem de seed.
**Não são a aceitação final dos vetores.** Os scripts iniciais continuam para
provenance/reprodução, não para substituir `run_system_vectors.py`.

`development/` identifica fontes/logs/traços dessas falhas, incluindo o caso em
que COMMIT era um na captura e zero na observação da saída. Seus hashes se
referem às versões daquele ensaio; não exigir que uma fonte atual evoluída
coincida com o hash de uma iteração anterior.

`environment.json` é complemento posterior de metadata: ferramentas e ROMs
originais iguais ao commit base. `load-inventory.json` conta folhas candidatas,
não consumo real nem BOM global homologada. Firmware raw scan não implementa
debounce/fila, e os testes não integram os domínios físicos da NET-18.

As fixtures SV nesta pasta preservam os bytes exatos usados na compilação,
inclusive linhas em branco com indentação do emissor. A exceção de formatação
em .gitattributes se restringe a esses snapshots; não altera scripts, modelos,
esquemas, ERC ou critérios de aprovação da simulação.
