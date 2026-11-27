# 8BIT-PC — recomeço a partir do Gigatron

Computador de lógica discreta, pequeno o suficiente para montar e compreender.
A direção escolhida em 27/11/2026 é partir do Gigatron e avaliar melhorias com
poucos CIs adicionais. A implementação anterior de 460 CIs foi encerrada como
base de desenvolvimento; permanece preservada no histórico.

## O que existe agora

- BOM oficial do Gigatron: [arquivo original](references/gigatron/bom-original.xlsx).
- Emulador C e ROMv6 oficiais, fixados em uma revisão identificada.
- [Escopo e critérios](docs/ESCOPO.md), [decisões](DECISIONS.md) e [próximos passos](ROADMAP.md).
- [Origem dos arquivos](PROVENANCE.md) e [como recuperar o projeto anterior](docs/HISTORICO.md).

Não há circuito novo, PCB ou liberação de compra/fabricação nesta base.
Os arquivos oficiais de referência não são uma BOM já homologada para uma variante nossa.

## Regra central

Primeiro reproduzir e entender a base. Depois melhorar uma coisa por vez,
mostrando componentes acrescentados/retirados, impacto no software e teste.
Quantidade de CIs é requisito de projeto, não uma contagem feita no final.

Não se herdaram automaticamente ISA, microcódigo, circuitos e aprovações NET
do projeto anterior. Um recurso antigo só volta à base após avaliação explícita
do custo e da necessidade. As melhorias lembradas pelo usuário ainda não foram
identificadas; não preencher essa lacuna por suposição.

## Verificar os materiais de referência

No Ubuntu WSL, a partir deste diretório:

```sh
python3 scripts/check_baseline.py
```

O comando confere hashes e a estrutura do XLSX, compila uma cópia temporária
do emulador e executa um trecho limitado da ROM. Não é simulação dos CIs,
validação elétrica nem prova de compatibilidade de uma arquitetura modificada.

Repositório: https://github.com/gabrielchristino/8BIT-PC
