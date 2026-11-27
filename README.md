NET-26 (26/11/2026): reset local emP1, controlador com uma etapa de buffer e AHC174 real no teclado. Passaram156 cenários estritos,128 combinações selecionadas,48 cortes SRAM, oito cortes CPU,6.886 vetores ideais/dois temporizados de1.062 e boot/quadro completo ideal. Candidato460CIs+2osciladores; energia/temporização global/PCB/protótipo continuam abertos. [Circuito, resultados e limites](docs/engineering/NET26.md). Placa não liberada.

Investigação NET-25 (26/11/2026): drenagem síncrona passou32 cortes selecionados e6.886 vetores ideais, mas a variante NÃO foi promovida: partida binária arbitrária ainda rejeita pulso7,722ns/20ns sob CLR0; um reset breve50ns rejeita recovery em U36_1. Uma hipótese somenteHDL com dupla local emP1 passou156 cenários funcionais, conservando clock frio como restrição aberta. Ver [evidências e próximos ensaios](docs/engineering/NET25.md). Placa não liberada.

Atualização NET-24 (26/11/2026): dois pinos agrupam o sincronizador de pedidos no mesmo clock, mantendo31CIs. 32 cenários selecionados, 6.886 casos ideais, dois temporizados de1.062, oito cortes da CPU e boot/quadro passaram. Permanece uma rejeição reproduzida: quatro resets com perfil assimétrico geram pulso7,722ns contra20ns no modelo HC74; não são aprovações. Ver [resultados e lacuna aberta](docs/engineering/NET24.md). Próximo: encerrar a sequência de fases com pulsos completos; placa não liberada.

Atualização NET-23 (26/11/2026): dois osciladores ACH candidatos no esquema e recepção da CPU por duas Schmitt livres, sem CI adicional de lógica. Partida/falta de clock, pinos SRAM, oito cortes de escrita da CPU e6.886 casos ideais/dois cenários temporizados de1.062 passaram. Carga15pF exige trilhas até5pF e código completo/BOM, jitter/POR e temporização global continuam abertos. Ver [circuito e escopos](docs/engineering/NET23.md); placa não liberada.

Atualização NET-22 (26/11/2026): variante de vídeo corrige sensibilidade do anel de fases a atrasos distintos de buffers. Shift AHC164/NOR LVC1G27 e carry de linha registrado; 36 CIs, um a mais. 384 combinações de atrasos e256 de assimetria de pulsos, 6.886 casos ideais da CPU, dois cenários temporizados de1.062, boot/quadro completo e cortes de reset passaram; osciladores físicos e fechamento global continuam pendentes. Ver [circuito e evidências](docs/engineering/NET22.md); placa não liberada.

Atualização NET-21A (26/11/2026): supervisor candidato TPS3808 e recepção Schmitt resolvem o conflito do orçamento de carga anterior: 20 pF previstos contra condição de teste de 50 pF. Oito CIs preservados; 48 cortes de escrita, quatro com CPU real, raw scan temporizado e reservas condicionais passaram. Nova janela interna proposta de 5,392 V exige qualificação da fonte. Ver [circuito, resultados e limites](docs/engineering/NET21.md); produção continua bloqueada.

Atualização NET-20A (26/11/2026): domínios de reset ligados à CPU/MMIO/memórias; 48 cortes de escrita observados nos pinos SRAM, inibição em até 80 ns no cenário selecionado, pausas de clocks e raw scan passaram. Supervisor continua forcepoint qualificado: Ci máximo do buffer esgota o CL=10 pF da condição temporal anterior, sem margem de trilha. Ver [evidências e limites](docs/engineering/NET20.md); placa não liberada.

**Avanço NET-19A:** [CPU com MMIO e teclado por pinos](docs/engineering/NET19A.md): 6.886 casos ideais, dois cenários temporizados de 1.062 casos e boot/quadro completo passaram. Diagnóstico de varredura executa na CPU; três pacotes do controlador passam a AHC174, mantendo lógica e quantidade. Energia/reset global, clock/DAC, firmware de eventos e placa física continuam pendentes.

**Nova recuperação, 26/11/2026:** [exportação local do ISA-1](docs/EXPORT_RECOVERY_2026-11-26.md), com quatro registros de conversa, 240 arquivos disponíveis e duas Pages. REV33 e REV76 completas foram recuperadas e suas auditorias reproduzidas. Permanecem 33 anexos sem conteúdo nesta exportação e 72 IDs de mensagens de origem ausentes; não se declara recuperação integral.

**Avanço NET-18:** [alimentação e supervisão](docs/engineering/NET18.md): nova folha candidata de seis CIs/100 pinos, 64 cenários condicionais de reserva de energia e regressões de reset passaram. Consumo real, conversor/USB-C/POR e integração global permanecem abertos; o modelo oficial do regulador não concluiu a simulação.

**Avanço NET-17:** [teclado com alvo de contato de 500 Ω](docs/engineering/NET17.md): variante nativa com resistores nas linhas, espera de 2,60 ms e proteção da retomada. Passaram 768 cenários elétricos condicionais e regressões digitais; a política de até duas teclas ainda é referência no host. Medições das membranas, integração CPU/energia e fabricação continuam pendentes.

**Avanço NET-15:** [MMIO e teclado por pinos](docs/engineering/NET15.md): matriz de quatro membranas, registradores e espera de acomodação em esquema separado; testes digitais e envelope RC condicional registrados. Integração CPU desta etapa, reset/energia global e validação física continuam pendentes.

# ISA-1 — computador de 8 bits

Projeto de computador pessoal com CPU própria de lógica discreta, endereçamento de 16 bits, vídeo VGA e teclado de membrana. Este repositório reúne os materiais originais recuperados e a documentação de continuidade.

**Estado: protótipo lógico em desenvolvimento; hardware não liberado para fabricação.** A migração de 24/11/2026 recuperou três pacotes originais: revisão 9.3, revisão 9.8.3 e incremento 9.8.4.1. O histórico anterior permanece parcialmente recuperado. Ausências estão registradas em [LACUNAS.md](docs/LACUNAS.md).

## Começar

**Lista atual de testes e pendências:** [VALIDATION_STATUS](docs/engineering/VALIDATION_STATUS.md), com evidências, critérios de fechamento e revisões ainda necessárias. **Integração atual:** [NET-14C — CPU, boot e quadro com raster por pinos](docs/engineering/NET14C.md). Boot/quadro ideal completo passou com SRAM inicialmente desconhecida; instruções e cortes temporizados têm hipótese explícita de resolução binária na fronteira assíncrona. O modelo estrito ainda rejeita recovery externo e MTBF/analógico não estão aprovados. MMIO/teclado físico e fechamento global continuam em desenvolvimento.

**Desenvolvimento atual:** [NET-13 — chips de memória e barramento](docs/engineering/NET13.md), com SRAM/EEPROM, buffers TTL, muxes e troca de drivers a partir dos pinos KiCad. A variante do controlador desliga o driver antes de devolver VRAM ao vídeo. Testes cobrem todos os endereços, cenários de atraso e boot/quadro completo com SRAM inicialmente indefinida. Imagem EEPROM do diagnóstico em `firmware/net13`. Cargas reais, reset/alimentação, raster/relógios/DAC, MMIO/teclado por pinos, footprints e PCB continuam pendentes; não há liberação de fabricação.

**Registradores/dados:** [NET-06](docs/engineering/NET06.md). A referência fornecida pelo usuário para as membranas está em [KEYPAD_CONNECTOR.md](docs/engineering/KEYPAD_CONNECTOR.md).

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
**Avanço NET-16:** [ordem de reset e domínios de clock](docs/engineering/NET16B.md) em esquema candidato separado; testes isolados de cortes/pausas e envelopes RC registrados. Supervisor/energia, integração global e validação física continuam pendentes.
