"""Parte 3 - Fila de prioridade com heapq, guardando (prioridade, contador, cliente)."""

from __future__ import annotations

import heapq
import itertools
from typing import Iterable, Iterator

from cliente import (
    PRIORIDADES,
    Cliente,
    cabecalho,
    configurar_console,
    gerar_clientes,
    imprimir_clientes,
)


class FilaPrioridadeVaziaError(Exception):
    """Levantada ao tentar consultar ou remover de uma fila de prioridade vazia."""


class FilaPrioridade:
    """Fila de prioridade estavel: o contador desempata a favor de quem chegou antes."""

    def __init__(self, clientes: Iterable[Cliente] | None = None) -> None:
        self._heap: list[tuple[int, int, Cliente]] = []
        self._contador = itertools.count()
        for cliente in clientes or []:
            self.enqueue(cliente)

    def enqueue(self, cliente: Cliente) -> None:
        """Insere o cliente no heap, em O(log n)."""
        if not isinstance(cliente, Cliente):
            raise TypeError("Apenas objetos Cliente podem entrar na fila.")
        ordem_chegada = next(self._contador)
        heapq.heappush(self._heap, (cliente.prioridade, ordem_chegada, cliente))

    def dequeue(self) -> Cliente:
        """Remove e devolve o cliente de maior prioridade (menor valor), em O(log n)."""
        if self.empty():
            raise FilaPrioridadeVaziaError("Nao ha clientes aguardando atendimento.")
        _, _, cliente = heapq.heappop(self._heap)
        return cliente

    def head(self) -> Cliente:
        """Consulta a raiz do min-heap, que e sempre o proximo a ser atendido."""
        if self.empty():
            raise FilaPrioridadeVaziaError("Nao ha clientes aguardando atendimento.")
        return self._heap[0][2]

    def size(self) -> int:
        """Quantidade de clientes aguardando."""
        return len(self._heap)

    def empty(self) -> bool:
        """Diz se a fila esta vazia."""
        return not self._heap

    def listar(self) -> list[Cliente]:
        """Ordem real de atendimento, obtida esvaziando uma copia do heap com heappop."""
        copia = list(self._heap)
        ordenada: list[Cliente] = []
        while copia:
            ordenada.append(heapq.heappop(copia)[2])
        return ordenada

    def heap_interno(self) -> list[str]:
        """Senhas na ordem fisica do vetor que representa o heap."""
        return [f"({p}, {ordem}, {c.senha})" for p, ordem, c in self._heap]

    def contagem_por_prioridade(self) -> dict[int, int]:
        """Quantos clientes aguardam em cada classe de prioridade."""
        contagem = {prioridade: 0 for prioridade in PRIORIDADES}
        for prioridade, _, _ in self._heap:
            contagem[prioridade] += 1
        return contagem

    def __len__(self) -> int:
        return self.size()

    def __iter__(self) -> Iterator[Cliente]:
        return iter(self.listar())

    def __repr__(self) -> str:
        return f"FilaPrioridade(size={self.size()})"


def demonstrar() -> None:
    """Mostra a ordem por prioridade e o desempate pela ordem de chegada."""
    cabecalho("PARTE 3 - FILA DE PRIORIDADE (heapq)")

    prioridades = [3, 3, 2, 1, 3, 2, 1, 3, 2, 1]
    clientes = gerar_clientes(10, prioridades=prioridades, semente=11)

    print("\n>> Ordem de CHEGADA dos clientes:")
    imprimir_clientes(clientes)

    fila = FilaPrioridade()
    for cliente in clientes:
        fila.enqueue(cliente)

    print("\n>> Conteudo do heap na ordem fisica do vetor (prioridade, chegada, senha):")
    print(f"   {fila.heap_interno()}")
    print("   Repare que essa NAO e a ordem de atendimento: o heap so garante que a")
    print("   raiz (indice 0) e o menor elemento.")

    print("\n>> Estado da fila")
    print(f"   size()  = {fila.size()}")
    print(f"   empty() = {fila.empty()}")
    print(f"   head()  = {fila.head()}")
    print(f"   por prioridade = {fila.contagem_por_prioridade()}")

    print("\n>> Atendimento com dequeue() (menor prioridade numerica primeiro):\n")
    ordem: list[Cliente] = []
    while not fila.empty():
        atendido = fila.dequeue()
        ordem.append(atendido)
        print(f"   dequeue -> {atendido}   (restam {fila.size()})")

    print("\n>> Verificacao 1: as prioridades saem em ordem nao decrescente?")
    sequencia = [c.prioridade for c in ordem]
    ok_prioridade = sequencia == sorted(sequencia)
    print(f"   Prioridades na saida: {sequencia}")
    print(f"   RESULTADO: {'OK' if ok_prioridade else 'FALHOU'}")

    print("\n>> Verificacao 2: dentro da mesma prioridade, vale a ordem de chegada (FIFO)?")
    chegada = {cliente.senha: posicao for posicao, cliente in enumerate(clientes)}
    ok_estabilidade = True
    for prioridade in sorted(PRIORIDADES):
        grupo = [c.senha for c in ordem if c.prioridade == prioridade]
        esperado = [c.senha for c in clientes if c.prioridade == prioridade]
        estavel = grupo == esperado
        ok_estabilidade = ok_estabilidade and estavel
        posicoes = [chegada[s] + 1 for s in grupo]
        print(
            f"   Prioridade {prioridade} ({PRIORIDADES[prioridade]:<12}): {grupo} "
            f"-> chegadas {posicoes}  {'OK' if estavel else 'FALHOU'}"
        )
    print(f"   RESULTADO: {'OK - fila de prioridade estavel' if ok_estabilidade else 'FALHOU'}")

    print("\n>> Tentando atender com a fila vazia:")
    try:
        fila.dequeue()
    except FilaPrioridadeVaziaError as erro:
        print(f"   FilaPrioridadeVaziaError: {erro}")


if __name__ == "__main__":
    configurar_console()
    demonstrar()
