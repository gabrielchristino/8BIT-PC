# ISA-1 — Revisão 4.1 — Comparação dos incrementadores PC e SP

**Status:** comparação arquitetural e testes de função. **Não aprovado eletricamente para PCB.** Base: revisão 4.0, `ISA-1_REV40_CAMINHOS_16_BITS.md`.

## PC + 1 (16 bits)

1. **Quatro somadores 74HC283**, em cascata, com B=0 e carry-in inicial=1. Cada estágio de 4 bits recebe o carry do anterior. **4 CIs**, além do registrador PC e seleção de carga. O atraso de carry deve ser calculado com os valores máximos do fabricante e carga real.
2. **Portas XOR/AND:** `out[0]=~PC[0]`; para i>0, `out[i]=PC[i] XOR (AND PC[0..i-1])`. Implementação uniforme de 16 XOR e 14 AND binários: **4 × 74HC86 + 4 × 74HC08 = 8 CIs** (a primeira XOR pode virar inversor, mas não reduz necessariamente a quantidade de encapsulamentos). Propagação sequencial por até 14 AND se implementada em ripple; pode usar prefixo balanceado, com outras conexões/fanout. **Não é economia de encapsulamentos** perante 74HC283.
3. **Contadores síncronos de 4 bits com carga paralela**, em cascata, para integrar armazenamento e incremento. Exemplo de classe: 74HC163, sujeito a conferência de variante, encapsulamento, reset, pinos de habilitação e temporização. São quatro CIs contadores mais lógica de habilitação de nibbles; podem substituir os registradores PC de 16 bits **e** o incrementador. Contudo, o PC também precisa de carga arbitrária por `JMP`, `CALL` e `RET`, e a cadeia de carry/habilitação deve estar estável antes da borda de clock. Não selecionado até completar pinagem e temporização.

## SP +1 / -1

**Um único caminho de quatro 74HC283** pode executar ambas as operações:

- `INC`: B=0000h, carry-in=1 → SP+1.
- `DEC`: B=FFFFh, carry-in=0 → SP−1, módulo 65536.

Se `DEC` for sinal lógico ativo-alto, cada bit B recebe `DEC`, e o carry-in inicial recebe `NOT DEC`. Requer distribuir o controle com fanout apropriado e garantir estabilidade antes de carregar o SP. **Não são necessários dois somadores**. Essa equivalência foi testada exaustivamente em software.

## Decisão provisória

- **PC:** manter 4×74HC283 como referência elétrica conservadora; investigar 4×contadores com carga paralela porque podem eliminar registradores e muxes, não apenas substituir portas.
- **SP:** escolher um único conjunto de 4×74HC283 para incremento/decremento, sujeito a temporização e à implementação dos caminhos de carga.
- **XOR/AND:** não adotar para o PC apenas por aparente simplicidade: contagem direta de CIs é maior, e o pior caminho de carry precisa ser avaliado.

## Testes executados

`python3 isa1_rev41_incrementers.py` verificou os 65.536 valores de PC/SP para +1 com XOR/AND e 74HC283, −1 com 74HC283 e +1 por cascata de contadores; verificou também 50.000 ciclos de −1 seguido de +1 em SP. **312.144 verificações comportamentais**; nenhuma falha. Não simula portas, ruído, clock, fanout, setup/hold, potência ou glitches.

## Pendências obrigatórias

1. Conferir datasheets oficiais e pinagens exatas de 74HC283, 74HC163, 74HC86, 74HC08 e buffers de direção, incluindo disponibilidade SOIC.
2. Definir o clock alvo e calcular a cadeia crítica com valores máximos de atraso, setup e hold sob VCC e carga escolhidos.
3. Comparar **circuitos completos** (PC registradores + mux de carga + incremento; SP registradores + mux de carga + ±1), não apenas os CIs aritméticos.
4. Confirmar comportamento de reset, `JMP`, `CALL`, `RET`, carga paralela e overflow em simulação de ciclos antes de gerar esquema KiCad.
5. Evitar interpretar contadores ou modelos matemáticos como comprovação elétrica.
