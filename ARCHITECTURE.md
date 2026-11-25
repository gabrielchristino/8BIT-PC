# Arquitetura recuperada

Síntese editorial da migração, baseada principalmente em `revisions/rev983/{cpu,system,microcode,control,sequencer}.py` e na conversa «Construir computador 8 bits». Descreve o modelo recuperado, não um circuito físico concluído.

## CPU e ISA

Dados de 8 bits, endereços de 16 bits, operandos de endereço em ordem little-endian. A e B têm 8 bits; X, PC e SP têm 16 bits. Flags arquiteturais: Zero e Carry. O estudo 9.8.4 também lista EA, RET, IR e MDR como armazenamento candidato; o controle Python usa temporários locais e não comprova um banco físico com essa organização.

| Opcode hexadecimal | Operação |
|---|---|
| 00 | NOP |
| 10, 11 | LDA imediato, LDB imediato |
| 20–26 | ADD, SUB, AND, OR, XOR, SHL, SHR |
| 30, 31 | LDA absoluto, STA absoluto |
| 32–36 | LDX imediato, LDA [X], STA [X], INX, DEX |
| 40–42 | JMP, JZ, JNZ |
| 50–54 | CALL, RET, PUSH A, POP A, CMP |
| FF | HALT |

`assembler.py` aceita PUSH/POP e HALT/HLT. O opcode FF é uma única instrução, apesar dos aliases. ADD atualiza Z/C; SUB/CMP usam Carry como ausência de empréstimo; operações lógicas preservam C; shifts armazenam o bit deslocado em C; CMP preserva A. Consultar o código para os efeitos exatos de cargas e POP sobre Z.

SP vazio = 8000h. PUSH escreve em SP-1 e somente atualiza SP após a transação; POP lê em SP e incrementa após a leitura. CALL empilha alto e baixo; RET recupera baixo e alto. X possui aritmética circular de 16 bits; SP possui guardas de limites. Proteções de pilha não detectam toda colisão com dados e programas.

## Mapa lógico da revisão 9.8.3

| Faixa | Mapeamento |
|---|---|
| 0000–7FFF | RAM 32 KiB; boot sobrepõe ROM em 0000–3FFF |
| 8000–9FFF | Janela VRAM 8 KiB, quatro bancos |
| A000–BFFF | Região de I/O no decodificador |
| C000–FFFF | Janela EEPROM 16 KiB, dois bancos |

A000 seleciona VRAM; A001 seleciona EEPROM; A002 desativa overlay de boot quando o bit 0 é escrito. O modelo `system.py` usa A010 para linha do teclado e A011/A012 para colunas. A proposta ENG-KBD-01 mantém os endereços simbólicos e exige conciliação com a decodificação real: ela ainda não integra sua habilitação global ao modelo Python de teclado.

O boot experimental salta de 0000h para C040h. Trocar o banco da EEPROM enquanto se executa nela exige uma rotina segura em RAM. `eeprom.py` é um controlador abstrato de gravação, limitado à faixa física 7800–7FFF e condicionado a alimentação, RUN e execução em RAM; não emula fisicamente a proteção do componente.

## Vídeo, barramento e controle

O modelo tem raster de 200 × 525 ciclos e área ativa de 160 × 480 ciclos, repetindo verticalmente cada linha lógica quatro vezes. O endereço de pixel usa stride de 256 bytes e 120 linhas. A janela de acesso da CPU à VRAM fica no apagamento horizontal. A frequência e a geração analógica VGA continuam dependentes do circuito e de sua validação.

O barramento usa eventos ISSUE/WAIT/COMMIT e handshake de quatro fases no modelo integrado. Cancelamento por geração evita retomada de operações antigas após reset. Essas abstrações não modelam metastabilidade nem pulsos elétricos parciais.

O controle horizontal define 26 bits por palavra. `sequencer.py` organiza 8192 palavras de 32 bits: A12 seleciona FETCH, A11–A4 são opcode, A3–A0 são microetapa. Quatro arquivos de 8192 bytes representam as lanes da ROM. Endereços sem uso recebem HALT seguro. O sequenciador é um modelo isolado; os testes do controle e as ROMs não comprovam uma CPU física executando essas EEPROMs.

## Teclado e hardware

Quatro matrizes comerciais 4 × 4 formam uma matriz compartilhada 4 × 16. A página ENG-KBD-01 propõe linha ativa baixa e demais linhas em alta impedância, rejeição conservadora de quadros acima de duas teclas, cancelamento de eventos e rearme após vazio estável. Polling alvo de 200 Hz e debounce de 15–20 ms são parâmetros propostos.

74HC273, 74HC139, 74HC125 e dois 74HC244 são candidatos do bloco de teclado. A própria proposta identifica margem elétrica insuficientemente demonstrada para 220 ohms e 16 colunas baixas; não converter esses valores em BOM definitiva.

ALU candidata: dois 74HC283, portas XOR/AND/OR e oito 74HC151; o subtotal histórico de 18 CIs exclui controle, flags e armazenamento. X com 74HC191 é candidato; SP conserva provisoriamente o caminho anterior por precisar simultaneamente de SP e SP-1. Esquemas, layout, pinagem e validação elétrica permanecem pendentes.
