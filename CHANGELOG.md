# Histórico preservado

## NET-04 — 25/11/2026

Banco parcial de microcódigo com 34 CIs: esquema/pinos/XML e simulação derivada, integração sem alterar as ROMs recuperadas, retenção da palavra em WAIT e decodificação de SP. Correção nova da fase de direção DEX, fontes anteriores preservadas. Regressões nas duas configurações de X, monitores temporais e casos negativos em verification/net04; relatório docs/engineering/NET04.md. Não constitui liberação para fabricação.


## 25/11/2026 — NET-03, transações derivadas do esquema

- Controle em HC174/HC74/portas, com captura e retenção de endereço/dado/modo/MDR em HC377.
- Esquema parcial com 17 CIs e 17 desacoplamentos propostos; 304 pinos conferidos e HDL gerado do XML KiCad.
- Rearme exige retorno de START/ACK; fontes podem mudar após captura sem alterar a transação ativa.
- Distribuição de clock/clear, orçamento de carga, monitores e testes negativos; regressões com SP da NET-02 e CPU das ROMs.
- Interface CMOS e validações digitais explícitas; sequenciador ROM, condicionamento elétrico e produção permanecem pendentes.

## 25/11/2026 — NET-02, banco SP derivado do esquema

- Esquema parcial SP com 12 CIs e 12 desacoplamentos; 220 pinos conferidos, HDL derivado da netlist KiCad.
- Armazenamento HC273 com bit 15 codificado, soma SP±1 compartilhada e direção distribuída por HC125.
- Bancadas de todas as direções/valores, retenção, reset, atrasos selecionados, falhas intencionais e regressão da CPU integrada.
- Base RTL-01 e snapshots históricos preservados; controle físico e liberação de placa ainda pendentes.

## 24–25/11/2026 — integração de emulação RTL-01

- CPU HDL comandada pelas ROMs binárias originais, memória/MMIO, arbitragem VRAM e raster ideais.
- Adaptador de carga e seleção entre X RTL e banco funcional HC191/157/377, preservando o esquema parcial anterior.
- Diagnóstico novo com boot EEPROM → RAM e imagem VGA; bancadas de instruções, ALU, reset/energia, WAIT e pausas de RUN.
- CALL/RET verificam dois bytes antes do primeiro acesso de pilha; os limites foram exauridos para todos os valores de SP e boot.
- Validação funcional separada de netlist física, temporização integrada e liberação de produção.

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
