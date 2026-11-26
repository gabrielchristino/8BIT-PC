# ISA-1 — Revisão 2.3: CI removível com programa e SAVE

Data: 2026-11-23. Status: proposta e testes de formato lógico, **não aprovado eletricamente**.

## Decisões confirmadas pelo usuário

- Um único CI removível em soquete ZIF para código e dados de SAVE.
- O próprio ISA-1 deve gravar um CI inicialmente vazio.
- O programa é carregado para a SRAM e executado nela; o CI funciona como mídia removível semelhante a disquete.
- A placa principal também terá armazenamento interno, a definir.
- Troca de CI somente com equipamento desligado, na primeira versão.

## Layout lógico candidato — EEPROM de 32768 bytes

| Offset | Comprimento | Conteúdo |
|---|---:|---|
| 0000h–003Fh | 64 | Cabeçalho, assinatura ISA1, offset/tamanho/CRC32 do programa; outros campos ainda indefinidos |
| 0040h–783Fh | 30656 | Código e recursos (capacidade máxima teórica da região, não necessariamente executável integralmente na SRAM) |
| 7840h–7C3Fh | 1024 | SAVE A |
| 7C40h–7FFFh | 1024 | SAVE B |

Cada SAVE possui 16 bytes de cabeçalho (assinatura, geração de 32 bits, comprimento, CRC32) e até 1008 bytes de dados. Dois slots servem como redundância de gravação, **não** como dois saves independentes do jogador.

## Falha encontrada e correção no modelo

A primeira versão do teste tentou atualizar um slot já ocupado copiando bytes desde o início. Falhou: a geração podia ser parcialmente modificada antes do restante do registro, permitindo interpretar conteúdo antigo com metadados parcialmente novos. Essa falha foi detectada por uma asserção real, não por inspeção manual.

O modelo foi corrigido para invalidar primeiro os quatro bytes da assinatura do slot de destino, escrever seu corpo e somente depois confirmar a assinatura. Em caso de interrupção, o outro slot deve permanecer legível.

**Advertência crítica:** o modelo supõe operações byte a byte ordenadas e persistentes. Uma EEPROM física pode usar page-write, ciclos internos, polling e comportamento de interrupção de energia diferente. A escrita do marcador por último não constitui por si só garantia física de atomicidade. Será necessário verificar datasheet, restrições de página, /WE, proteção e talvez um circuito de supervisão de alimentação. Não declarar o SAVE à prova de quedas de energia até teste físico.

## Testes executados

`python isa1_rev23_media_test.py`

- 2053 pontos de interrupção em duas situações: primeiro preenchimento de slot vazio e atualização de slot ocupado com protocolo de invalidação.
- 12 inversões de bits de payload detectadas por CRC32.
- Programa com checksum permanece íntegro nos casos simulados.
- Programa maior que a região disponível é rejeitado.

Limitações: não testou endurance, gravação por página, todos os padrões de corrupção, wrap-around da geração, nem escrita elétrica. O CRC32 não é garantia contra corrupção arbitrária ou maliciosa.

## Projeto elétrico ainda pendente

1. Escolher modelo **exato** de EEPROM paralela 5 V, DIP-28, com disponibilidade real; AT28C256 é candidata, não componente aprovado.
2. Consultar datasheet do fabricante escolhido para pinagem, /CE, /OE, /WE, tempos, page-write, polling, endurance e proteção contra gravação.
3. Definir o circuito ZIF de 28 pinos, orientação, proteção de pinos e controle de escrita; não trocar CI energizado.
4. Definir como a CPU apresenta endereço de 15 bits e dados de 8 bits ao chip sem conflito com SRAM ou vídeo.
5. Projetar controle de /WE com estados registrados, bloqueio no reset e autorização explícita de gravação.
6. Especificar comandos do monitor: LIST, LOAD, RUN, SAVE CHIP, VERIFY (nomes provisórios); para saves de jogos, rotina de sistema específica.
7. Definir formato de programa executável (endereços de carga, relocação, entrada, pilha, RAM livre, ABI) e estratégia para programas maiores que a RAM disponível.
8. Medir margem temporal e validar em protótipo antes de fabricar a PCB final.

## Referência arquitetural

O Gigatron continua como referência para separação de barramentos e simplicidade de caminhos, sem copiar sua ISA ou eliminar os recursos próprios do ISA-1.

## Arquivos

- `isa1_rev23_media_test.py`: teste lógico reproduzível.
- `isa1_rev23_results.json`: resultados.
