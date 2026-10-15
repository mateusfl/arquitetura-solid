from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from core.domain.entities.dominio import (
    CategoriaModel,
    FormaPagamentoModel,
    ProdutoModel,
    VendaModel,
    VendaProduto,
)
from core.domain.use_cases.ports.interfaces_dao import ICrudDAO


T = TypeVar("T")


class BaseCrudRepository(ABC, Generic[T]):
    """Regras da aplicacao antes de delegar operacoes ao DAO."""

    def __init__(self, dao: ICrudDAO) -> None:
        self._dao = dao

    @abstractmethod
    def validar(self, obj: T) -> None:
        raise NotImplementedError

    def incluir(self, obj: T) -> T:
        self.validar(obj)
        return self._dao.incluir(obj)

    def alterar(self, obj: T) -> T:
        self.validar(obj)
        return self._dao.alterar(obj)

    def excluir(self, id: int) -> None:
        self._dao.excluir(id)

    def obter_por_id(self, id: int) -> T | None:
        if id <= 0:
            raise ValueError('O parâmetro "ID" deve ser positivo.')
        return self._dao.obter_por_id(id)

    def listar(self) -> list[T]:
        return self._dao.listar()


class CategoriaRepository(BaseCrudRepository[CategoriaModel]):
    def validar(self, obj: CategoriaModel) -> None:
        if not obj.descricao or not obj.descricao.strip():
            raise ValueError("A descrição da categoria é obrigatória.")


class ProdutoRepository(BaseCrudRepository[ProdutoModel]):
    def validar(self, obj: ProdutoModel) -> None:
        if not obj.descricao or not obj.descricao.strip():
            raise ValueError("A descrição do produto é obrigatória.")
        if obj.preco <= 0:
            raise ValueError("O preço do produto deve ser maior que zero.")
        if obj.quantidade_estoque < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        if obj.categoria is None or obj.categoria.id is None or obj.categoria.id <= 0:
            raise ValueError("O produto deve ter uma categoria persistida.")


class VendaRepository(BaseCrudRepository[VendaModel]):
    def validar(self, obj: VendaModel) -> None:
        if obj.desconto < 0:
            raise ValueError("O desconto não pode ser negativo.")


class FormaPagamentoRepository(BaseCrudRepository[FormaPagamentoModel]):
    def validar(self, obj: FormaPagamentoModel) -> None:
        if obj.venda is None or obj.venda.id is None or obj.venda.id <= 0:
            raise ValueError("O pagamento deve referenciar uma venda persistida.")
        if obj.valor_pago <= 0:
            raise ValueError("O valor pago deve ser maior que zero.")


class VendaProdutoRepository(BaseCrudRepository[VendaProduto]):
    def validar(self, obj: VendaProduto) -> None:
        if obj.venda is None or obj.venda.id is None or obj.venda.id <= 0:
            raise ValueError("O item deve referenciar uma venda persistida.")
        if obj.produto is None or obj.produto.id is None or obj.produto.id <= 0:
            raise ValueError("O item deve referenciar um produto persistido.")
        if obj.quantidade_vendida <= 0:
            raise ValueError("A quantidade vendida deve ser maior que zero.")
        if obj.preco_momento_venda < 0:
            raise ValueError("O preço no momento da venda não pode ser negativo.")
