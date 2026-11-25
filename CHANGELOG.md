# Histórico preservado

## 24/11/2026 — desenvolvimento 9.8.4.2

- Ferramentas Icarus Verilog 12.0, ngspice 42 e KiCad CLI 7.0.11 preparadas no WSL Ubuntu.
- Modelos novos HC191/157/377, banco de carga de 16 bits e sequenciador de referência, mantendo a CPU e arquivos históricos intactos.
- Duas rodadas de 393.235 verificações de valor aprovadas; modelo HC191 exercitado e sete violações temporais intencionais detectadas.
- Primeiro esquema parcial do banco X, com 20 componentes e 188 pinos; mapa conferido contra a netlist exportada. Controle físico, SP-1, ERC/DRC e produção continuam pendentes.

## 24/11/2026 — migração para GitHub

- Inspeção do remoto vazio e das pastas locais, recuperação dos pacotes 9.3, 9.8.3 e incremento 9.8.4.1.
- Preservação de arquivos originais, leituras de quatro conversas e duas páginas, com capturas adicionais da interface.
- README, AGENTS, arquitetura, decisões, roadmap, provenance, inventário e registro de lacunas.
- Execução local das bancadas existentes em cópias temporárias, preservando a falha por diagnostic.asm ausente.
- Comparação das quatro lanes de ROM regeneradas com os binários originais.

## Sequência histórica recuperada

Nova conferência: acervo salvo em `C:/Users/gabri/projetos/isa1`, arquivos locais adicionais preservados e modelos 7.4/7.5 reexecutados com resultados iguais aos registros existentes. Downloads novos pelo chat compartilhado bloqueados com `ERR_BLOCKED_BY_CLIENT`; completude integral não confirmada. Ver `docs/RECHECK_SHARED_CHATS.md`.

| Revisão | Conteúdo e limite de evidência |
|---|---|
| 7.6 / REV76 | Auditoria estrutural, divergência de convenção de pilha, sete opcodes pendentes naquele estágio; não emulador completo |
| 7.7–7.9 | CPU simbólica executável com X e conjunto de 26 opcodes, indicada no cabeçalho de cpu.py posterior |
| 8.x | Integração de modelos digitais, teclado e regressões; snapshots individuais não recuperados integralmente |
| 9.2–9.3 | Proteção de escrita/reset, cancelamento por epoch e recuperação; ZIP 9.3 preservado |
| 9.4.x | Microcódigo codificado e controle horizontal, incorporados aos arquivos posteriores |
| 9.8.1 | Sequenciador/ROM, incorporados ao pacote posterior |
| 9.8.2 | ALU booleana integrada ao controle; README preservado cumulativamente |
| 9.8.2.1–9.8.3 | Seleção de ALU, flags e aritmética de 16 bits em blocos isolados; ZIP 9.8.3 preservado |
| 9.8.4 | Análise arquitetural/BOM preliminar em conversa; não nova bancada relatada |
| 9.8.4.1 | Contadores candidatos e limites de pilha isolados; ZIP chamado rev984 preservado |

Esta tabela não substitui o histórico original nem atribui data/autoria de commit às revisões. Resultados de engenharia física continuam pendentes.
