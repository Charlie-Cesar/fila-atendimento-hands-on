"""Parte 1 - Fila classica (FIFO): o primeiro que chega e o primeiro a ser atendido."""

from __future__ import annotations

from collections import deque
from typing import Iterable, Iterator

from cliente import Cliente, cabecalho, configurar_console, gerar_clientes, imprimir_clientes


class FilaVaziaError(Exception):
    """Levantada ao tentar consultar ou remover um cliente de uma fila vazia."""


class Fila:
    """Fila FIFO apoiada em collections.deque, que remove do inicio em O(1)."""

    def __init__(self, clientes: Iterable[Cliente] | None = None) -> None:
        self._itens: deque[Cliente] = deque()
        for cliente in clientes or []:
            self.enqueue(cliente)

    def enqueue(self, cliente: Cliente) -> None:
        """Insere um cliente no fim da fila."""
        if not isinstance(cliente, Cliente):
            raise TypeError("Apenas objetos Cliente podem entrar na fila.")
        self._itens.append(cliente)

    def dequeue(self) -> Cliente:
        """Remove e devolve o cliente do inicio da fila."""
        if self.empty():
            raise FilaVaziaError("Não há clientes aguardando atendimento.")
        return self._itens.popleft()

    def head(self) -> Cliente:
        """Consulta, sem remover, o proximo cliente a ser atendido."""
        if self.empty():
            raise FilaVaziaError("Não há clientes aguardando atendimento.")
        return self._itens[0]

    def size(self) -> int:
        """Quantidade de clientes aguardando."""
        return len(self._itens)

    def empty(self) -> bool:
        """Diz se a fila esta vazia."""
        return len(self._itens) == 0

    def tail(self) -> Cliente:
        """Consulta o ultimo cliente que entrou na fila."""
        if self.empty():
            raise FilaVaziaError("Não há clientes aguardando atendimento.")
        return self._itens[-1]

    def listar(self) -> list[Cliente]:
        """Devolve os clientes na ordem em que serao atendidos."""
        return list(self._itens)

    def __len__(self) -> int:
        return self.size()

    def __iter__(self) -> Iterator[Cliente]:
        return iter(self._itens)

    def __repr__(self) -> str:
        return f"Fila(size={self.size()}, head={self._itens[0].senha if self._itens else None})"


def demonstrar(quantidade: int = 10, semente: int = 1) -> None:
    """Cadastra clientes e mostra que a ordem de atendimento e a de chegada."""
    cabecalho("PARTE 1 - FILA CLÁSSICA (FIFO)")

    clientes = gerar_clientes(quantidade, semente=semente)
    fila = Fila()

    print(f"\n>> Cadastrando {quantidade} clientes com enqueue():\n")
    for cliente in clientes:
        fila.enqueue(cliente)
        print(f"   enqueue -> {cliente}   (size = {fila.size()})")

    print(f"\n>> Estado da fila")
    print(f"   empty() = {fila.empty()}")
    print(f"   size()  = {fila.size()}")
    print(f"   head()  = {fila.head()}")
    print(f"   último  = {fila.tail()}")

    print("\n>> Ordem de chegada (cadastro):")
    imprimir_clientes(clientes)

    print("\n>> Atendimento com dequeue() até esvaziar a fila:\n")
    ordem_atendimento: list[Cliente] = []
    while not fila.empty():
        atendido = fila.dequeue()
        ordem_atendimento.append(atendido)
        restantes = fila.head().senha if not fila.empty() else "---"
        print(f"   dequeue -> {atendido}   (restam {fila.size()}, próximo: {restantes})")

    print("\n>> Conferência: a ordem de atendimento é igual à ordem de chegada?")
    print(f"   Chegada......: {[c.senha for c in clientes]}")
    print(f"   Atendimento..: {[c.senha for c in ordem_atendimento]}")
    print(f"   RESULTADO....: {'IGUAIS -> comportamento FIFO confirmado' if ordem_atendimento == clientes else 'DIFERENTES -> erro!'}")

    print("\n>> Tentando atender com a fila vazia:")
    try:
        fila.dequeue()
    except FilaVaziaError as erro:
        print(f"   FilaVaziaError: {erro}")


if __name__ == "__main__":
    configurar_console()
    demonstrar()
