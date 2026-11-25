# Roadmap de continuidade

## Iteração ativa — 9.8.4.2

- [x] Preparar Icarus Verilog, ngspice e KiCad CLI no WSL Ubuntu.
- [x] Modelar carga transparente HC191, HC157 e HC377 e testar inicialização/carga de 16 bits.
- [x] Executar rodadas lógica e com atrasos selecionados, reset, WAIT e testes negativos dos monitores.
- [x] Gerar esquema parcial do banco X, mapa de pinos e conferir netlist exportada.
- [ ] Mapear sequenciamento e portas a CIs/controle real; comparar custo com alternativas.
- [ ] Fechar temporização com atrasos mínimos, skew e cargas reais.
- [ ] Resolver SP-1 e integrar o controle à CPU com regressão das 26 instruções.

A etapa de carga tem uma bancada aprovada, mas ainda não está fechada como circuito físico completo. Detalhes e critérios em docs/engineering/REV9842.md e PRODUCTION_GATES.md.

As etapas abaixo organizam pendências recuperadas e trabalho necessário para concluir a migração. Não representam revisões implementadas ou datas prometidas.

## 1. Completar a recuperação

- [ ] Recuperar exportação completa das conversas, incluindo ramificações, anexos e imagens.
- [ ] Recuperar arquivos ausentes e revisões individuais de [LACUNAS.md](docs/LACUNAS.md), especialmente rev33 e `diagnostic.asm`.
- [ ] Registrar bytes, hashes e origem; comparar versões antes de qualquer consolidação.
- [ ] Resolver divergências de numeração: REV76 = 7.6; o pacote chamado rev984 corresponde ao estudo 9.8.4.1.

Aceitação: cada material citado tem arquivo recuperado ou ausência identificada; nenhuma alegação de completude sem inventário verificável.

## 2. Estabelecer uma base de desenvolvimento

- [ ] Criar versão de trabalho a partir do snapshot completo rev983, mantendo originais intactos.
- [ ] Recuperar diagnóstico e obter aprovação das bancadas existentes; complementar apenas riscos não cobertos.
- [ ] Conciliar especificação ISA, mapa de memória, boot, pilha e teclado entre o código 9.x e ENG-KBD-01.
- [ ] Validar integração do sequenciador/ROM ao modelo da CPU, não apenas equivalência dos geradores e modelos isolados.

## 3. Fechar os blocos digitais

- [ ] 9.8.4.2 histórica: carga e inicialização segura dos contadores.
- [ ] 9.8.4.3 histórica: resolver SP-1, commit e falhas durante PUSH/POP/CALL/RET.
- [ ] Proteção de pilha e colisões; arbitragem de barramentos; datapath e controle integrados.
- [ ] Comparar contadores, registradores e somadores com BOM e caminho crítico completos.
- [ ] Criar HDL/testbenches com reset, WAIT, CDC, opcodes inválidos e propriedades de segurança.

## 4. Integrar o teclado real

- [ ] Medir pinagem, resistência e capacitância das quatro membranas.
- [ ] Dimensionar linha ativa e proteção; resolver margem de VOL no pior caso.
- [ ] Esquema KiCad com decodificação real e ENABLE; driver, ABI e fila de eventos.
- [ ] Validar pares, trios em L entre módulos, quadros mistos, bounce, cancelamento, fila cheia e carga sobre CPU/VGA.

## 5. Validar hardware e fabricar protótipo

- [ ] Esquemático completo, datasheets identificados por revisão, pinagem e encapsulamentos.
- [ ] Orçamento de alimentação USB-C, reset/brownout, desacoplamento, níveis TTL/CMOS e saída VGA.
- [ ] Temporização com limites máximos, cargas reais, modelos SPICE quando aplicável e formas de onda digitais.
- [ ] ERC/DRC, revisão de layout/BOM e plano de montagem/teste.
- [ ] Protótipo físico e medição de boot, CPU, memórias, VGA e teclado antes de declarar validação física.

## 6. Software do computador

- [ ] Consolidar monitor/boot, diagnóstico, formatos da EEPROM e rotinas seguras de salvamento.
- [ ] Biblioteca de vídeo, teclado e testes de integração de programas.
- [ ] Retomar interpretador BASIC e recursos de uso pessoal somente com requisitos e fontes recuperados.
