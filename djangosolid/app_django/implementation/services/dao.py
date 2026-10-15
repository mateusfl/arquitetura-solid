"""Conexão SQLite via Django ORM e DAOs que convertem domínio/ORM."""

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper

from core.domain.entities.dominio import (
    CategoriaModel as Categoria,
    FormaPagamentoModel as FormaPagamento,
    ProdutoModel as Produto,
    TipoPagamento,
    VendaModel as Venda,
    VendaProduto as ItemVenda,
)
from app_django.models import (
    Categoria as CategoriaORM,
    FormaPagamento as FormaPagamentoORM,
    Produto as ProdutoORM,
    Venda as VendaORM,
    VendaProduto as ItemVendaORM,
)
from core.domain.use_cases.ports.interfaces_dao import ICrudDAO


class ConexaoBD_ORM:
    DB_ALIAS = "db_solid"

    def obter_conexao(self) -> BaseDatabaseWrapper:
        """Obtém a conexão SQLite configurada em settings.DATABASES."""
        return connections[self.DB_ALIAS]


class CategoriaDAO_ORM(ICrudDAO):
    def __init__(self, conexao: ConexaoBD_ORM) -> None:
        self._conexao = conexao
        self._conexao.obter_conexao()

    @property
    def _manager(self):
        return CategoriaORM.objects.using(self._conexao.DB_ALIAS)

    @staticmethod
    def _dominio(registro: CategoriaORM) -> Categoria:
        return Categoria(
            id=registro.pk,
            tipo_categoria=registro.tipo_categoria,
            descricao=registro.descricao,
            margem_lucro=registro.margem_lucro,
        )

    def incluir(self, entidade: Categoria) -> Categoria:
        registro = CategoriaORM(
            tipo_categoria=entidade.tipo_categoria,
            descricao=entidade.descricao,
            margem_lucro=entidade.margem_lucro,
        )
        registro.save(using=self._conexao.DB_ALIAS, force_insert=True)
        return self._dominio(registro)

    def alterar(self, entidade: Categoria) -> Categoria:
        registro = self._manager.filter(pk=entidade.id).first()
        if registro is None:
            raise CategoriaORM.DoesNotExist(f"Categoria id={entidade.id} não encontrada")
        registro.tipo_categoria = entidade.tipo_categoria
        registro.descricao = entidade.descricao
        registro.margem_lucro = entidade.margem_lucro
        registro.save(using=self._conexao.DB_ALIAS, force_update=True)
        return self._dominio(registro)

    def excluir(self, id: int) -> None:
        self._manager.filter(pk=id).delete()

    def obter_por_id(self, id: int) -> Categoria | None:
        registro = self._manager.filter(pk=id).first()
        return self._dominio(registro) if registro else None

    def listar(self) -> list[Categoria]:
        return [self._dominio(registro) for registro in self._manager.order_by("descricao")]


class ProdutoDAO_ORM(ICrudDAO):
    def __init__(self, conexao: ConexaoBD_ORM) -> None:
        self._conexao = conexao
        self._conexao.obter_conexao()

    @property
    def _manager(self):
        return ProdutoORM.objects.using(self._conexao.DB_ALIAS)

    @staticmethod
    def _dominio(registro: ProdutoORM) -> Produto:
        categoria = registro.categoria
        return Produto(
            id=registro.pk,
            nome=registro.nome,
            descricao=registro.descricao,
            preco=registro.preco,
            quantidade_estoque=registro.quantidade_estoque,
            alerta_estoque_baixo=registro.alerta_estoque_baixo,
            codigo_interno=registro.codigo_interno,
            margem_lucro=registro.margem_lucro,
            categoria=CategoriaDAO_ORM._dominio(categoria),
        )

    @staticmethod
    def _dados(entidade: Produto) -> dict[str, object]:
        if entidade.categoria is None or entidade.categoria.id is None:
            raise ValueError("O produto deve referenciar uma categoria persistida.")
        return {
            "nome": entidade.nome,
            "descricao": entidade.descricao,
            "preco": entidade.preco,
            "quantidade_estoque": entidade.quantidade_estoque,
            "alerta_estoque_baixo": entidade.alerta_estoque_baixo,
            "codigo_interno": entidade.codigo_interno,
            "margem_lucro": entidade.margem_lucro,
            "categoria_id": entidade.categoria.id,
        }

    def incluir(self, entidade: Produto) -> Produto:
        registro = ProdutoORM(**self._dados(entidade))
        registro.save(using=self._conexao.DB_ALIAS, force_insert=True)
        registro = self._manager.select_related("categoria").get(pk=registro.pk)
        return self._dominio(registro)

    def alterar(self, entidade: Produto) -> Produto:
        registro = self._manager.filter(pk=entidade.id).first()
        if registro is None:
            raise ProdutoORM.DoesNotExist(f"Produto id={entidade.id} não encontrado")
        for campo, valor in self._dados(entidade).items():
            setattr(registro, campo, valor)
        registro.save(using=self._conexao.DB_ALIAS, force_update=True)
        registro = self._manager.select_related("categoria").get(pk=registro.pk)
        return self._dominio(registro)

    def excluir(self, id: int) -> None:
        self._manager.filter(pk=id).delete()

    def obter_por_id(self, id: int) -> Produto | None:
        registro = self._manager.select_related("categoria").filter(pk=id).first()
        return self._dominio(registro) if registro else None

    def listar(self) -> list[Produto]:
        registros = self._manager.select_related("categoria").order_by("nome")
        return [self._dominio(registro) for registro in registros]


class VendaDAO_ORM(ICrudDAO):
    def __init__(self, conexao: ConexaoBD_ORM) -> None:
        self._conexao = conexao
        self._conexao.obter_conexao()

    @property
    def _manager(self):
        return VendaORM.objects.using(self._conexao.DB_ALIAS)

    @staticmethod
    def _dominio(registro: VendaORM) -> Venda:
        return Venda(
            id=registro.pk,
            datahora_venda=registro.datahora_venda,
            desconto=registro.desconto,
        )

    def incluir(self, entidade: Venda) -> Venda:
        registro = VendaORM(desconto=entidade.desconto)
        registro.save(using=self._conexao.DB_ALIAS, force_insert=True)
        return self._dominio(registro)

    def alterar(self, entidade: Venda) -> Venda:
        registro = self._manager.filter(pk=entidade.id).first()
        if registro is None:
            raise VendaORM.DoesNotExist(f"Venda id={entidade.id} não encontrada")
        registro.desconto = entidade.desconto
        registro.save(using=self._conexao.DB_ALIAS, force_update=True)
        return self._dominio(registro)

    def excluir(self, id: int) -> None:
        self._manager.filter(pk=id).delete()

    def obter_por_id(self, id: int) -> Venda | None:
        registro = self._manager.filter(pk=id).first()
        return self._dominio(registro) if registro else None

    def listar(self) -> list[Venda]:
        return [self._dominio(registro) for registro in self._manager.order_by("-datahora_venda")]


class FormaPagamentoDAO_ORM(ICrudDAO):
    def __init__(self, conexao: ConexaoBD_ORM) -> None:
        self._conexao = conexao
        self._conexao.obter_conexao()

    @property
    def _manager(self):
        return FormaPagamentoORM.objects.using(self._conexao.DB_ALIAS)

    @staticmethod
    def _dominio(registro: FormaPagamentoORM) -> FormaPagamento:
        venda = VendaDAO_ORM._dominio(registro.venda)
        return FormaPagamento(
            id=registro.pk,
            tipo_pagamento=TipoPagamento(registro.tipo_pagamento),
            valor_pago=registro.valor_pago,
            venda=venda,
        )

    @staticmethod
    def _dados(entidade: FormaPagamento) -> dict[str, object]:
        if entidade.venda is None or entidade.venda.id is None:
            raise ValueError("O pagamento deve referenciar uma venda persistida.")
        return {
            "tipo_pagamento": int(entidade.tipo_pagamento),
            "valor_pago": entidade.valor_pago,
            "venda_id": entidade.venda.id,
        }

    def incluir(self, entidade: FormaPagamento) -> FormaPagamento:
        registro = FormaPagamentoORM(**self._dados(entidade))
        registro.save(using=self._conexao.DB_ALIAS, force_insert=True)
        registro = self._manager.select_related("venda").get(pk=registro.pk)
        return self._dominio(registro)

    def alterar(self, entidade: FormaPagamento) -> FormaPagamento:
        registro = self._manager.filter(pk=entidade.id).first()
        if registro is None:
            raise FormaPagamentoORM.DoesNotExist(
                f"Forma de pagamento id={entidade.id} não encontrada"
            )
        for campo, valor in self._dados(entidade).items():
            setattr(registro, campo, valor)
        registro.save(using=self._conexao.DB_ALIAS, force_update=True)
        registro = self._manager.select_related("venda").get(pk=registro.pk)
        return self._dominio(registro)

    def excluir(self, id: int) -> None:
        self._manager.filter(pk=id).delete()

    def obter_por_id(self, id: int) -> FormaPagamento | None:
        registro = self._manager.select_related("venda").filter(pk=id).first()
        return self._dominio(registro) if registro else None

    def listar(self) -> list[FormaPagamento]:
        registros = self._manager.select_related("venda").order_by("id")
        return [self._dominio(registro) for registro in registros]


class VendaProdutoDAO_ORM(ICrudDAO):
    def __init__(self, conexao: ConexaoBD_ORM) -> None:
        self._conexao = conexao
        self._conexao.obter_conexao()

    @property
    def _manager(self):
        return ItemVendaORM.objects.using(self._conexao.DB_ALIAS)

    @staticmethod
    def _dominio(registro: ItemVendaORM) -> ItemVenda:
        return ItemVenda(
            id=registro.pk,
            quantidade_vendida=registro.quantidade_vendida,
            preco_momento_venda=registro.preco_momento_venda,
            venda=VendaDAO_ORM._dominio(registro.venda),
            produto=ProdutoDAO_ORM._dominio(registro.produto),
        )

    @staticmethod
    def _dados(entidade: ItemVenda) -> dict[str, object]:
        if entidade.venda is None or entidade.venda.id is None:
            raise ValueError("O item deve referenciar uma venda persistida.")
        if entidade.produto is None or entidade.produto.id is None:
            raise ValueError("O item deve referenciar um produto persistido.")
        return {
            "quantidade_vendida": entidade.quantidade_vendida,
            "preco_momento_venda": entidade.preco_momento_venda,
            "venda_id": entidade.venda.id,
            "produto_id": entidade.produto.id,
        }

    def incluir(self, entidade: ItemVenda) -> ItemVenda:
        registro = ItemVendaORM(**self._dados(entidade))
        registro.save(using=self._conexao.DB_ALIAS, force_insert=True)
        registro = self._manager.select_related("venda", "produto__categoria").get(pk=registro.pk)
        return self._dominio(registro)

    def alterar(self, entidade: ItemVenda) -> ItemVenda:
        registro = self._manager.filter(pk=entidade.id).first()
        if registro is None:
            raise ItemVendaORM.DoesNotExist(f"Item de venda id={entidade.id} não encontrado")
        for campo, valor in self._dados(entidade).items():
            setattr(registro, campo, valor)
        registro.save(using=self._conexao.DB_ALIAS, force_update=True)
        registro = self._manager.select_related("venda", "produto__categoria").get(pk=registro.pk)
        return self._dominio(registro)

    def excluir(self, id: int) -> None:
        self._manager.filter(pk=id).delete()

    def obter_por_id(self, id: int) -> ItemVenda | None:
        registro = self._manager.select_related("venda", "produto__categoria").filter(pk=id).first()
        return self._dominio(registro) if registro else None

    def listar(self) -> list[ItemVenda]:
        registros = self._manager.select_related("venda", "produto__categoria").order_by("id")
        return [self._dominio(registro) for registro in registros]

    def listar_por_venda(self, id_venda: int) -> list[ItemVenda]:
        registros = self._manager.select_related("venda", "produto__categoria").filter(venda_id=id_venda)
        return [self._dominio(registro) for registro in registros]

    def buscar_por_venda_e_produto(
        self, id_venda: int, id_produto: int
    ) -> ItemVenda | None:
        registro = self._manager.select_related("venda", "produto__categoria").filter(
            venda_id=id_venda,
            produto_id=id_produto,
        ).first()
        return self._dominio(registro) if registro else None
