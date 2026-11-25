# Verificação da migração

`results.json` registra a execução local com Python 3.12.14 de 23 bancadas recuperadas: **22 passaram e uma falhou**, por ausência de `diagnostic.asm` no pacote rev983. Os arquivos históricos foram executados em cópias temporárias, mantendo snapshots e resultados originais intactos.

As bancadas aprovadas abrangem decodificação de memória, arbitragem VRAM, programas integrados, reset/instruções, segurança, EEPROM abstrata, microcódigo, controle, sequenciador, teclado, ALU, aritmética e contadores. Consultar as saídas de cada bancada para números e escopos; não somar casos de revisões diferentes como testes independentes sem sobreposição.

O verificador remove as quatro lanes da cópia temporária, executa `sequencer.py` e compara os binários recém-gerados aos originais. A comparação de integridade dos ZIPs é feita separadamente por `scripts/verify_archive.py`.

Reproduzir:

```text
python scripts/verify_recovered.py
python scripts/verify_archive.py
```

O primeiro comando retorna código diferente de zero enquanto a bancada conhecida continuar falhando. O relatório mantém stdout/stderr completos, incluindo a dependência ausente. As verificações não demonstram funcionamento elétrico, fabricação, temporização real ou integração física CPU/VGA/teclado.
