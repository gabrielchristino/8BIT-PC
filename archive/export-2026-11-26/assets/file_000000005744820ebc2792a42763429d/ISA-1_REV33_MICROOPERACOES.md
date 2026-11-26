# ISA-1 — Revisão 3.3 — Microoperações simbólicas da CPU

**Status:** contrato arquitetural intermediário; NÃO é netlist, microcódigo binário, esquema elétrico nem PCB pronta.

## Fontes efetivamente reabertas
- `ISA-1_REV31_CPU_CONTRATO_E_REGRESSAO.md`
- `ISA-1_REV32_MICROCICLOS.md`
- `isa1_rev07_emulator.py`

## Entregáveis e teste
- `isa1_rev33_microcode.py` gera `isa1_rev33_microcode.json` com tabela de 19 opcodes implementados no emulador.
- Execução: `python3 isa1_rev33_microcode.py`.
- Resultado: 19 instruções, 101 passos simbólicos contando duas fases de busca de opcode em cada instrução; máximo 13 etapas.
- As asserções verificam unicidade, inexistência de transação READ e WRITE simultânea em uma mesma etapa textual, restrição textual de acessos MEM e preparação de MAR antes de WRITE.
- **Limitação crítica:** esses testes não comprovam temporização, exclusão elétrica de drivers, capacidade dos multiplexadores ou equivalência formal com o emulador.

## Contrato provisório
- Registradores arquiteturais: A, B, PC, SP, Z, C.
- Temporários **propostos** (ainda não contados como CIs): IR, MAR, MDR, TMP, TPH, EA, RETADDR.
- Busca: MAR recebe PC; leitura entrega IR; PC incrementa.
- Imediato 16 bits little-endian: primeiro byte TMP (baixo), depois TPH (alto), formando EA.
- CALL: após buscar endereço de destino, empilha endereço de retorno alto e baixo, com SP decrescente; RET lê baixo e alto com SP crescente.
- SUB: carry=1 significa ausência de empréstimo.
- Escrita: dados e endereço devem ser estáveis antes de /WE ativo; ainda falta dividir fases físicas de setup, pulso e hold.

## Bloqueios e riscos identificados
1. **Não congelar opcodes 32,33,34,35,36,42,54**: aparecem na especificação 3.1, mas não no emulador rev07.
2. `MAR<-PC` e `PC<-PC+1` podem exigir incrementador dedicado e microestados adicionais conforme datapath escolhido.
3. Atualizar SP no mesmo passo abstrato que WRITE não implica que o circuito real possa fazer isso no mesmo flanco. A decomposição física precisa respeitar setup/hold.
4. `EA` deve sobreviver ao CALL enquanto MAR muda para endereços de pilha.
5. Uma única porta de memória com multiplexação exige estados de transição e saída em alta impedância quando necessário.
6. ROM, SRAM, VRAM, I/O, vídeo CVBS, teclado, ZIF e reset ainda não estão interligados em esquemático.
7. Não há prova de que 74HC em frequência escolhida atenda ao pior caminho de propagação; clock ainda não fixado.

## Próxima etapa técnica
Selecionar um datapath fisicamente realizável e contabilizar CIs: registradores, ALU, incrementadores, muxes, transceptores e microsequenciador. Só depois gerar sinais por microestado, verificar com simulação digital independente e criar esquema pin-to-pin em KiCad.
