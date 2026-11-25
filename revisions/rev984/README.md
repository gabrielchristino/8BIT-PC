# ISA-1 9.8.4.1 — Contadores candidatos
Modelo ideal de quatro nibbles com clock comum e habilitação paralela: E[i] = COMMIT AND terminal de todos os nibbles inferiores. Terminal zero na descida, quinze na subida. Não usar RCO como clock nesta topologia. Carga assíncrona do HC191 exige fase protegida e dados estáveis. Inicialização X=0000 e SP=8000 via carga; nenhuma escrita durante reset.
PUSH ainda requer endereço SP-1 antes de commit: manter somador dedicado provisoriamente ou avaliar alteração do microcódigo com pré-decremento protegido. Não adotar economia de quatro CIs como definitiva. POP usa SP atual e incrementa após leitura. Limites da pilha preservam overlay de boot.
Fontes: https://www.ti.com/product/SN74HC191 ; https://www.ti.com/product/SN74HC193 ; https://www.ti.com/lit/ds/symlink/sn74hc191.pdf
Executar python counter.py. Teste isolado, sem integração CPU, sem temporização, sem ERC. Pacote incremental apenas.
