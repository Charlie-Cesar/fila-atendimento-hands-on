"""Menu interativo que opera as tres estruturas ao mesmo tempo sobre os mesmos clientes."""

from __future__ import annotations

from cliente import (
    PRIORIDADES,
    Cliente,
    cabecalho,
    configurar_console,
    criar_cliente,
    gerar_clientes,
)
from fila_circular import CAPACIDADE_PADRAO, FilaCheiaError, FilaCircular, FilaCircularVaziaError
from fila_classica import Fila, FilaVaziaError
from fila_prioridade import FilaPrioridade, FilaPrioridadeVaziaError

MENU = """
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
+----------------------------------------------------------------+"""


class Central:
    """Agrupa as tres filas e mantem o historico de atendimentos."""

    def __init__(self) -> None:
        self.fila = Fila()
        self.circular = FilaCircular(capacidade=CAPACIDADE_PADRAO)
        self.prioridade = FilaPrioridade()
        self.historico: list[tuple[str, Cliente]] = []
        self.sequencial = 0

    def inserir(self, nome: str, prioridade: int) -> tuple[Cliente, bool]:
        """Insere o cliente nas tres filas e diz se ele coube na circular."""
        self.sequencial += 1
        cliente = criar_cliente(nome, prioridade, self.sequencial)
        self.fila.enqueue(cliente)
        self.prioridade.enqueue(cliente)
        try:
            self.circular.enqueue(cliente)
            return cliente, True
        except FilaCheiaError:
            return cliente, False

    def registrar(self, estrutura: str, cliente: Cliente) -> None:
        """Guarda no historico quem foi atendido e por qual estrutura."""
        self.historico.append((estrutura, cliente))


def ler_inteiro(mensagem: str, minimo: int, maximo: int) -> int | None:
    """Le um inteiro validado; devolve None se o usuario cancelar com ENTER vazio."""
    while True:
        bruto = input(mensagem).strip()
        if not bruto:
            return None
        try:
            valor = int(bruto)
        except ValueError:
            print(f"   ! Digite um numero entre {minimo} e {maximo} (ou ENTER para cancelar).")
            continue
        if minimo <= valor <= maximo:
            return valor
        print(f"   ! Valor fora da faixa permitida ({minimo} a {maximo}).")


def opcao_inserir(central: Central) -> None:
    """Pergunta nome e prioridade e cadastra o cliente nas tres filas."""
    cabecalho("INSERIR CLIENTE")
    nome = input("   Nome do cliente (ENTER cancela): ").strip()
    if not nome:
        print("   Operacao cancelada.")
        return
    print("\n   Prioridades: " + " | ".join(f"{k} = {v}" for k, v in PRIORIDADES.items()))
    prioridade = ler_inteiro("   Prioridade (1-3): ", 1, 3)
    if prioridade is None:
        print("   Operacao cancelada.")
        return

    cliente, entrou_na_circular = central.inserir(nome, prioridade)
    print(f"\n   Cliente cadastrado: {cliente}")
    print(f"   Fila classica ..... posicao {central.fila.size()}")
    print(f"   Fila prioridade ... {central.prioridade.size()} aguardando; proximo e {central.prioridade.head().senha}")
    if entrou_na_circular:
        print(f"   Fila circular ..... ocupou o slot {central.circular.rear}")
        print(central.circular.desenhar())
    else:
        print(f"   Fila circular ..... CHEIA ({central.circular.size()}/{central.circular.capacidade}):")
        print("                       o cliente entrou nas outras duas filas, mas so ocupara")
        print("                       um lugar na sala de espera apos um atendimento (opcao 4).")


def opcao_atender(central: Central, estrutura: str) -> None:
    """Chama o proximo cliente pela estrutura escolhida."""
    cabecalho(f"ATENDER PROXIMO - {estrutura.upper()}")
    try:
        if estrutura == "fila classica":
            atendido = central.fila.dequeue()
        elif estrutura == "fila de prioridade":
            atendido = central.prioridade.dequeue()
        else:
            atendido = central.circular.dequeue()
    except (FilaVaziaError, FilaPrioridadeVaziaError, FilaCircularVaziaError) as erro:
        print(f"   {type(erro).__name__}: {erro}")
        return

    central.registrar(estrutura, atendido)
    print(f"   Chamando: {atendido}")
    if estrutura == "fila circular":
        print(f"   Slot liberado. {central.circular.indices()}")
        print(central.circular.desenhar())
    else:
        restante = central.fila if estrutura == "fila classica" else central.prioridade
        print(f"   Restam {restante.size()} cliente(s) nesta fila.")


def opcao_consultar(central: Central) -> None:
    """Mostra o head das tres filas lado a lado."""
    cabecalho("PROXIMO DE CADA FILA (head)")
    for rotulo, fila in (
        ("Fila classica    ", central.fila),
        ("Fila circular    ", central.circular),
        ("Fila de prioridade", central.prioridade),
    ):
        if fila.empty():
            print(f"   {rotulo}: (vazia)")
        else:
            print(f"   {rotulo}: {fila.head()}")


def opcao_estado(central: Central) -> None:
    """Imprime o conteudo das tres filas e o historico de atendimentos."""
    cabecalho("ESTADO ATUAL DO SISTEMA")

    print("\n>> FILA CLASSICA (FIFO)")
    print(f"   size={central.fila.size()}  empty={central.fila.empty()}")
    for posicao, cliente in enumerate(central.fila.listar(), start=1):
        print(f"   {posicao:>2}o  {cliente}")
    if central.fila.empty():
        print("   (vazia)")

    print("\n>> FILA CIRCULAR (sala de espera, capacidade 5)")
    print(central.circular.desenhar())
    for posicao, cliente in enumerate(central.circular.listar(), start=1):
        print(f"   {posicao:>2}o  {cliente}")
    if central.circular.empty():
        print("   (vazia)")

    print("\n>> FILA DE PRIORIDADE (ordem real de atendimento)")
    print(f"   size={central.prioridade.size()}  por prioridade={central.prioridade.contagem_por_prioridade()}")
    for posicao, cliente in enumerate(central.prioridade.listar(), start=1):
        print(f"   {posicao:>2}o  {cliente}")
    if central.prioridade.empty():
        print("   (vazia)")

    print("\n>> HISTORICO DE ATENDIMENTOS")
    if not central.historico:
        print("   (ninguem foi atendido ainda)")
    else:
        for posicao, (estrutura, cliente) in enumerate(central.historico, start=1):
            print(f"   {posicao:>2}o  [{estrutura:<18}] {cliente}")


def opcao_exemplo(central: Central) -> None:
    """Cadastra de uma vez varios clientes sorteados."""
    cabecalho("CARREGAR CLIENTES DE EXEMPLO")
    quantidade = ler_inteiro("   Quantos clientes gerar? (1-20, ENTER cancela): ", 1, 20)
    if quantidade is None:
        print("   Operacao cancelada.")
        return
    for sorteado in gerar_clientes(quantidade, semente=None):
        cliente, entrou = central.inserir(sorteado.nome, sorteado.prioridade)
        aviso = "" if entrou else "   (nao coube na fila circular)"
        print(f"   + {cliente}{aviso}")
    print(f"\n   Total na fila classica: {central.fila.size()}")
    print(f"   Total na sala de espera (circular): {central.circular.size()}/{central.circular.capacidade}")


def opcao_simulacao() -> None:
    """Roda a simulacao completa do desafio final."""
    import desafio_final

    desafio_final.main()


def main() -> None:
    """Laco principal do menu."""
    configurar_console()
    central = Central()
    cabecalho("SISTEMA INTELIGENTE DE ATENDIMENTO")
    print("\nDigite o numero da opcao desejada e pressione ENTER.")

    acoes = {
        "1": lambda: opcao_inserir(central),
        "2": lambda: opcao_atender(central, "fila classica"),
        "3": lambda: opcao_atender(central, "fila de prioridade"),
        "4": lambda: opcao_atender(central, "fila circular"),
        "5": lambda: opcao_consultar(central),
        "6": lambda: opcao_estado(central),
        "7": lambda: opcao_exemplo(central),
        "8": opcao_simulacao,
    }

    while True:
        print(MENU)
        try:
            escolha = input("   Opcao: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n   Encerrando o sistema. Ate logo!")
            return

        if escolha == "0":
            cabecalho("ENCERRANDO O SISTEMA")
            print(f"\n   Clientes atendidos nesta sessao: {len(central.historico)}")
            print("   Ate logo!")
            return

        acao = acoes.get(escolha)
        if acao is None:
            print("   ! Opcao invalida. Escolha um numero de 0 a 8.")
            continue
        acao()


if __name__ == "__main__":
    main()
