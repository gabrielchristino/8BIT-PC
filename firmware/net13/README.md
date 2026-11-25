# Imagem do diagnóstico de integração

`integration-diagnostic-eeprom.bin` contém os 32.768 bytes físicos da EEPROM principal usados no boot aprovado da NET-13. Gere novamente com `python3 tools/export_memory_diagnostic.py` no Ubuntu WSL. O arquivo `.hex` é um byte por linha para `$readmemh`, sem o formato Intel HEX. Origem, fontes e hashes estão em `origin.json`.

Esta imagem nova deriva do diagnóstico RTL-01 e não substitui o `diagnostic.asm` ausente do pacote histórico. Foi comparada com a imagem efetivamente executada, com SRAM inicialmente indefinida. Não é firmware final de produto ou autorização de fabricação. A EEPROM do circuito candidato tem WE permanentemente alto e precisa receber sua imagem por programação externa; não há programação em circuito implementada.
