from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import IntEnum


@dataclass
class CategoriaModel:
    id: int | None = None
    tipo_categoria: int = 0
    descricao: str = ""
    margem_lucro: Decimal = Decimal("0.00")


@dataclass
class VendaModel:
    id: int | None = None
    datahora_venda: datetime | None = None
    desconto: Decimal = Decimal("0.00")


class TipoPagamento(IntEnum):
    PIX = 1
    CREDITO = 2
    DEBITO = 3
    ESPECIE = 4


@dataclass
class FormaPagamentoModel:
    id: int | None = None
    tipo_pagamento: TipoPagamento = TipoPagamento.PIX
    valor_pago: Decimal = Decimal("0.00")
    venda: VendaModel | None = None


@dataclass
class ProdutoModel:
    id: int | None = None
    nome: str = ""
    descricao: str = ""
    preco: Decimal = Decimal("0.00")
    quantidade_estoque: int = 0
    alerta_estoque_baixo: int = 0
    codigo_interno: str = ""
    margem_lucro: Decimal = Decimal("0.00")
    categoria: CategoriaModel | None = None


@dataclass
class VendaProduto:
    id: int | None = None
    quantidade_vendida: int = 0
    preco_momento_venda: Decimal = Decimal("0.00")
    venda: VendaModel | None = None
    produto: ProdutoModel | None = None
