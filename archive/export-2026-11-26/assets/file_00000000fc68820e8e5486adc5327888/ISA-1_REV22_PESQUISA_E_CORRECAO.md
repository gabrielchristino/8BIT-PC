# ISA-1 — Revisão 2.2: contenção de barramento, pesquisa e validação

Data: 2026-11-23. Status: pesquisa e modelo abstrato, **não** aprovação de circuito físico.

## Fontes consultadas

- Gigatron, manual com esquemáticos: https://gigatronttl.eu/media/Gigatron-manual.pdf — barramentos separados de dados e resultado, buffers tri-state.
- Gigatron, ensaio da lógica de escrita RAM: https://hackaday.io/project/20781-gigatron-ttl-microcomputer/log/56269-testing-the-ram-write-control-logic — endereço estabiliza na primeira fase; escrita na segunda.
- Magic-1, microarquitetura: https://mail.homebrewcpu.com/microarchitecture.htm — autor descreve problemas de propagação de clock e seleção de famílias 74F/74LS para contorná-los.
- Magic-1: https://www.magic-1.org/ — CPU com ~200 CIs TTL.
- Comunidade Ben Eater, glitches EEPROM e sugestão de 74LS138: https://www.reddit.com/r/beneater/comments/1dwxcxr/
- Comunidade Ben Eater, falha 74LS245 por contenção: https://www.reddit.com/r/beneater/comments/1bxww8v/
- TI SN74HC245: https://www.ti.com/product/SN74HC245 — DIR e /OE permitem isolamento, mas transições dependem dos tempos de habilitação/desabilitação.

## Diagnóstico

1. Uma seleção one-hot em estados estáticos não garante ausência de sobreposição durante transientes.
2. Um decodificador combinacional pode produzir pulsos espúrios durante mudança de entradas, apesar de no máximo uma saída ativa em estados estabilizados.
3. Um transceptor 74HC245 isolado não resolve contenção no lado oposto; ambas as pontas devem ser auditadas.
4. Controle direto de /WE por EEPROM ou lógica combinacional sujeita a glitch é risco de corrupção.
5. Saídas de registradores sem reset podem ter estado indefinido ao ligar; usar reset ou mascarar sinais de habilitação e fazer inicialização síncrona.
6. **Atenção adicional:** 74HC273 não tem clock-enable. Não usar AND simples para 'gating' do clock sem analisar pulsos espúrios; preferir mux na entrada D ou um registrador com enable adequado.

## Proposta de correção — ainda candidata

- Caminho interno de operandos por mux; barramento de resultado separado.
- SRAM com /OE, /WE, /CE derivados de estados registrados e mascarados por `RESET_OK`.
- Controle de acesso: IDLE -> READ -> TURN -> WRITE_SETUP -> WRITE_PULSE -> WRITE_HOLD -> IDLE, com TURN também no sentido inverso quando necessário.
- Em TURN, SRAM /OE=1, /WE=1 e transceptor /OE=1. Trocar DIR somente depois de desabilitar o transceptor; habilitar apenas após janela segura.
- Garantir que a CPU não dirige o barramento interno durante READ.
- Evitar pulsos espúrios em clock e /WE; usar máquina de estados registrada e revisar saídas combinacionais com análise de hazards.
- O dimensionamento da guarda exige tempos máximos de desligamento, mínimos de habilitação, skew do controlador e cargas reais; não usar 21 unidades do modelo como valor de hardware.
- Proteger reset com nível inativo definido por resistores apropriados e supervisor de alimentação a avaliar.

## Experimento executado

`python isa1_rev22_bus_test.py` verifica 441 pares de atrasos hipotéticos (off/on de 0 a 20 unidades) por valor de guarda.

| Guarda abstrata | Sobreposições potenciais |
|---:|---:|
| 0 | 231 |
| 10 | 66 |
| 20 | 1 |
| 21 | 0 |
| 30 | 0 |

Critério conservador: igualdade dos instantes é insegura. Também foram verificados 6 estados estáticos e injetado cenário de falha de decodificação com ambos drivers habilitados, detectado pelo modelo.

**Limitações:** modelo não representa circuitos com portas reais, tempos de fabricantes, ruído, transientes de alimentação, hazards ou validação física. Os resultados apenas comprovam a regra matemática da janela de guarda sob os atrasos assumidos.

## Próximas tarefas antes de KiCad

1. Congelar topologia de barramento e lista de drivers por segmento.
2. Selecionar SRAM e buffer com datasheets de uma mesma condição de operação (VCC, temperatura, CL).
3. Criar tabela pino-a-pino dos sinais /OE, /WE, /CE, DIR, CLK e RESET.
4. Implementar controlador com portas/flip-flops e simular transições assíncronas e reset.
5. Analisar escrita de SRAM: tAS, tAW, tWP, tDW, tDH, tWR e atrasos de /OE e /CE conforme modelo selecionado.
6. Definir clock e margens; só depois autorizar layout e fabricação.
