# ISA-1 — computador de 8 bits

Projeto de computador pessoal com CPU própria de lógica discreta, endereçamento de 16 bits, vídeo VGA e teclado de membrana. Este repositório reúne os materiais originais recuperados e a documentação de continuidade.

**Estado: protótipo lógico em desenvolvimento; hardware não liberado para fabricação.** A migração de 24/11/2026 recuperou três pacotes originais: revisão 9.3, revisão 9.8.3 e incremento 9.8.4.1. O histórico anterior permanece parcialmente recuperado. Ausências estão registradas em [LACUNAS.md](docs/LACUNAS.md).

## Começar

**Desenvolvimento atual:** [NET-06 — A/B/EA, flags e seleção de dados](docs/engineering/NET06.md). Registradores e mux de dados derivam da netlist KiCad e integram-se aos blocos anteriores. Execute `python3 tools/run_register_netlist.py` e `python3 tools/run_register_timing_checks.py` no WSL Ubuntu. PC, caminho de endereços e controle físico restante continuam pendentes, além da validação elétrica/temporal/física.

**ALU de 8 bits:** [NET-05](docs/engineering/NET05.md), com soma/subtração, lógica e deslocamentos da netlist.

**Microcódigo:** [NET-04](docs/engineering/NET04.md), com microstep, FETCH, IR, EEPROMs, retenção e decodificação da palavra de controle.

**Controle de transações:** [NET-03](docs/engineering/NET03.md), reutilizado pela NET-04.

**Banco SP:** [NET-02 — SP a partir do esquema](docs/engineering/NET02.md). O armazenamento de SP e o somador SP±1 são simulados da netlist exportada pelo KiCad e ligados à CPU das ROMs. Esquema nativo em `hardware/stack_bank/`; regressões em `verification/net02/`. Controle físico, restante da CPU e liberação para produção continuam pendentes.

**Base da CPU:** [RTL-01 — CPU executando as ROMs recuperadas](docs/engineering/RTL01.md), com boot, memória, VRAM, teclado simulado e comparação entre X ideal e modelos HC191/157/377. Execute `python3 tools/run_rtl.py` no Ubuntu WSL. Resultados e quadro de vídeo em `verification/rtl01/`. Ainda não é um circuito físico completo.

**Banco X candidato:** [revisão 9.8.4.2](docs/engineering/REV9842.md), com modelos HDL de componentes, bancadas e primeiro esquemático parcial do banco X. As ferramentas de simulação rodam no WSL Ubuntu. Ver os [critérios de produção](docs/engineering/PRODUCTION_GATES.md) antes de interpretar uma aprovação como liberação de hardware.

O diretório de continuidade é `C:/Users/gabri/projetos/isa1`. A nova conferência preservou arquivos locais 7.4/7.5 e a auditoria 7.6, mas os downloads pelo chat compartilhado foram bloqueados pelo Chrome. Ver [relatório da conferência](docs/RECHECK_SHARED_CHATS.md).

- [Arquitetura e conjunto de instruções](ARCHITECTURE.md)
- [Decisões e alternativas](DECISIONS.md)
- [Próximas etapas](ROADMAP.md)
- [Origem dos materiais](PROVENANCE.md)
- [Inventário](docs/INVENTORY.md)
- [Validação local](verification/README.md)
- [Histórico das revisões](CHANGELOG.md)
- [Engenharia original do teclado](archive/pages/page_d3278588f6388191a2041bb3c9f6ee1f.md)

## Material executável

`revisions/rev983/` é o pacote completo mais recente recuperado: CPU, sistema, ALU, montador, desmontador, microcódigo, sequenciador, modelos de vídeo/teclado, testes e quatro ROMs de controle. `revisions/rev984/` é um estudo incremental isolado de contadores e limites da pilha, não uma substituição completa da revisão anterior. `revisions/rev93/` preserva uma versão anterior do modelo integrado.

Com Python 3.12 ou compatível, execute a partir da raiz:

```text
python scripts/verify_recovered.py
python scripts/verify_archive.py
```

O primeiro comando executa as bancadas existentes em cópias temporárias, registra saídas e falhas em `verification/results.json` e regenera as ROMs para comparação. A falha conhecida de `test_assembler.py` decorre da ausência original de `diagnostic.asm`; ela não é ocultada. Nenhum teste físico é realizado por esses comandos.

## Especificações recuperadas

| Bloco | Estado documentado |
|---|---|
| CPU | Dados de 8 bits; endereços de 16 bits; 26 opcodes no modelo recuperado |
| Registradores | A/B, X, PC, SP; flags Z/C; temporários no controle |
| Memórias físicas | RAM 32 KiB, VRAM 32 KiB, EEPROM removível 32 KiB com ZIF |
| Vídeo | VGA com pixels lógicos 160 × 120, RGB332 de 256 cores |
| Teclado | Quatro membranas 4 × 4; modelo compartilhado 4 × 16; tratamento conservador de ambiguidades |
| Construção pretendida | PCB principal única, SMD preferencialmente SOIC, lógica 74HC/74HCT |
| Alimentação pretendida | USB-C 5 V |

Os resultados lógicos não comprovam temporização, níveis elétricos, pinagem, consumo ou funcionamento de uma placa física. A página de teclado baseada na REV76 e os pacotes 9.x representam estágios distintos: pendências da REV76 não devem ser atribuídas automaticamente ao modelo posterior, nem o sucesso posterior pode ser aplicado retroativamente à REV76.

Os ZIPs originais estão em `archive/packages/`; as extrações preservam seus bytes. Textos recuperados da interface têm identificação própria, pois não equivalem a downloads dos arquivos originais. Não foi escolhida uma licença nova durante a migração.
