"""Parte 2 - Fila circular: vetor de tamanho fixo com indices que dao a volta."""

from __future__ import annotations

from typing import Iterable, Iterator

from cliente import Cliente, cabecalho, configurar_console, criar_cliente, gerar_clientes

CAPACIDADE_PADRAO = 5


class FilaCheiaError(Exception):
    """Levantada ao tentar inserir um cliente em uma fila circular cheia."""


class FilaCircularVaziaError(Exception):
    """Levantada ao tentar consultar ou remover de uma fila circular vazia."""


class FilaCircular:
    """Fila circular de capacidade fixa; o contador _total distingue cheia de vazia."""

    def __init__(
        self,
        capacidade: int = CAPACIDADE_PADRAO,
        clientes: Iterable[Cliente] | None = None,
    ) -> None:
        if capacidade < 1:
            raise ValueError("A capacidade deve ser de pelo menos 1 cliente.")
        self._capacidade = capacidade
        self._itens: list[Cliente | None] = [None] * capacidade
        self._front = 0
        self._rear = -1
        self._total = 0
        for cliente in clientes or []:
            self.enqueue(cliente)

    @property
    def capacidade(self) -> int:
        return self._capacidade

    @property
    def front(self) -> int:
        return self._front

    @property
    def rear(self) -> int:
        return self._rear

    def enqueue(self, cliente: Cliente) -> None:
        """Insere um cliente na proxima posicao livre; erro se a fila estiver cheia."""
        if not isinstance(cliente, Cliente):
            raise TypeError("Apenas objetos Cliente podem entrar na fila.")
        if self.full():
            raise FilaCheiaError(
                f"Fila circular cheia ({self._total}/{self._capacidade}). O cliente "
                f"{cliente.senha} nao pode ser inserido ate que alguem seja atendido."
            )
        self._rear = (self._rear + 1) % self._capacidade
        self._itens[self._rear] = cliente
        self._total += 1

    def dequeue(self) -> Cliente:
        """Atende o cliente da posicao front e libera aquele slot para reutilizacao."""
        if self.empty():
            raise FilaCircularVaziaError("Fila circular vazia: nao ha quem atender.")
        cliente = self._itens[self._front]
        self._itens[self._front] = None
        self._front = (self._front + 1) % self._capacidade
        self._total -= 1
        if self._total == 0:
            self._front, self._rear = 0, -1
        return cliente

    def head(self) -> Cliente:
        """Consulta, sem remover, o cliente da posicao front."""
        if self.empty():
            raise FilaCircularVaziaError("Fila circular vazia: nao ha quem atender.")
        return self._itens[self._front]

    def size(self) -> int:
        """Quantidade de clientes armazenados no momento."""
        return self._total

    def empty(self) -> bool:
        """Diz se nenhum slot esta ocupado."""
        return self._total == 0

    def full(self) -> bool:
        """Diz se todos os slots estao ocupados."""
        return self._total == self._capacidade

    def listar(self) -> list[Cliente]:
        """Clientes na ordem de atendimento, percorrendo o vetor de forma circular."""
        return [
            self._itens[(self._front + passo) % self._capacidade]
            for passo in range(self._total)
        ]

    def indices(self) -> str:
        """Resumo textual dos indices de controle."""
        return f"front={self._front}  rear={self._rear}  size={self._total}/{self._capacidade}"

    def vetor_resumido(self) -> str:
        """Versao compacta do vetor interno, em uma unica linha."""
        celulas = [
            (item.senha if item is not None else "----") for item in self._itens
        ]
        return "[" + "][".join(celulas) + "]"

    def desenhar(self, recuo: str = "   ") -> str:
        """Desenha o vetor interno marcando onde estao front e rear."""
        largura = 10
        rotulo = " " * 9
        linha_idx = recuo + "indice : " + "".join(
            f"[{i}]".center(largura) for i in range(self._capacidade)
        )
        linha_val = recuo + "vetor  : " + "".join(
            (item.senha if item is not None else "----").center(largura)
            for item in self._itens
        )
        marcadores: list[str] = []
        for i in range(self._capacidade):
            if self._total and i == self._front and i == self._rear:
                marcadores.append("^F=R".center(largura))
            elif self._total and i == self._front:
                marcadores.append("^front".center(largura))
            elif self._total and i == self._rear:
                marcadores.append("^rear".center(largura))
            else:
                marcadores.append(" " * largura)
        linha_mark = (recuo + rotulo + "".join(marcadores)).rstrip()
        estado = "CHEIA" if self.full() else ("VAZIA" if self.empty() else "parcial")
        linha_est = f"{recuo}{rotulo}{self.indices()}  ({estado})"
        return "\n".join([linha_idx, linha_val, linha_mark, linha_est])

    def __len__(self) -> int:
        return self._total

    def __iter__(self) -> Iterator[Cliente]:
        return iter(self.listar())

    def __repr__(self) -> str:
        return f"FilaCircular(capacidade={self._capacidade}, {self.indices()})"


def demonstrar() -> None:
    """Enche a fila, mostra o erro de fila cheia e o reuso das posicoes liberadas."""
    cabecalho("PARTE 2 - FILA CIRCULAR (CAPACIDADE 5)")

    fila = FilaCircular(capacidade=5)
    clientes = gerar_clientes(5, semente=3)

    print("\n>> Fila recem-criada (vazia):")
    print(fila.desenhar())

    print("\n>> Inserindo 5 clientes ate encher o vetor:\n")
    for cliente in clientes:
        fila.enqueue(cliente)
        print(f"   enqueue({cliente.senha}) -> {cliente.nome}")
        print(fila.desenhar())
        print()

    print(">> A fila esta CHEIA. Tentando inserir um 6o cliente:")
    try:
        fila.enqueue(criar_cliente("Vinicius Lopes", 1, 6))
    except FilaCheiaError as erro:
        print(f"   FilaCheiaError: {erro}")

    print("\n>> Atendendo 2 clientes (dequeue) para liberar as posicoes 0 e 1:\n")
    for _ in range(2):
        atendido = fila.dequeue()
        print(f"   dequeue() -> {atendido}")
        print(fila.desenhar())
        print()

    print(">> REUTILIZACAO DAS POSICOES: inserindo 2 novos clientes.")
    print("   Observe rear dar a volta (4 -> 0 -> 1) e ocupar slots ja usados antes.\n")
    for nome, prioridade, sequencial in [("Vinicius Lopes", 1, 6), ("Tiago Barros", 3, 7)]:
        novo = criar_cliente(nome, prioridade, sequencial)
        fila.enqueue(novo)
        print(f"   enqueue({novo.senha}) -> {novo.nome}   [rear agora e {fila.rear}]")
        print(fila.desenhar())
        print()

    print(">> Ordem de atendimento atual (percurso circular a partir de front):")
    for posicao, cliente in enumerate(fila.listar(), start=1):
        print(f"   {posicao}o  {cliente}")

    print("\n>> Esvaziando a fila por completo:\n")
    while not fila.empty():
        atendido = fila.dequeue()
        print(f"   dequeue() -> {atendido.senha}  |  {fila.indices()}")

    print("\n>> Fila vazia novamente (indices reiniciados):")
    print(fila.desenhar())

    print("\n>> Tentando atender com a fila vazia:")
    try:
        fila.dequeue()
    except FilaCircularVaziaError as erro:
        print(f"   FilaCircularVaziaError: {erro}")


if __name__ == "__main__":
    configurar_console()
    demonstrar()
