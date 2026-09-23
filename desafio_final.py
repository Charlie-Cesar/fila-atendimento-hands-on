"""Desafio final - 20 clientes gerados automaticamente nas tres estruturas, com comparacao."""

from __future__ import annotations

from cliente import (
    PRIORIDADES,
    Cliente,
    cabecalho,
    configurar_console,
    gerar_clientes,
    imprimir_clientes,
)
from fila_circular import CAPACIDADE_PADRAO, FilaCheiaError, FilaCircular
from fila_classica import Fila
from fila_prioridade import FilaPrioridade

TOTAL_CLIENTES = 20
SEMENTE = 2025


def etapa_chegada() -> list[Cliente]:
    """Gera os clientes e mostra a ordem de chegada e a distribuicao por prioridade."""
    cabecalho("DESAFIO FINAL - ETAPA 1: CHEGADA DE 20 CLIENTES")
    clientes = gerar_clientes(TOTAL_CLIENTES, semente=SEMENTE)

    print(f"\n>> {TOTAL_CLIENTES} clientes gerados automaticamente (prioridades sorteadas de 1 a 3):")
    imprimir_clientes(clientes)

    print("\n>> Distribuicao por prioridade:")
    for prioridade, rotulo in PRIORIDADES.items():
        senhas = [c.senha for c in clientes if c.prioridade == prioridade]
        print(f"   {prioridade} - {rotulo:<12} : {len(senhas):>2} cliente(s)  {senhas}")
    return clientes


def etapa_fila_classica(clientes: list[Cliente]) -> list[Cliente]:
    """Atende todos pela fila FIFO e devolve a ordem de atendimento."""
    cabecalho("ETAPA 2: ATENDIMENTO COM A FILA CLASSICA (FIFO)")

    fila = Fila(clientes)
    print(f"\n>> size() apos os 20 enqueue(): {fila.size()}")
    print(f">> head(): {fila.head()}")

    ordem: list[Cliente] = []
    print("\n>> Ordem de atendimento:\n")
    while not fila.empty():
        atendido = fila.dequeue()
        ordem.append(atendido)
        print(f"   {len(ordem):>2}o atendido -> {atendido}")

    print(f"\n>> A ordem de atendimento e identica a de chegada? {ordem == clientes}")
    print("   A prioridade foi completamente ignorada por esta estrutura.")
    return ordem


def etapa_fila_circular(clientes: list[Cliente]) -> tuple[list[Cliente], int, set[int]]:
    """Simula a sala de espera de 5 lugares e devolve ordem, recusas e slots reutilizados."""
    cabecalho("ETAPA 3: SALA DE ESPERA COM FILA CIRCULAR (CAPACIDADE 5)")

    print("\n>> Regra da simulacao: a sala de espera comporta no maximo 5 pessoas.")
    print("   Quando ela enche, o guiche atende (dequeue) para liberar um slot e so")
    print("   entao o proximo cliente entra, reaproveitando a posicao liberada.\n")

    fila = FilaCircular(capacidade=CAPACIDADE_PADRAO)
    ordem: list[Cliente] = []
    recusas = 0
    slots_reutilizados: set[int] = set()
    slots_ja_usados: set[int] = set()

    print(f"   {'evento':<26} {'vetor interno':<32} indices")
    print("   " + "-" * 78)

    for cliente in clientes:
        try:
            fila.enqueue(cliente)
        except FilaCheiaError:
            recusas += 1
            print(f"   {'FILA CHEIA (' + cliente.senha + ' aguarda)':<26} {fila.vetor_resumido():<32} {fila.indices()}")
            atendido = fila.dequeue()
            ordem.append(atendido)
            print(f"   {'atende ' + atendido.senha + ' (libera slot)':<26} {fila.vetor_resumido():<32} {fila.indices()}")
            fila.enqueue(cliente)

        if fila.rear in slots_ja_usados:
            slots_reutilizados.add(fila.rear)
        slots_ja_usados.add(fila.rear)
        marca = " <- slot reutilizado" if fila.rear in slots_reutilizados else ""
        print(f"   {'entra ' + cliente.senha:<26} {fila.vetor_resumido():<32} {fila.indices()}{marca}")

    print("\n>> Fim das chegadas. Atendendo quem ficou na sala:\n")
    while not fila.empty():
        atendido = fila.dequeue()
        ordem.append(atendido)
        print(f"   {'atende ' + atendido.senha:<26} {fila.vetor_resumido():<32} {fila.indices()}")

    print(f"\n>> Total atendido: {len(ordem)} clientes")
    print(f">> Vezes em que a fila ficou cheia e bloqueou uma insercao: {recusas}")
    print(f">> Slots reaproveitados apos remocao: {sorted(slots_reutilizados)}")
    print(f">> A ordem de saida e a mesma da fila classica? {ordem == clientes}")
    return ordem, recusas, slots_reutilizados


def etapa_fila_prioridade(clientes: list[Cliente]) -> list[Cliente]:
    """Atende todos pela fila de prioridade e confere a estabilidade por chegada."""
    cabecalho("ETAPA 4: ATENDIMENTO COM A FILA DE PRIORIDADE (heapq)")

    fila = FilaPrioridade(clientes)
    print(f"\n>> size() apos os 20 enqueue(): {fila.size()}")
    print(f">> head(): {fila.head()}")

    ordem: list[Cliente] = []
    print("\n>> Ordem de atendimento:\n")
    while not fila.empty():
        atendido = fila.dequeue()
        ordem.append(atendido)
        print(f"   {len(ordem):>2}o atendido -> {atendido}")

    print("\n>> Dentro de cada prioridade a ordem de chegada foi preservada?")
    for prioridade, rotulo in PRIORIDADES.items():
        obtido = [c.senha for c in ordem if c.prioridade == prioridade]
        esperado = [c.senha for c in clientes if c.prioridade == prioridade]
        print(f"   {prioridade} - {rotulo:<12}: {obtido} -> {'OK' if obtido == esperado else 'FALHOU'}")
    return ordem


def etapa_comparacao(
    clientes: list[Cliente],
    ordem_fifo: list[Cliente],
    ordem_circular: list[Cliente],
    ordem_prioridade: list[Cliente],
    recusas: int,
) -> None:
    """Monta as tabelas de posicoes e de espera media, e comenta os resultados."""
    cabecalho("ETAPA 5: COMPARACAO DAS TRES ESTRUTURAS")

    pos_fifo = {c.senha: i + 1 for i, c in enumerate(ordem_fifo)}
    pos_circular = {c.senha: i + 1 for i, c in enumerate(ordem_circular)}
    pos_prioridade = {c.senha: i + 1 for i, c in enumerate(ordem_prioridade)}

    print("\n>> Posicao de atendimento de cada cliente em cada estrutura")
    print("   (ganho = quantas posicoes o cliente subiu na fila de prioridade)\n")
    cabecalho_tabela = (
        f"   {'senha':<6} {'nome':<20} {'prio':<5} {'chegada':>7} {'FIFO':>5} "
        f"{'circular':>9} {'prioridade':>11} {'ganho':>6}"
    )
    print(cabecalho_tabela)
    print("   " + "-" * (len(cabecalho_tabela) - 3))
    for chegada, cliente in enumerate(clientes, start=1):
        ganho = pos_fifo[cliente.senha] - pos_prioridade[cliente.senha]
        sinal = f"+{ganho}" if ganho > 0 else str(ganho)
        print(
            f"   {cliente.senha:<6} {cliente.nome:<20} {cliente.prioridade:<5} {chegada:>7} "
            f"{pos_fifo[cliente.senha]:>5} {pos_circular[cliente.senha]:>9} "
            f"{pos_prioridade[cliente.senha]:>11} {sinal:>6}"
        )

    print("\n>> Espera media (em posicoes) por classe de prioridade\n")
    print(f"   {'prioridade':<18} {'qtd':>4} {'FIFO':>8} {'circular':>10} {'prioridade':>12} {'ganho':>8}")
    print("   " + "-" * 64)
    for prioridade, rotulo in PRIORIDADES.items():
        grupo = [c for c in clientes if c.prioridade == prioridade]
        if not grupo:
            continue
        media_fifo = sum(pos_fifo[c.senha] for c in grupo) / len(grupo)
        media_circ = sum(pos_circular[c.senha] for c in grupo) / len(grupo)
        media_prio = sum(pos_prioridade[c.senha] for c in grupo) / len(grupo)
        print(
            f"   {prioridade} - {rotulo:<14} {len(grupo):>4} {media_fifo:>8.1f} "
            f"{media_circ:>10.1f} {media_prio:>12.1f} {media_fifo - media_prio:>+8.1f}"
        )

    emergencias = [c for c in clientes if c.prioridade == 1]
    pior_fifo = max((pos_fifo[c.senha] for c in emergencias), default=0)
    pior_prio = max((pos_prioridade[c.senha] for c in emergencias), default=0)
    if emergencias:
        print(
            f"\n   Pior caso para uma EMERGENCIA: {pior_fifo}o lugar na fila classica "
            f"contra {pior_prio}o na fila de prioridade."
        )

    print("\n>> Leitura dos resultados\n")
    print("   * Fila classica (FIFO): ordem de atendimento = ordem de chegada. E a mais")
    print("     justa em termos de 'quem chegou antes', mas ignora a gravidade do caso.")
    print(f"     Uma emergencia que chegou por ultimo so seria atendida em {pior_fifo}o lugar.")
    print()
    print("   * Fila circular: a ORDEM de atendimento e exatamente a mesma da fila classica")
    print(f"     ({ordem_circular == ordem_fifo}). O que muda e a CAPACIDADE: com 5 posicoes a sala")
    print(f"     encheu {recusas} vezes e cada nova entrada so foi possivel depois de um")
    print("     atendimento. Em troca, ela usa memoria fixa e reaproveita as posicoes.")
    print()
    print("   * Fila de prioridade: reordena a saida. Todas as emergencias sao atendidas")
    print("     antes dos prioritarios, e estes antes dos normais; o empate e resolvido")
    print("     pela ordem de chegada (contador). O preco disso e o atraso dos clientes")
    print("     de prioridade 3, que podem sofrer inanicao (starvation) se emergencias")
    print("     continuarem chegando.")

    print("\n>> Resumo das primeiras 8 senhas de cada estrutura\n")
    print(f"   Chegada......: {[c.senha for c in clientes][:8]}")
    print(f"   FIFO.........: {[c.senha for c in ordem_fifo][:8]}")
    print(f"   Circular.....: {[c.senha for c in ordem_circular][:8]}")
    print(f"   Prioridade...: {[c.senha for c in ordem_prioridade][:8]}")


def main() -> None:
    """Executa as cinco etapas da simulacao na ordem."""
    configurar_console()
    clientes = etapa_chegada()
    ordem_fifo = etapa_fila_classica(clientes)
    ordem_circular, recusas, _ = etapa_fila_circular(clientes)
    ordem_prioridade = etapa_fila_prioridade(clientes)
    etapa_comparacao(clientes, ordem_fifo, ordem_circular, ordem_prioridade, recusas)
    cabecalho("FIM DA SIMULACAO")


if __name__ == "__main__":
    main()
