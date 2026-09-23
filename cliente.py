"""Modelo de cliente compartilhado pelas tres estruturas de fila."""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass

PRIORIDADES: dict[int, str] = {
    1: "Emergência",
    2: "Prioritário",
    3: "Normal",
}

PREFIXOS_SENHA: dict[int, str] = {1: "E", 2: "P", 3: "N"}

NOMES: list[str] = [
    "Ana Souza", "Bruno Lima", "Carla Menezes", "Diego Ramos", "Elisa Prado",
    "Fabio Nunes", "Gabriela Rocha", "Heitor Campos", "Isabela Freitas", "João Vitor",
    "Karina Alves", "Lucas Ferreira", "Marina Duarte", "Nathan Borges", "Olivia Tavares",
    "Paulo Andrade", "Quenia Martins", "Rafael Moreira", "Sofia Cardoso", "Tiago Barros",
    "Ursula Pinto", "Vinicius Lopes", "Wesley Monteiro", "Xênia Ribeiro", "Yasmin Correia",
    "Zeca Almeida", "Beatriz Siqueira", "Caio Estevão", "Daniela Pires", "Eduardo Chaves",
]


def configurar_console() -> None:
    """Forca UTF-8 na saida para os acentos aparecerem no terminal do Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass


@dataclass(frozen=True)
class Cliente:
    """Cliente que retirou uma senha na central de atendimento."""

    nome: str
    senha: str
    prioridade: int

    def __post_init__(self) -> None:
        if self.prioridade not in PRIORIDADES:
            raise ValueError(
                f"Prioridade inválida: {self.prioridade!r}. Use 1 (Emergência), "
                f"2 (Prioritário) ou 3 (Normal)."
            )

    @property
    def descricao_prioridade(self) -> str:
        return PRIORIDADES[self.prioridade]

    def __str__(self) -> str:
        return f"{self.senha} | {self.nome:<20} | {self.prioridade} - {self.descricao_prioridade}"


def gerar_senha(prioridade: int, sequencial: int) -> str:
    """Monta a senha no formato <letra da prioridade><numero de 3 digitos>."""
    return f"{PREFIXOS_SENHA[prioridade]}{sequencial:03d}"


def criar_cliente(nome: str, prioridade: int, sequencial: int) -> Cliente:
    """Cria um cliente com a senha ja gerada a partir da prioridade."""
    return Cliente(nome=nome, senha=gerar_senha(prioridade, sequencial), prioridade=prioridade)


def gerar_clientes(
    quantidade: int,
    prioridades: list[int] | None = None,
    semente: int | None = None,
) -> list[Cliente]:
    """Gera clientes com nomes sorteados; uma semente fixa torna o resultado reproduzivel."""
    sorteio = random.Random(semente)
    if quantidade <= len(NOMES):
        nomes = sorteio.sample(NOMES, k=quantidade)
    else:
        nomes = [sorteio.choice(NOMES) for _ in range(quantidade)]

    clientes: list[Cliente] = []
    for posicao, nome in enumerate(nomes, start=1):
        if prioridades is not None:
            prioridade = prioridades[posicao - 1]
        else:
            prioridade = sorteio.randint(1, 3)
        clientes.append(criar_cliente(nome, prioridade, posicao))
    return clientes


def imprimir_clientes(clientes: list[Cliente], titulo: str = "") -> None:
    """Imprime uma lista numerada de clientes."""
    if titulo:
        print(titulo)
    if not clientes:
        print("   (nenhum cliente)")
        return
    for posicao, cliente in enumerate(clientes, start=1):
        print(f"   {posicao:>2}º  {cliente}")


def cabecalho(texto: str, largura: int = 72) -> None:
    """Imprime um titulo de secao destacado."""
    print()
    print("=" * largura)
    print(texto.center(largura))
    print("=" * largura)


if __name__ == "__main__":
    configurar_console()
    cabecalho("MODELO DE CLIENTE")
    imprimir_clientes(gerar_clientes(5, semente=7), "Exemplo de 5 clientes gerados:")
