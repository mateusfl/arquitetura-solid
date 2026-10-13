"""Repositórios de domínio que delegam persistência aos DAOs ORM."""

from core.entities.dominio import (
    CategoriaModel as Categoria,
    FormaPagamentoModel as FormaPagamento,
    ProdutoModel as Produto,
    VendaModel as Venda,
    VendaProduto as ItemVenda,
)
from core.implementation.services.dao import (
    CategoriaDAO_ORM,
    ConexaoBD_ORM,
    FormaPagamentoDAO_ORM,
    ProdutoDAO_ORM,
    VendaDAO_ORM,
    VendaProdutoDAO_ORM,
)
from core.ports.interfaces import IConexaoBD, InterfaceDAO


class CategoriaRepository(InterfaceDAO[Categoria]):
    def __init__(self, conexao: IConexaoBD | None = None) -> None:
        self.dao = CategoriaDAO_ORM(conexao or ConexaoBD_ORM())

    def incluir(self, entidade: Categoria) -> Categoria:
        return self.dao.incluir(entidade)

    def alterar(self, entidade: Categoria) -> Categoria:
        return self.dao.alterar(entidade)

    def excluir(self, id: int) -> None:
        self.dao.excluir(id)

    def obter_por_id(self, id: int) -> Categoria | None:
        return self.dao.obter_por_id(id)

    def listar(self) -> list[Categoria]:
        return self.dao.listar()


class ProdutoRepository(InterfaceDAO[Produto]):
    def __init__(self, conexao: IConexaoBD | None = None) -> None:
        self.dao = ProdutoDAO_ORM(conexao or ConexaoBD_ORM())

    def incluir(self, entidade: Produto) -> Produto:
        return self.dao.incluir(entidade)

    def alterar(self, entidade: Produto) -> Produto:
        return self.dao.alterar(entidade)

    def excluir(self, id: int) -> None:
        self.dao.excluir(id)

    def obter_por_id(self, id: int) -> Produto | None:
        return self.dao.obter_por_id(id)

    def listar(self) -> list[Produto]:
        return self.dao.listar()


class VendaRepository(InterfaceDAO[Venda]):
    def __init__(self, conexao: IConexaoBD | None = None) -> None:
        self.dao = VendaDAO_ORM(conexao or ConexaoBD_ORM())

    def incluir(self, entidade: Venda) -> Venda:
        return self.dao.incluir(entidade)

    def alterar(self, entidade: Venda) -> Venda:
        return self.dao.alterar(entidade)

    def excluir(self, id: int) -> None:
        self.dao.excluir(id)

    def obter_por_id(self, id: int) -> Venda | None:
        return self.dao.obter_por_id(id)

    def listar(self) -> list[Venda]:
        return self.dao.listar()


class FormaPagamentoRepository(InterfaceDAO[FormaPagamento]):
    def __init__(self, conexao: IConexaoBD | None = None) -> None:
        self.dao = FormaPagamentoDAO_ORM(conexao or ConexaoBD_ORM())

    def incluir(self, entidade: FormaPagamento) -> FormaPagamento:
        return self.dao.incluir(entidade)

    def alterar(self, entidade: FormaPagamento) -> FormaPagamento:
        return self.dao.alterar(entidade)

    def excluir(self, id: int) -> None:
        self.dao.excluir(id)

    def obter_por_id(self, id: int) -> FormaPagamento | None:
        return self.dao.obter_por_id(id)

    def listar(self) -> list[FormaPagamento]:
        return self.dao.listar()


class VendaProdutoRepository(InterfaceDAO[ItemVenda]):
    def __init__(self, conexao: IConexaoBD | None = None) -> None:
        self.dao = VendaProdutoDAO_ORM(conexao or ConexaoBD_ORM())

    def incluir(self, entidade: ItemVenda) -> ItemVenda:
        return self.dao.incluir(entidade)

    def alterar(self, entidade: ItemVenda) -> ItemVenda:
        return self.dao.alterar(entidade)

    def excluir(self, id: int) -> None:
        self.dao.excluir(id)

    def obter_por_id(self, id: int) -> ItemVenda | None:
        return self.dao.obter_por_id(id)

    def listar(self) -> list[ItemVenda]:
        return self.dao.listar()

    def listar_por_venda(self, id_venda: int) -> list[ItemVenda]:
        return self.dao.listar_por_venda(id_venda)

    def buscar_por_venda_e_produto(
        self, id_venda: int, id_produto: int
    ) -> ItemVenda | None:
        return self.dao.buscar_por_venda_e_produto(id_venda, id_produto)
