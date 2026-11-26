# ISA-1 — Revisão 5.5 — Alimentação, supervisão e inibição de escrita

## Escopo e status
Projeto preliminar de alimentação **5 V regulados** para lógica 74HC, supervisor, clock e memórias. Esta revisão **fecha o contrato lógico e a seleção provisória do supervisor**, não a segurança elétrica da alimentação. Não autoriza fabricar PCB nem conectar /WE de EEPROM sem análise adicional.

## 1. Arquitetura de alimentação
- Entrada externa: **fonte DC regulada de 5 V**, com corrente nominal a dimensionar após orçamento de consumo de CPU, vídeo, teclado e memória. Não escolher conector, fusível ou capacidade nominal sem conhecer consumo total.
- Criar redes `+5V_SYS` e `GND`; plano de retorno contínuo, capacitores cerâmicos **100 nF por CI** próximos aos pinos de alimentação como ponto de partida de layout, e capacitância bulk a calcular a partir de transientes de carga e características da fonte. Evitar declarar que 100 nF por CI resolve integridade de alimentação.
- Para periféricos não tolerantes a 5 V, adicionar domínio separado e tradução de níveis; não assumir que o futuro vídeo ou armazenamento usam 5 V.
- Considerar proteção contra inversão de polaridade, sobrecorrente e ESD na entrada, a especificar com fonte/conector escolhidos.

## 2. Supervisor selecionado para protótipo
**TPS3808G50DBVR**, Texas Instruments, encapsulamento **SOT-23-6** (exceção justificada à preferência SOIC), threshold nominal **4,65 V**. Não é um regulador. Saída `/RESET` open-drain. Pinagem vista superior:

| Pino | Sinal | Rede proposta |
|---|---|---|
| 1 | /RESET | `SUP_RESET_N` com pull-up **10 kΩ a +5V_SYS** (valor preliminar, dentro da faixa TI) |
| 2 | GND | GND |
| 3 | /MR | `MANUAL_RESET_N`, botão opcional ao GND; pull-up interno existente; revisar ESD e filtragem |
| 4 | CT | aberto inicialmente, para retardo fixo conforme datasheet; confirmar limites antes do layout |
| 5 | SENSE | `+5V_SYS` monitorado |
| 6 | VDD | `+5V_SYS`, cerâmico 100 nF a GND junto ao CI |

Fonte TI: https://www.ti.com/lit/ds/symlink/tps3808.pdf ; https://www.ti.com/product/TPS3808/part-details/TPS3808G50DBVR

**Advertência crítica:** abaixo da tensão mínima de operação do supervisor, sua saída não é garantida; o datasheet explicita região abaixo de VPOR com `/RESET` indefinido. Portanto, **supervisor + porta 74HC NÃO bastam para prometer /WE inativo durante toda a rampa**. O threshold de 4,65 V também deve ser confrontado com tolerâncias, VCC mínimo de todos os chips e tempo de resposta a quedas rápidas.

## 3. Sequência de partida preservada
- `/RESET` do supervisor limpa assincronamente os FFs 74HC74 de sincronização.
- `SYS_CLK` precisa existir e ser estável para que o PC 74HC163 seja zerado por reset síncrono.
- Após três bordas válidas, `CPU_RUN` sobe; o PC começa a operar na quarta borda, mantendo o bloqueio de carga e contagem da revisão 5.2.
- Necessário conferir tempos de recovery/removal na desassertiva de clear dos HC74, metastabilidade, clock válido, e margem temporal das portas; esta revisão não demonstra esses requisitos.

## 4. Segurança de escrita: regra lógica versus hardware
Contrato booleano **ideal**: `WRITE_PERMIT = POWER_GOOD AND CPU_RUN AND ADDR_VALID AND WRITE_REQ`; `/WE_SAFE = NOT WRITE_PERMIT`. `POWER_GOOD` deve representar uma condição eletricamente válida e independente do firmware. Cada memória terá um circuito de habilitação próprio, respeitando /CE e /OE, e preferencialmente uma polarização de /WE no pino da memória para o estado inativo.

**Não conectar diretamente** a saída combinacional acima ao /WE real como se ela fosse livre de glitches. Há risco de pulsos espúrios em mudanças de endereço, sinais assíncronos e brownout. É necessário definir temporização de escrita, eventual registro de comandos, e a ordem de desativação de /CE e /WE.

**Não usar resistor de pull-up como prova de segurança**: se VCC cai, o nível alto do pull-up também cai e os requisitos VIH/VIL deixam de ser garantidos. Se a memória tiver alimentação diferente da lógica, há risco de alimentação parasita pelos pinos. A EEPROM AT28C256 possui comportamento específico de escrita, SDP e limites de alimentação que precisam ser consultados no datasheet da variante exata. A proteção em subtensão pode requerer um circuito de write-protect dedicado e/ou retenção de alimentação da memória, a dimensionar.

## 5. Clock
**Oscilador ainda não selecionado.** Não fixar frequência nominal nem declarar margem temporal. Requisitos: oscilador CMOS compatível com +5 V, tempo de startup, duty cycle, corrente, jitter e carga de fan-out documentados; buffering se necessário. Evitar gating combinacional do clock. O sequenciador de reset só libera a CPU após bordas de clock válidas.

## 6. Testes executáveis
`python isa1_rev55_power_audit.py` produz `isa1_rev55_results.json`. Percorre 16 combinações de entradas da regra de /WE, e 65.536 valores iniciais do PC com quatro bordas de partida. Os testes demonstram apenas consistência booleana e da máquina ideal de estados; **não** modelam rampas analógicas, correntes, glitches, atrasos nem falhas de alimentação.

## 7. Critérios para realmente fechar a alimentação (pendências)
1. Orçamento de corrente completo e escolha de fonte/conector/proteção.
2. Verificação do datasheet do oscilador selecionado, VCC e margem temporal da cadeia HC163.
3. Escolha da SRAM e da variante exata AT28C256; revisão de /CE, /OE, /WE, tempos e alimentação mínima.
4. Circuito de write-inhibit que permaneça seguro durante rampa de alimentação, comprovado em simulação elétrica e bancada; teste de desligamento durante escrita de EEPROM.
5. Esquemático real e ERC; ensaios de power-on, power-off, brownout e reset manual com osciloscópio.

**Gate de fabricação: NÃO APROVADO.**
