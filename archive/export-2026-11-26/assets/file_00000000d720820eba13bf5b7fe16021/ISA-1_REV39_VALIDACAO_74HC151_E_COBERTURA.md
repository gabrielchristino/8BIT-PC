# ISA-1 — Rev. 3.9 — Validação do 74HC151 e auditoria das rotas

**Decisão:** adotar **74HC151D SOIC-16 como candidato preferencial** para os dois multiplexadores 8:1 de 8 bits da Rev. 3.8; **não** aprovar ainda a netlist completa da CPU.

## Fontes do fabricante
- TI, SN74HC151: https://www.ti.com/lit/ds/symlink/sn74hc151.pdf
- Nexperia, 74HC/HCT151, Rev. 11: https://assets.nexperia.com/documents/data-sheet/74HC_HCT151.pdf

O 74HC151 seleciona **uma** entre oito entradas de **um bit**, portanto são oito CIs para um barramento de 8 bits. Disponível em SOIC-16, faixa 2–6 V na versão HC; há saídas normal e complementar, habilitação ativa baixa. Não confundir a nomenclatura comercial '8-input multiplexer' com oito canais independentes. O 74HCT151 tem limiares TTL e operação nominal em 5 V; para interligação HC-CMOS, preferir HC após auditoria de níveis de todos os fornecedores.

## Pinagem da versão SOIC-16
I0=4, I1=3, I2=2, I3=1, I4=15, I5=14, I6=13, I7=12; S0=11, S1=10, S2=9; /E=7; Y=5; /Y=6; GND=8; VCC=16. Saída Y não inversora. Com /E=1, Y=0 e /Y=1, **não** alta impedância.

## Contagem de componentes
- DB principal: 8 × 74HC151D, versus 14 × 74HC157 em árvore.
- Seleção ADDR_BYTE: 8 × 74HC151D, versus 14 × 74HC157 em árvore.
- Total parcial: 16 em vez de 28, redução de 12 CIs (42,9%).
- MUX de 16 bits para MAR da Rev. 3.7 é **outro circuito** e não entra na economia.
- Não contar 16 CIs como BOM definitiva: as fontes do DB e caminhos de destino ainda estão incompletos.

## Auditoria de cobertura de instruções
O arquivo `isa1_rev33_microcode.json` contém 19 instruções e 101 microetapas. A análise identificou caminhos ainda não fechados:
1. `CALL`: bytes alto e baixo de RETADDR precisam alcançar MDR; `ADDR_BYTE` atual não os oferece.
2. `JMP`/`CALL`/`JZ`: caminho de EA[15:0] para PC[15:0] e carga do PC ainda não definido.
3. `RET`: caminho TPH:TMP para PC[15:0] ainda não definido.
4. `EA<-TPH:TMP`: carga de EA de 16 bits ainda não definida.
5. `SP+1`/`SP-1`: incrementador/decrementador de 16 bits ainda não definido.
6. ALU/flags: funções e habilitações de atualização de A, C, Z ainda não especificadas fisicamente.
7. `MEM`/`CONST`: a leitura externa precisa de isolamento real; constantes e entrada I/O permanecem indefinidas.

Essas lacunas **não são falhas do 74HC151**: são limitações da topologia de dados incompleta.

## Testes executados
`isa1_rev39_mux_audit.py` valida a tabela de pinos, gera 16 instâncias com entradas individualizadas, testa 1.600.000 seleções de bits com um decodificador independente da indexação esperada e percorre as 101 microetapas para identificar dependências. Resultados em JSON. Isso é teste **lógico de software**, não simulação de atrasos ou de tensões.

## Condições antes de esquemático/PCB
- Medir/calcular atraso máximo do 74HC151 para VCC e carga efetivos (não usar atraso típico para fechar clock).
- Verificar fanout de S0/S1/S2: cada seleção dirige oito entradas; considerar buffer se necessário.
- Garantir /E em nível definido e entradas não utilizadas amarradas; não usar /E como isolamento tri-state.
- Registrar seleção e enables; evitar /WE assíncrono originado do MUX.
- Completar matriz origem→destino por microetapa, especialmente CALL/RET, antes de travar BOM.

**Veredito:** componente compatível e otimização válida no nível lógico; integração elétrica e CPU completa ainda não aprovadas.
