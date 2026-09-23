"""Testes automatizados das tres estruturas, usando apenas assert e um runner simples."""

from __future__ import annotations

import sys
import traceback
from collections.abc import Callable

from cliente import Cliente, cabecalho, configurar_console, criar_cliente, gerar_clientes
from fila_circular import FilaCheiaError, FilaCircular, FilaCircularVaziaError
from fila_classica import Fila, FilaVaziaError
from fila_prioridade import FilaPrioridade, FilaPrioridadeVaziaError

TESTES: list[tuple[str, Callable[[], None]]] = []


def teste(descricao: str):
    """Decorator que registra uma funcao na lista de testes."""

    def registrar(funcao: Callable[[], None]) -> Callable[[], None]:
        TESTES.append((descricao, funcao))
        return funcao

    return registrar


@teste("Cliente: senha e gerada com a letra da prioridade")
def test_senha() -> None:
    assert criar_cliente("Ana", 1, 7).senha == "E007"
    assert criar_cliente("Bia", 2, 12).senha == "P012"
    assert criar_cliente("Caio", 3, 3).senha == "N003"


@teste("Cliente: prioridade fora de 1..3 levanta ValueError")
def test_prioridade_invalida() -> None:
    try:
        Cliente(nome="Zé", senha="X001", prioridade=4)
    except ValueError:
        return
    raise AssertionError("Deveria ter levantado ValueError para prioridade 4.")


@teste("Fila: enqueue/dequeue respeitam a ordem de chegada (FIFO)")
def test_fifo() -> None:
    clientes = gerar_clientes(10, semente=1)
    fila = Fila(clientes)
    atendidos = [fila.dequeue() for _ in range(10)]
    assert atendidos == clientes, "A ordem de saida deveria ser igual a de entrada."


@teste("Fila: size(), empty() e head() refletem o estado atual")
def test_estado_fila() -> None:
    fila = Fila()
    assert fila.empty() is True and fila.size() == 0
    clientes = gerar_clientes(3, semente=5)
    for cliente in clientes:
        fila.enqueue(cliente)
    assert fila.size() == 3
    assert fila.empty() is False
    assert fila.head() == clientes[0], "head() deve devolver o primeiro que chegou."
    assert fila.tail() == clientes[-1], "tail() deve devolver o ultimo que chegou."
    assert fila.head() == clientes[0], "head() nao pode remover o cliente."
    assert fila.size() == 3


@teste("Fila: dequeue()/head() em fila vazia levantam FilaVaziaError")
def test_fila_vazia() -> None:
    fila = Fila()
    for operacao in (fila.dequeue, fila.head):
        try:
            operacao()
        except FilaVaziaError:
            continue
        raise AssertionError(f"{operacao.__name__} deveria ter levantado FilaVaziaError.")


@teste("Fila: aceita apenas objetos Cliente")
def test_tipo_invalido() -> None:
    try:
        Fila().enqueue("Maria")
    except TypeError:
        return
    raise AssertionError("Deveria ter levantado TypeError.")


@teste("FilaCircular: enqueue faz rear avancar e dequeue faz front avancar")
def test_indices_circular() -> None:
    fila = FilaCircular(capacidade=5)
    assert (fila.front, fila.rear, fila.size()) == (0, -1, 0)
    clientes = gerar_clientes(3, semente=2)
    for esperado, cliente in enumerate(clientes):
        fila.enqueue(cliente)
        assert fila.rear == esperado, f"rear deveria ser {esperado}."
        assert fila.front == 0
    fila.dequeue()
    assert fila.front == 1, "front deveria avancar apos o dequeue."
    assert fila.size() == 2


@teste("FilaCircular: inserir na fila cheia levanta FilaCheiaError sem perder dados")
def test_fila_cheia() -> None:
    clientes = gerar_clientes(6, semente=4)
    fila = FilaCircular(capacidade=5, clientes=clientes[:5])
    assert fila.full() is True
    estado_antes = fila.listar()
    try:
        fila.enqueue(clientes[5])
    except FilaCheiaError:
        assert fila.size() == 5, "A fila nao pode crescer alem da capacidade."
        assert fila.listar() == estado_antes, "Os clientes ja enfileirados devem continuar intactos."
        return
    raise AssertionError("Deveria ter levantado FilaCheiaError.")


@teste("FilaCircular: posicao liberada e reutilizada (rear da a volta)")
def test_reutilizacao() -> None:
    clientes = gerar_clientes(7, semente=6)
    fila = FilaCircular(capacidade=5, clientes=clientes[:5])
    assert fila.rear == 4

    fila.dequeue()
    assert fila.front == 1
    fila.enqueue(clientes[5])
    assert fila.rear == 0, "rear deveria ter voltado ao slot 0 (aritmetica modular)."

    fila.dequeue()
    fila.enqueue(clientes[6])
    assert fila.rear == 1, "rear deveria ocupar o slot 1, tambem reaproveitado."
    assert fila.size() == 5
    assert fila.listar() == clientes[2:7], "A ordem FIFO deve ser mantida na volta."


@teste("FilaCircular: dequeue em fila vazia levanta FilaCircularVaziaError")
def test_circular_vazia() -> None:
    fila = FilaCircular(capacidade=5)
    try:
        fila.dequeue()
    except FilaCircularVaziaError:
        return
    raise AssertionError("Deveria ter levantado FilaCircularVaziaError.")


@teste("FilaCircular: ciclo completo de insercoes e remocoes mantem a ordem FIFO")
def test_ciclo_completo() -> None:
    clientes = gerar_clientes(20, semente=8)
    fila = FilaCircular(capacidade=5)
    saida: list[Cliente] = []
    for cliente in clientes:
        if fila.full():
            saida.append(fila.dequeue())
        fila.enqueue(cliente)
    while not fila.empty():
        saida.append(fila.dequeue())
    assert saida == clientes, "Mesmo dando voltas no vetor, a ordem deve ser a de chegada."


@teste("FilaPrioridade: menor valor de prioridade e atendido primeiro")
def test_ordem_prioridade() -> None:
    clientes = gerar_clientes(12, semente=9)
    fila = FilaPrioridade(clientes)
    prioridades = [fila.dequeue().prioridade for _ in range(12)]
    assert prioridades == sorted(prioridades), "As prioridades devem sair em ordem crescente."


@teste("FilaPrioridade: empate de prioridade preserva a ordem de chegada")
def test_estabilidade() -> None:
    prioridades = [3, 1, 2, 1, 3, 2, 1, 3]
    clientes = gerar_clientes(8, prioridades=prioridades, semente=10)
    fila = FilaPrioridade(clientes)
    atendidos = [fila.dequeue() for _ in range(8)]
    for valor in (1, 2, 3):
        obtidos = [c.senha for c in atendidos if c.prioridade == valor]
        esperados = [c.senha for c in clientes if c.prioridade == valor]
        assert obtidos == esperados, f"Empate na prioridade {valor} deveria seguir a chegada."


@teste("FilaPrioridade: head() aponta para a raiz do heap sem remover")
def test_head_prioridade() -> None:
    clientes = [
        criar_cliente("Normal", 3, 1),
        criar_cliente("Emergencia", 1, 2),
        criar_cliente("Prioritario", 2, 3),
    ]
    fila = FilaPrioridade(clientes)
    assert fila.head().nome == "Emergencia"
    assert fila.size() == 3, "head() nao pode remover ninguem."
    assert fila.dequeue().nome == "Emergencia"
    assert fila.head().nome == "Prioritario"


@teste("FilaPrioridade: clientes distintos com mesma prioridade nao quebram a comparacao")
def test_sem_comparar_cliente() -> None:
    fila = FilaPrioridade()
    for indice in range(50):
        fila.enqueue(criar_cliente(f"Cliente {indice}", 2, indice + 1))
    assert fila.size() == 50
    assert [c.senha for c in fila.listar()] == [f"P{i + 1:03d}" for i in range(50)]


@teste("FilaPrioridade: dequeue em fila vazia levanta FilaPrioridadeVaziaError")
def test_prioridade_vazia() -> None:
    try:
        FilaPrioridade().dequeue()
    except FilaPrioridadeVaziaError:
        return
    raise AssertionError("Deveria ter levantado FilaPrioridadeVaziaError.")


@teste("Integracao: as tres estruturas processam os mesmos 20 clientes")
def test_integracao() -> None:
    clientes = gerar_clientes(20, semente=2025)

    classica = Fila(clientes)
    ordem_classica = [classica.dequeue() for _ in range(20)]

    circular = FilaCircular(capacidade=5)
    ordem_circular: list[Cliente] = []
    for cliente in clientes:
        if circular.full():
            ordem_circular.append(circular.dequeue())
        circular.enqueue(cliente)
    while not circular.empty():
        ordem_circular.append(circular.dequeue())

    prioridade = FilaPrioridade(clientes)
    ordem_prioridade = [prioridade.dequeue() for _ in range(20)]

    assert ordem_classica == clientes
    assert ordem_circular == ordem_classica, "A circular mantem a ordem FIFO, so limita a capacidade."
    assert sorted(ordem_prioridade, key=lambda c: c.senha) == sorted(clientes, key=lambda c: c.senha), (
        "A fila de prioridade reordena, mas nao pode perder nem duplicar clientes."
    )
    chegada = {c.senha: i for i, c in enumerate(clientes)}
    chaves = [(c.prioridade, chegada[c.senha]) for c in ordem_prioridade]
    assert chaves == sorted(chaves), "A saida deve seguir (prioridade, ordem de chegada)."
    assert ordem_prioridade != ordem_classica, "Com prioridades variadas as ordens devem diferir."


def main() -> int:
    """Roda todos os testes registrados e devolve 1 se algum falhar."""
    configurar_console()
    cabecalho("TESTES AUTOMATIZADOS")
    print()

    falhas = 0
    for numero, (descricao, funcao) in enumerate(TESTES, start=1):
        try:
            funcao()
        except Exception as erro:
            falhas += 1
            print(f"   [{numero:>2}] FALHOU  {descricao}")
            print(f"        -> {type(erro).__name__}: {erro}")
            traceback.print_exc()
        else:
            print(f"   [{numero:>2}] OK      {descricao}")

    total = len(TESTES)
    print()
    print("-" * 72)
    if falhas:
        print(f"   RESULTADO: {total - falhas}/{total} testes passaram, {falhas} falharam.")
    else:
        print(f"   RESULTADO: {total}/{total} testes passaram. Tudo certo!")
    print("-" * 72)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
