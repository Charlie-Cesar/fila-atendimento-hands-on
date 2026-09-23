# Sistema Inteligente de Atendimento

Este é o hands-on de filas da disciplina. A ideia foi montar uma central de atendimento em
Python e fazer o mesmo grupo de clientes passar por três estruturas diferentes: a fila
clássica (FIFO), a fila circular e a fila de prioridade feita com `heapq`. No fim dá para
comparar quem seria chamado primeiro em cada caso e o que cada escolha custa.

Cada cliente tem nome, senha e uma prioridade de 1 a 3, sendo 1 emergência, 2 prioritário e
3 atendimento normal.

Usei só a biblioteca padrão do Python, então não tem nada para instalar.

**Disciplina:** Estruturas de Dados II · **Professor(a):** Karla Roberto Sartin

---

## Estrutura do repositório

```
fila-atendimento-hands-on/
├── cliente.py             # Modelo de dados (Cliente) + gerador automático de clientes
├── fila_classica.py       # Parte 1 - fila FIFO
├── fila_circular.py       # Parte 2 - fila circular com capacidade 5
├── fila_prioridade.py     # Parte 3 - fila de prioridade com heapq
├── desafio_final.py       # Desafio final - 20 clientes nas três estruturas + comparação
├── main.py                # Bônus - menu interativo
├── testes.py              # 17 testes automatizados
├── saidas/                # A saída de cada programa, salva como evidência
│   ├── parte1_fila_classica.txt
│   ├── parte2_fila_circular.txt
│   ├── parte3_fila_prioridade.txt
│   ├── desafio_final.txt
│   ├── menu_interativo.txt
│   └── testes.txt
└── README.md
```

---

## Como executar

Precisa de Python 3.10 ou mais novo, porque usei anotações como `int | None` e
`list[Cliente]`.

```bash
git clone https://github.com/Charlie-Cesar/fila-atendimento-hands-on.git
cd fila-atendimento-hands-on
```

Cada parte roda sozinha:

| Objetivo | Comando |
| --- | --- |
| Parte 1, fila clássica com 10 clientes | `python fila_classica.py` |
| Parte 2, fila circular de capacidade 5 | `python fila_circular.py` |
| Parte 3, fila de prioridade | `python fila_prioridade.py` |
| Desafio final, 20 clientes e comparação | `python desafio_final.py` |
| Menu interativo (bônus) | `python main.py` |
| Testes automatizados | `python testes.py` |

Se os acentos saírem quebrados no terminal do Windows, vale tentar com `py -3`. De todo
jeito os programas já forçam UTF-8 na saída pela `configurar_console()`.

---

## O modelo de cliente

As três filas trabalham com o mesmo objeto, que está em `cliente.py`:

```python
@dataclass(frozen=True)
class Cliente:
    nome: str        # identificação da pessoa
    senha: str       # ficha do totem: E001, P004, N012...
    prioridade: int  # 1 = Emergência | 2 = Prioritário | 3 = Normal
```

A senha é montada juntando a letra da classe (`E`, `P` ou `N`) com um número sequencial.
Isso ajudou bastante na hora de ler os logs, porque a prioridade fica visível só de bater o
olho na senha. Deixei o dataclass como `frozen=True` para ninguém conseguir mudar a
prioridade de um cliente depois que ele já entrou na fila.

Os clientes saem de `gerar_clientes(quantidade, prioridades=None, semente=None)`. Quando
passo uma semente, o sorteio fica travado e a simulação vira reproduzível, ou seja, quem
rodar o código chega exatamente nos mesmos números que estão aqui no README.

---

## Parte 1: fila clássica (FIFO)

Arquivo: [`fila_classica.py`](fila_classica.py)

A classe `Fila` tem as cinco operações que o enunciado pede:

| Operação | O que faz | Custo |
| --- | --- | --- |
| `enqueue(cliente)` | insere no fim da fila | O(1) |
| `dequeue()` | remove e devolve quem está no início | O(1) |
| `head()` | mostra o próximo sem remover | O(1) |
| `size()` | quantos clientes estão na fila | O(1) |
| `empty()` | diz se a fila está vazia | O(1) |

Fora essas, criei `tail()` e `listar()`, que ajudam na hora de imprimir o estado e de
escrever os testes.

Por dentro preferi `collections.deque` a uma lista comum. Numa lista, `lista.pop(0)` custa
O(n), porque todo mundo precisa andar uma casa para trás toda vez que alguém é atendido. O
`deque` remove do início em O(1). Também achei melhor levantar `FilaVaziaError` quando
tentam atender uma fila vazia, em vez de devolver `None` e deixar o erro estourar lá na
frente, longe da causa.

Rodando `python fila_classica.py` (a saída inteira está em [`saidas/parte1_fila_classica.txt`](saidas/parte1_fila_classica.txt)):

```
>> Ordem de chegada (cadastro):
    1º  P001 | Elisa Prado          | 2 - Prioritário
    2º  N002 | Sofia Cardoso        | 3 - Normal
    3º  P003 | Caio Estevão         | 2 - Prioritário
    4º  E004 | Zeca Almeida         | 1 - Emergência
   ...
   10º  N010 | Olivia Tavares       | 3 - Normal

>> Conferência: a ordem de atendimento é igual à ordem de chegada?
   Chegada......: ['P001', 'N002', 'P003', 'E004', 'E005', 'P006', 'E007', 'P008', 'P009', 'N010']
   Atendimento..: ['P001', 'N002', 'P003', 'E004', 'E005', 'P006', 'E007', 'P008', 'P009', 'N010']
   RESULTADO....: IGUAIS -> comportamento FIFO confirmado
```

Repare no `E004`. É uma emergência e mesmo assim foi atendido em quarto lugar, porque a fila
clássica simplesmente não olha para a prioridade.

---

## Parte 2: fila circular (capacidade 5)

Arquivo: [`fila_circular.py`](fila_circular.py)

Essa foi a parte que deu mais trabalho para acertar. O vetor tem tamanho fixo e os dois
índices dão a volta com aritmética modular:

```python
rear  = (rear  + 1) % capacidade   # ao inserir
front = (front + 1) % capacidade   # ao remover
```

Além das operações básicas a classe tem `full()`, `indices()` e `desenhar()`. Esse último
imprime o vetor interno marcando onde estão `front` e `rear`, e foi o que permitiu mostrar
passo a passo o que acontece durante a execução.

Tem um detalhe que só fica claro implementando: só com `front` e `rear` não dá para saber se
a fila está cheia ou vazia, porque nos dois casos os índices podem parar em posições
equivalentes. Dá para resolver sacrificando um slot do vetor ou guardando um contador.
Escolhi o contador `_total`, que resolve sem desperdiçar espaço.

### A reutilização das posições

Com cinco clientes o vetor lota, ocupando os slots de 0 a 4:

```
   indice :    [0]       [1]       [2]       [3]       [4]
   vetor  :    N001      P002      N003      N004      E005
              ^front                                  ^rear
            front=0  rear=4  size=5/5  (CHEIA)

>> A fila esta CHEIA. Tentando inserir um 6o cliente:
   FilaCheiaError: Fila circular cheia (5/5). O cliente E006 nao pode ser inserido
   ate que alguem seja atendido.
```

Depois de dois `dequeue()`, que liberam os slots 0 e 1, os próximos clientes ocupam
justamente essas posições. O `rear` vai de 4 para 0 e depois para 1, que é a volta
acontecendo na prática:

```
   enqueue(E006) -> Vinicius Lopes   [rear agora e 0]
   indice :    [0]       [1]       [2]       [3]       [4]
   vetor  :    E006      ----      N003      N004      E005
              ^rear               ^front
            front=2  rear=0  size=4/5  (parcial)

   enqueue(N007) -> Tiago Barros   [rear agora e 1]
   indice :    [0]       [1]       [2]       [3]       [4]
   vetor  :    E006      N007      N003      N004      E005
                        ^rear     ^front
            front=2  rear=1  size=5/5  (CHEIA)
```

Fisicamente os dados ficam fora de ordem no vetor, mas a ordem lógica continua certa, porque
a leitura sempre começa no `front` e anda de forma circular:

```
>> Ordem de atendimento atual (percurso circular a partir de front):
   1o  N003 | Rafael Moreira       | 3 - Normal
   2o  N004 | Elisa Prado          | 3 - Normal
   3o  E005 | Lucas Ferreira       | 1 - Emergência
   4o  E006 | Vinicius Lopes       | 1 - Emergência
   5o  N007 | Tiago Barros         | 3 - Normal
```

A execução completa está em [`saidas/parte2_fila_circular.txt`](saidas/parte2_fila_circular.txt).

---

## Parte 3: fila de prioridade com heapq

Arquivo: [`fila_prioridade.py`](fila_prioridade.py)

Cada cliente entra no heap como a tupla que o enunciado sugere:

```python
heapq.heappush(self._heap, (cliente.prioridade, ordem_chegada, cliente))
```

A prioridade é o critério principal, já que o `heapq` é um min-heap e o menor valor sai
primeiro. O `ordem_chegada` vem de um `itertools.count()` e serve de desempate. O cliente em
si é só o dado que vai junto.

Esse contador parece um detalhe bobo, mas resolve dois problemas de uma vez.

O primeiro é a estabilidade. O heap sozinho não garante ordem de chegada entre clientes de
mesma prioridade, então dois "prioridade 2" poderiam sair trocados. Com o contador, o
desempate é sempre a favor de quem chegou antes.

O segundo só aparece quando o programa quebra. Se os dois primeiros campos da tupla empatam,
o Python passa a comparar o terceiro, e `Cliente` não define `<`, o que levantaria
`TypeError` no meio de uma inserção. Como o contador nunca se repete, a comparação sempre
para nele e o objeto `Cliente` nunca chega a ser comparado. O teste 15 existe só para
garantir isso.

Vale comentar o `listar()` também. O heap é uma árvore só parcialmente ordenada, então ler o
vetor interno na ordem física não dá a ordem de atendimento. Para devolver a ordem real, o
método trabalha em cima de uma cópia e vai esvaziando com `heappop`.

Rodando `python fila_prioridade.py` (completo em [`saidas/parte3_fila_prioridade.txt`](saidas/parte3_fila_prioridade.txt)):

```
>> Conteudo do heap na ordem fisica do vetor (prioridade, chegada, senha):
   ['(1, 3, E004)', '(1, 9, E010)', '(1, 6, E007)', '(2, 8, P009)', '(2, 2, P003)',
    '(3, 0, N001)', '(2, 5, P006)', '(3, 7, N008)', '(3, 1, N002)', '(3, 4, N005)']
   Repare que essa NAO e a ordem de atendimento: o heap so garante que a
   raiz (indice 0) e o menor elemento.

>> Verificacao 1: as prioridades saem em ordem nao decrescente?
   Prioridades na saida: [1, 1, 1, 2, 2, 2, 3, 3, 3, 3]
   RESULTADO: OK

>> Verificacao 2: dentro da mesma prioridade, vale a ordem de chegada (FIFO)?
   Prioridade 1 (Emergência  ): ['E004', 'E007', 'E010'] -> chegadas [4, 7, 10]  OK
   Prioridade 2 (Prioritário ): ['P003', 'P006', 'P009'] -> chegadas [3, 6, 9]  OK
   Prioridade 3 (Normal      ): ['N001', 'N002', 'N005', 'N008'] -> chegadas [1, 2, 5, 8]  OK
   RESULTADO: OK - fila de prioridade estavel
```

---

## Desafio final: 20 clientes nas três estruturas

Arquivo: [`desafio_final.py`](desafio_final.py) · Saída completa: [`saidas/desafio_final.txt`](saidas/desafio_final.txt)

O programa gera 20 clientes com prioridades sorteadas de 1 a 3. Travei a semente em `2025`,
então o resultado é sempre o mesmo: 9 emergências, 4 prioritários e 7 normais.

São cinco etapas, nessa ordem: a chegada dos clientes, o atendimento pela fila clássica, o
comportamento da fila circular, o atendimento pela fila de prioridade e a comparação.

### A fila circular com mais clientes do que lugares

Como a capacidade é 5 e os clientes são 20, tratei a fila circular como uma sala de espera
de verdade. Quando ela enche, o guichê precisa chamar alguém antes de a próxima pessoa
conseguir entrar:

```
   evento                     vetor interno                    indices
   ------------------------------------------------------------------------------
   entra E005                 [E001][P002][E003][N004][E005]   front=0  rear=4  size=5/5
   FILA CHEIA (N006 aguarda)  [E001][P002][E003][N004][E005]   front=0  rear=4  size=5/5
   atende E001 (libera slot)  [----][P002][E003][N004][E005]   front=1  rear=4  size=4/5
   entra N006                 [N006][P002][E003][N004][E005]   front=1  rear=0  size=5/5 <- slot reutilizado
   FILA CHEIA (N007 aguarda)  [N006][P002][E003][N004][E005]   front=1  rear=0  size=5/5
   atende P002 (libera slot)  [N006][----][E003][N004][E005]   front=2  rear=0  size=4/5
   entra N007                 [N006][N007][E003][N004][E005]   front=2  rear=1  size=5/5 <- slot reutilizado
```

No total a sala ficou cheia 15 vezes e os cinco slots foram reaproveitados. Mesmo assim, a
ordem final de saída é igualzinha à da fila clássica.

### Comparando os três resultados

A tabela mostra em que posição cada cliente foi atendido em cada estrutura. É um trecho, a
dos 20 está na saída completa. A coluna "ganho" é quantas posições a pessoa subiu ao trocar
a fila clássica pela de prioridade:

| senha | nome | prio | chegada | FIFO | circular | prioridade | ganho |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E001 | Rafael Moreira | 1 | 1 | 1 | 1 | 1 | 0 |
| P002 | Carla Menezes | 2 | 2 | 2 | 2 | 10 | -8 |
| E003 | Ursula Pinto | 1 | 3 | 3 | 3 | 2 | +1 |
| N004 | Beatriz Siqueira | 3 | 4 | 4 | 4 | 14 | -10 |
| E008 | Ana Souza | 1 | 8 | 8 | 8 | 4 | +4 |
| N012 | Heitor Campos | 3 | 12 | 12 | 12 | 17 | -5 |
| P015 | Xênia Ribeiro | 2 | 15 | 15 | 15 | 11 | +4 |
| E019 | Diego Ramos | 1 | 19 | 19 | 19 | 9 | +10 |
| N020 | Gabriela Rocha | 3 | 20 | 20 | 20 | 20 | 0 |

Juntando por classe, a espera média em número de posições fica assim:

| Prioridade | Qtd | FIFO | Circular | Prioridade | Ganho |
| --- | --- | --- | --- | --- | --- |
| 1, Emergência | 9 | 8.8 | 8.8 | 5.0 | +3.8 |
| 2, Prioritário | 4 | 12.5 | 12.5 | 11.5 | +1.0 |
| 3, Normal | 7 | 11.6 | 11.6 | 17.0 | -5.4 |

O caso mais gritante é o do `E019`. Ele chegou em décimo nono e, na fila clássica, seria
atendido exatamente nessa posição, mesmo sendo emergência. Na fila de prioridade ele é o
nono, dez lugares à frente.

Olhando só as oito primeiras senhas chamadas por cada estrutura a diferença salta:

```
Chegada......: ['E001', 'P002', 'E003', 'N004', 'E005', 'N006', 'N007', 'E008']
FIFO.........: ['E001', 'P002', 'E003', 'N004', 'E005', 'N006', 'N007', 'E008']
Circular.....: ['E001', 'P002', 'E003', 'N004', 'E005', 'N006', 'N007', 'E008']
Prioridade...: ['E001', 'E003', 'E005', 'E008', 'E009', 'E010', 'E011', 'E013']
```

O que dá para tirar desses números:

A fila clássica entrega exatamente a ordem de chegada. É a mais justa no critério "quem
chegou primeiro", só que ignora a gravidade do caso.

A fila circular deu a mesma ordem da clássica, e esse é o ponto principal dela: não reordena
nada. O que muda é a capacidade. Ela limita quantas pessoas esperam ao mesmo tempo e, em
troca, usa memória fixa e reaproveita as posições liberadas.

A fila de prioridade é a única que muda a ordem de saída. As emergências caem de 8.8 para
5.0 posições de espera média e os prioritários ganham uma posição. Só que essa conta é paga
pelos clientes normais, que sobem de 11.6 para 17.0.

---

## Menu interativo (bônus)

Arquivo: [`main.py`](main.py) · Saída de exemplo: [`saidas/menu_interativo.txt`](saidas/menu_interativo.txt)

No menu as três estruturas funcionam ao mesmo tempo, com os mesmos clientes. Achei que
assim ficava mais fácil ver as três discordando a cada operação:

```
+----------------------------------------------------------------+
|       SISTEMA INTELIGENTE DE ATENDIMENTO - MENU                |
+----------------------------------------------------------------+
| 1 - Inserir cliente                                            |
| 2 - Atender proximo (fila classica - FIFO)                     |
| 3 - Atender proximo (fila de prioridade)                       |
| 4 - Atender proximo (fila circular)                            |
| 5 - Consultar proximo de cada fila (head)                      |
| 6 - Visualizar estado atual do sistema                         |
| 7 - Carregar clientes de exemplo                               |
| 8 - Executar a simulacao do desafio final (20 clientes)        |
| 0 - Sair                                                       |
+----------------------------------------------------------------+
```

Um exemplo com dois clientes cadastrados, em que o `N001` (normal) chegou antes do `E002`
(emergência). A opção 5 mostra as filas discordando:

```
   Fila classica    : N001 | Maria Silva          | 3 - Normal
   Fila circular    : N001 | Maria Silva          | 3 - Normal
   Fila de prioridade: E002 | Jose Pereira         | 1 - Emergência
```

Quando a sala de espera está cheia o sistema avisa e mantém o cliente nas outras duas filas,
em vez de perder o cadastro.

---

## Testes

Arquivo: [`testes.py`](testes.py) · Saída: [`saidas/testes.txt`](saidas/testes.txt)

São 17 testes escritos só com `assert` e um runner pequeno, sem pytest:

```bash
python testes.py
```

```
   [ 1] OK      Cliente: senha e gerada com a letra da prioridade
   [ 2] OK      Cliente: prioridade fora de 1..3 levanta ValueError
   [ 3] OK      Fila: enqueue/dequeue respeitam a ordem de chegada (FIFO)
   [ 4] OK      Fila: size(), empty() e head() refletem o estado atual
   [ 5] OK      Fila: dequeue()/head() em fila vazia levantam FilaVaziaError
   [ 6] OK      Fila: aceita apenas objetos Cliente
   [ 7] OK      FilaCircular: enqueue faz rear avancar e dequeue faz front avancar
   [ 8] OK      FilaCircular: inserir na fila cheia levanta FilaCheiaError sem perder dados
   [ 9] OK      FilaCircular: posicao liberada e reutilizada (rear da a volta)
   [10] OK      FilaCircular: dequeue em fila vazia levanta FilaCircularVaziaError
   [11] OK      FilaCircular: ciclo completo de insercoes e remocoes mantem a ordem FIFO
   [12] OK      FilaPrioridade: menor valor de prioridade e atendido primeiro
   [13] OK      FilaPrioridade: empate de prioridade preserva a ordem de chegada
   [14] OK      FilaPrioridade: head() aponta para a raiz do heap sem remover
   [15] OK      FilaPrioridade: clientes distintos com mesma prioridade nao quebram a comparacao
   [16] OK      FilaPrioridade: dequeue em fila vazia levanta FilaPrioridadeVaziaError
   [17] OK      Integracao: as tres estruturas processam os mesmos 20 clientes

------------------------------------------------------------------------
   RESULTADO: 17/17 testes passaram. Tudo certo!
------------------------------------------------------------------------
```

---

## Relatório e análise

### 1. Por que a ordem de atendimento da fila de prioridade pode ser diferente da ordem da fila clássica?

Porque as duas ordenam por critérios diferentes.

A fila clássica usa um critério só, que é o instante da chegada. Quem entra primeiro sai
primeiro, e nenhuma característica do cliente interfere nisso. Como a inserção é sempre no
fim e a remoção sempre no início, a ordem nunca muda depois que a pessoa entrou.

A fila de prioridade ordena pela chave `(prioridade, ordem de chegada)`. A chegada deixa de
ser o critério principal e vira só o desempate. Como o `heapq` é um min-heap, quem tem o
menor valor de prioridade sobe para a raiz e é o próximo a sair, mesmo tendo chegado por
último. E a cada `heappush` a árvore se reorganiza, ou seja, a fila é reordenada a cada
inserção nova.

As duas ordens só batem em dois casos: quando todos os clientes têm a mesma prioridade, e aí
o desempate por chegada faz a fila de prioridade virar uma FIFO comum, ou quando as
prioridades por coincidência já chegam em ordem crescente.

Na simulação do desafio final a diferença é grande. O `E019` chegou em décimo nono e é
atendido em nono, enquanto o `N004` chegou em quarto e cai para décimo quarto. No fundo a
fila clássica responde "quem chegou antes?" e a de prioridade responde "quem precisa mais?".

### 2. Em quais situações reais uma fila de prioridade seria mais adequada?

Sempre que esperar custar coisas diferentes para pessoas diferentes, ou seja, quando atrasar
um caso específico gera um prejuízo muito maior que atrasar os outros. Alguns exemplos:

- Pronto-socorro, com triagem por gravidade. É o caso do enunciado: um infarto não pode
  esperar atrás de vinte casos de resfriado.
- Atendimento com prioridade garantida por lei, como idosos, gestantes e pessoas com
  deficiência em bancos e repartições públicas (Lei 10.048/2000).
- Suporte técnico com SLA. Um chamado de "sistema de produção fora do ar" precisa passar na
  frente de uma dúvida sobre relatório, mesmo que a dúvida tenha sido aberta antes.
- Escalonamento de processos no sistema operacional, em que tarefas de tempo real e
  interativas passam na frente das que rodam em lote.
- Roteamento de pacotes em redes com QoS, porque voz e vídeo são sensíveis a latência e um
  download não é.
- Algoritmos como Dijkstra e A*, que sempre expandem o caminho de menor custo, além do
  Huffman e do próprio Heapsort.

Por outro lado, ela é uma má escolha quando a justiça na ordem de chegada é o requisito
principal, tipo o caixa de um supermercado ou uma venda de ingressos. E exige cuidado com a
inanição, o tal do starvation: se emergências continuarem chegando, os clientes de
prioridade 3 podem nunca ser chamados. A solução clássica é o aging, que vai aumentando aos
poucos a prioridade de quem está esperando há muito tempo.

### 3. Quais são as vantagens e limitações de uma fila circular?

A vantagem principal é o reaproveitamento de espaço. A posição que um `dequeue` libera volta
a ser usada, coisa que uma fila linear em vetor não faz. Nela o `front` vai avançando e
deixando um rastro de posições mortas no começo do vetor, mesmo quando a fila está quase
vazia.

Junto com isso vem a memória fixa e previsível. O vetor é alocado uma vez só, não tem
realocação nem crescimento inesperado, o que faz diferença em sistemas embarcados e de tempo
real. As operações também são O(1) de verdade, porque inserir e remover é só aritmética
modular mais uma atribuição, sem precisar deslocar os outros elementos.

Tem ainda uma vantagem menos óbvia, que é o limite de capacidade ficar explícito. Isso
obriga a definir o que fazer quando a fila lota, em vez de deixar a memória crescer sem
controle. É por isso que essa é a estrutura por trás de buffers de áudio e vídeo, ring
buffers de log, filas de teclado e buffers de comunicação serial.

As limitações começam justamente pela capacidade fixa. Errar o dimensionamento significa ou
desperdiçar memória ou recusar clientes, e crescer exige criar um vetor maior e copiar tudo,
o que custa O(n).

Tem também a ambiguidade entre cheia e vazia, já que `front` e `rear` podem coincidir nas
duas situações. Ou se guarda um contador, como o `_total` que usei, ou se abre mão de um slot
do vetor.

E a implementação erra mais fácil que a de uma fila linear. A aritmética modular e os casos
de borda, como esvaziar a fila, dar a volta e reiniciar os índices, são uma fonte clássica de
bug.

Por fim, a fila circular não reordena nada. Continua sendo FIFO e não resolve o problema de
prioridade, o que ficou bem visível no desafio final, em que a ordem de saída dela foi
idêntica à da clássica. E ler o vetor direto confunde, porque os dados só fazem sentido
quando percorridos a partir do `front`.

### 4. O que acontece ao tentar inserir um elemento em uma fila circular cheia?

Acontece um overflow de fila. Não sobrou posição livre, porque `rear + 1` (mod capacidade)
aponta exatamente para o `front`, que está ocupado. O elemento não entra, e é importante que
não entre mesmo: sobrescrever aquele slot apagaria um cliente que ainda nem foi atendido.

No meu código o `enqueue()` checa o `full()` antes de mexer em qualquer índice e levanta uma
exceção explicando o motivo, deixando a fila intacta. O teste 8 confirma isso, conferindo o
`size()` e o conteúdo depois da tentativa:

```python
if self.full():
    raise FilaCheiaError(
        f"Fila circular cheia ({self._total}/{self._capacidade}). "
        f"O cliente {cliente.senha} nao pode ser inserido ate que alguem seja atendido."
    )
```

Na execução aparece assim:

```
>> A fila esta CHEIA. Tentando inserir um 6o cliente:
   FilaCheiaError: Fila circular cheia (5/5). O cliente E006 nao pode ser inserido
   ate que alguem seja atendido.
```

Só depois de um `dequeue()`, que libera um slot e avança o `front`, a inserção passa a ser
possível, e o cliente novo ocupa exatamente a posição reaproveitada.

Rejeitar não é a única política possível, e a escolha depende da aplicação:

| Política | Comportamento | Onde costuma aparecer |
| --- | --- | --- |
| Rejeitar (a que usei) | levanta erro e quem chamou decide o que fazer | filas de atendimento, validação de entrada |
| Sobrescrever o mais antigo | o dado novo substitui o mais velho | ring buffer de logs, telemetria |
| Bloquear e aguardar | a thread espera até liberar espaço | `queue.Queue` entre produtor e consumidor |
| Redimensionar | aloca um vetor maior e copia o conteúdo | filas dinâmicas, que perdem a memória fixa |

No `desafio_final.py` fui de rejeitar e atender: quando a sala enche, o guichê chama o
próximo e só então o cliente entra. Foi assim que apareceram as 15 ocorrências de fila cheia
e o reaproveitamento dos cinco slots.

---

## Resumo comparativo

| Característica | Fila clássica | Fila circular | Fila de prioridade |
| --- | --- | --- | --- |
| Critério de saída | ordem de chegada | ordem de chegada | prioridade, depois chegada |
| Capacidade | dinâmica | fixa (5) | dinâmica |
| `enqueue` | O(1) | O(1) | O(log n) |
| `dequeue` | O(1) | O(1) | O(log n) |
| `head` | O(1) | O(1) | O(1) |
| Memória | cresce conforme a demanda | constante | cresce conforme a demanda |
| Reaproveita posições | não | sim, por aritmética modular | não |
| Risco de inanição | não | não | sim, na prioridade 3 |
| Estrutura interna | `collections.deque` | vetor fixo com `front`, `rear` e `_total` | min-heap do `heapq` |
