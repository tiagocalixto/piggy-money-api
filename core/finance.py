### core/finance.py
"""
Módulo de cálculos e regras financeiras — funções puras de domínio.

Não depende de ORM ou banco de dados; recebe os dados prontos dos repositórios.
"""
import calendar
from datetime import date, datetime

from core.entity.transaction import Transaction


def calcular_saldo_atual(
    conta: object, saldo_inicial: float, repo_transaction: object
) -> float:
    """Calcula o saldo atual de uma conta.

    Saldo = saldo_inicial + total_entradas_efetivadas - total_saidas_efetivadas.

    Args:
        conta: Entidade Account com atributo `id`.
        saldo_inicial: Saldo inicial da conta.
        repo_transaction: Repositório de transações com método get_sum_by_conta.

    Returns:
        Saldo atualizado como float.
    """
    entradas = repo_transaction.get_sum_by_conta(conta.id, "entrada")
    saidas = repo_transaction.get_sum_by_conta(conta.id, "saida")
    return saldo_inicial + entradas - saidas


def calcular_limite_disponivel(
    cartao: object, repo_transaction: object
) -> float:
    """Calcula o limite disponível de um cartão de crédito.

    Limite disponível = limite_total - soma das saidas não pagas (efetivadas,
    vinculadas a faturas abertas/parciais ou sem fatura).

    Args:
        cartao: Entidade CreditCard com atributos `id` e `limite_total`.
        repo_transaction: Repositório com método get_sum_by_cartao_credito.

    Returns:
        Limite disponível como float.
    """
    gastos_nao_pagos = repo_transaction.get_sum_by_cartao_credito(cartao.id)
    return cartao.limite_total - gastos_nao_pagos


def calcular_saldo_beneficio(
    beneficio: object, repo_transaction: object
) -> float:
    """Calcula o saldo atual de um cartão de benefício.

    Saldo = saldo_inicial + entradas_efetivadas - saidas_efetivadas.

    Args:
        beneficio: Entidade BenefitCard com atributos `id` e `saldo_inicial`.
        repo_transaction: Repositório com método list_by_cartao_beneficio.

    Returns:
        Saldo atualizado como float.
    """
    transactions = repo_transaction.list_by_cartao_beneficio(beneficio.id)
    entradas = sum(
        t.valor
        for t in transactions
        if t.efetivada and t.tipo_movimento == "entrada"
    )
    saidas = sum(
        t.valor
        for t in transactions
        if t.efetivada and t.tipo_movimento == "saida"
    )
    return beneficio.saldo_inicial + entradas - saidas


def ajustar_data_parcela(data_original: date, parcela: int) -> date:
    """Ajusta a data para a parcela N no futuro.

    Trata dias inválidos (ex: 31/01 → 28/02 ou 29/02 em ano bissexto).

    Args:
        data_original: Data base da transação original.
        parcela: Número da parcela (1 = mês atual, 2 = mês seguinte, etc.).

    Returns:
        Data ajustada para a parcela.
    """
    mes = data_original.month + (parcela - 1)
    ano = data_original.year + (mes - 1) // 12
    mes = ((mes - 1) % 12) + 1
    dia = data_original.day

    # Ajusta dia para o último dia válido do mês
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    dia = min(dia, ultimo_dia)

    return date(ano, mes, dia)


def gerar_parcelas(
    transaction: Transaction, repo_transaction: object
) -> list[Transaction]:
    """Gera N transações parceladas a partir de uma transação original.

    A primeira parcela (parcela_atual=1) é persistida, as demais são geradas
    como entidades prontas para persistência. Cada parcela tem data ajustada
    para o mês correspondente e valor igual a valor_total / parcelas_total.

    Args:
        transaction: Transação base com parcelas_total > 1.
        repo_transaction: Repositório de transações com método create.

    Returns:
        Lista de transações criadas (todas as parcelas, incluindo a original).
    """
    if transaction.parcelas_total <= 1:
        return [transaction]

    valor_parcela = round(transaction.valor / transaction.parcelas_total, 2)
    data_base = transaction.data if transaction.data else datetime.now()

    # Garantir que data_base seja date
    if isinstance(data_base, datetime):
        data_base = data_base.date() if hasattr(data_base, "date") else date.today()

    parcelas = []
    primeira_parcela_id = None

    # Cria cada parcela
    for i in range(1, transaction.parcelas_total + 1):
        parcela = Transaction(
            usuario_id=transaction.usuario_id,
            descricao=transaction.descricao,
            valor=valor_parcela,
            categoria_id=transaction.categoria_id,
            tipo_movimento=transaction.tipo_movimento,
            data=datetime.combine(ajustar_data_parcela(data_base, i), datetime.min.time()),
            efetivada=transaction.efetivada,
            conta_id=transaction.conta_id,
            cartao_credito_id=transaction.cartao_credito_id,
            cartao_beneficio_id=transaction.cartao_beneficio_id,
            parcelas_total=transaction.parcelas_total,
            parcela_atual=i,
            transacao_original_id=primeira_parcela_id,
            fatura_id=transaction.fatura_id,
        )

        created = repo_transaction.create(parcela)
        parcelas.append(created)

        # Guarda o ID da primeira para referência das demais
        if i == 1:
            primeira_parcela_id = created.id

    return parcelas
