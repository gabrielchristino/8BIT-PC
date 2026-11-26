# ISA-1 — Rev. 2.7: caminhos de leitura e escrita separados
Status: arquitetura candidata, não esquemático aprovado.

## Decisão
Substituir a proposta de 74HC245 bidirecional por **dois 74HC244** (buffers octais de saída tri-state), um para leitura EEPROM -> CPU_DATA, outro para escrita REG_DATA -> EEPROM_IO. Os registradores de endereço LO/HI e dados continuam como candidatos 3× SN74HC377. A separação reduz controle de direção e facilita o intertravamento.

- U_RBUF: entradas A <= EEPROM IO[7:0]; saídas Y => CPU_DATA[7:0]. /OE dos dois bancos unidos ao sinal READ_BUF_N, habilitado apenas quando todas as outras fontes de CPU_DATA estão desligadas.
- U_WBUF: entradas A <= REG_DATA.Q[7:0]; saídas Y => EEPROM IO[7:0]. /OE dos dois bancos unidos ao sinal WRITE_BUF_N, habilitado apenas com EEPROM /OE inativo.
- EEPROM /CE, /OE, /WE devem ser decodificados com permissões e reset. Não assumir que buffers e EEPROM comutam instantaneamente.
- A CPU não dirige EEPROM_IO diretamente. Endereços de EEPROM vêm dos registradores dedicados.

## SN74HC244 — pinagem de referência (SOIC-20, verificar fabricante e sufixo antes de BOM)
1=1/OE; 2=1A1; 3=2Y4; 4=1A2; 5=2Y3; 6=1A3; 7=2Y2; 8=1A4; 9=2Y1; 10=GND; 11=2A1; 12=1Y4; 13=2A2; 14=1Y3; 15=2A3; 16=1Y2; 17=2A4; 18=1Y1; 19=2/OE; 20=VCC.
As duas metades de quatro bits têm distribuição de pinos intercalada. **Não ligar pinos por ordem numérica sem conferir a função.**

## Ainda falta
Esquemático ERC e netlist completa dos registradores/decodificação, tempos reais de habilitação/desabilitação, impedância e fan-out, capacitores de desacoplamento, pinos de teste, subida de alimentação e medição física.

Referência de família: https://www.ti.com/lit/ds/symlink/sn74hc244.pdf
