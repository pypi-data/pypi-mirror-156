# Trabalho Prático Engenharia de Software 2

Grupo:
 - Francisco Bonome Andrade
 - Lucas Caetano Lopes Rodrigues
 - Lucas Starling de Paula Salles
 - Yasmin Araújo

# FastTask

O FastTask é um sistema para gestão de tarefas. O sistema é capaz de gerenciar diferentes _boards_, nos quais o usuário pode criar tarefas, com nomes, descrições, e prioridade.

Para executar o sistema, instale-o através do pip: `pip install fasttask`

O usuário pode interagir com o sistema utilizando a CLI:

```sh
$ fasttask board create UFMG --label Pessoal
$ fasttask task list
On Default (id=1):

$ fasttask board list
Default (id=1)
UFMG (id=2)

$ fasttask board checkout 2
$ fasttask task create projeto_es2_entrega_1 --label "ES2"
$ fasttask task list
On UFMG (id=2):
projeto_es2_entrega_1

$ fasttask task describe projeto_es2_entrega_1
Task details:
Id:  1
Name:  projeto_es2_entrega_1
Status:  ToDo
Creation date:  29/05/2022
Label:  ES2
Priority:  0
Time Worked in this task: 0
```

# Tecnologias utilizadas
O sistema foi desenvolvido utilizando Python 3.7+ para construção da CLI e das classes principais do sistema, e SQLite para armazenar os _boards_ e as tarefas criadas. A ferramenta Unittest também foi utilizada para criar testes unitários para os componentes do sistema.

# Relatórios do Lizard

Para gerar os relatórios, utilizamos a seguinte configuração para o Lizard:

- Threshold para `cyclomatic_complexity` é 5
- Ordenar por: 1) cyclomatic_complexity; 2) length
- Para os arquivos do sistema em `src/`

Você pode encontrar todos os relatórios na pasta `lizard_reports`.

O comando utilizado foi:

```sh
$ lizard -T cyclomatic_complexity=5 -s cyclomatic_complexity -s length paths src/main.py src/modules/dbhandler.py src/modules/clicontroller.py src/modules/command.py src/modules/board.py src/modules/task.py
```

Após finalizar o projeto inicial do sistema, esses eram os warnings gerados:

```sh
==========================================================================================
!!!! Warnings (cyclomatic_complexity > 5 or length > 1000 or nloc > 1000000 or parameter_count > 100) !!!!
================================================
  NLOC    CCN   token  PARAM  length  location  
------------------------------------------------
      24      7    145      1      24 parse@82-105@src/modules/command.py
      16      7     93      1      16 shell@110-125@src/modules/command.py
      17      6    107      1      17 parse_flags@136-152@src/modules/command.py
==========================================================================================
Total nloc   Avg.NLOC  AvgCCN  Avg.token   Fun Cnt  Warning cnt   Fun Rt   nloc Rt
------------------------------------------------------------------------------------------
       491       6.6     1.5       43.2       72            3      0.04    0.12

```

Com as refatorações, as três funções mais complexas pararam de gerar warnings:

```sh
==========================================================================================
No thresholds exceeded (cyclomatic_complexity > 5 or length > 1000 or nloc > 1000000 or parameter_count > 100)
==========================================================================================
Total nloc   Avg.NLOC  AvgCCN  Avg.token   Fun Cnt  Warning cnt   Fun Rt   nloc Rt
------------------------------------------------------------------------------------------
       518       6.6     1.5       42.6       76            0      0.00    0.00

```
