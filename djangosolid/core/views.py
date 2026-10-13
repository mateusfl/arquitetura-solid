from dataclasses import dataclass
from typing import Any, Callable

from django.contrib import messages
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from core.entities.dominio import (
    CategoriaModel,
    FormaPagamentoModel,
    ProdutoModel,
    TipoPagamento,
    VendaModel,
    VendaProduto,
)
from core.forms import (
    CategoriaForm,
    FormaPagamentoForm,
    ProdutoForm,
    VendaForm,
    VendaProdutoForm,
)
from core.models import Categoria as CategoriaORM, Produto as ProdutoORM, Venda as VendaORM
from core.repositories.repository import (
    CategoriaRepository,
    FormaPagamentoRepository,
    ProdutoRepository,
    VendaProdutoRepository,
    VendaRepository,
)


@dataclass(frozen=True)
class RecursoCRUD:
    titulo: str
    form_class: type
    repositorio: type
    colunas: tuple[str, ...]
    para_entidade: Callable[[dict[str, Any], int | None], Any]
    para_formulario: Callable[[Any], dict[str, Any]]
    para_linha: Callable[[Any], tuple[Any, ...]]


def _categoria_do_modelo(modelo: CategoriaORM | None) -> CategoriaModel | None:
    if modelo is None:
        return None
    return CategoriaModel(
        id=modelo.pk,
        tipo_categoria=modelo.tipo_categoria,
        descricao=modelo.descricao,
        margem_lucro=modelo.margem_lucro,
    )


def _venda_do_modelo(modelo: VendaORM | None) -> VendaModel | None:
    if modelo is None:
        return None
    return VendaModel(id=modelo.pk, datahora_venda=modelo.datahora_venda, desconto=modelo.desconto)


def _produto_do_modelo(modelo: ProdutoORM | None) -> ProdutoModel | None:
    if modelo is None:
        return None
    return ProdutoModel(
        id=modelo.pk,
        nome=modelo.nome,
        descricao=modelo.descricao,
        preco=modelo.preco,
        quantidade_estoque=modelo.quantidade_estoque,
        alerta_estoque_baixo=modelo.alerta_estoque_baixo,
        codigo_interno=modelo.codigo_interno,
        margem_lucro=modelo.margem_lucro,
        categoria=_categoria_do_modelo(modelo.categoria),
    )


def _categoria_entidade(dados: dict[str, Any], id: int | None) -> CategoriaModel:
    return CategoriaModel(id, dados["tipo_categoria"], dados["descricao"], dados["margem_lucro"])


def _venda_entidade(dados: dict[str, Any], id: int | None) -> VendaModel:
    return VendaModel(id=id, desconto=dados["desconto"])


def _produto_entidade(dados: dict[str, Any], id: int | None) -> ProdutoModel:
    return ProdutoModel(
        id=id,
        nome=dados["nome"],
        descricao=dados["descricao"],
        preco=dados["preco"],
        quantidade_estoque=dados["quantidade_estoque"],
        alerta_estoque_baixo=dados["alerta_estoque_baixo"],
        codigo_interno=dados["codigo_interno"],
        margem_lucro=dados["margem_lucro"],
        categoria=_categoria_do_modelo(dados["categoria"]),
    )


def _pagamento_entidade(dados: dict[str, Any], id: int | None) -> FormaPagamentoModel:
    return FormaPagamentoModel(
        id=id,
        tipo_pagamento=TipoPagamento(int(dados["tipo_pagamento"])),
        valor_pago=dados["valor_pago"],
        venda=_venda_do_modelo(dados["venda"]),
    )


def _item_venda_entidade(dados: dict[str, Any], id: int | None) -> VendaProduto:
    return VendaProduto(
        id=id,
        quantidade_vendida=dados["quantidade_vendida"],
        preco_momento_venda=dados["preco_momento_venda"],
        venda=_venda_do_modelo(dados["venda"]),
        produto=_produto_do_modelo(dados["produto"]),
    )


RECURSOS: dict[str, RecursoCRUD] = {
    "categorias": RecursoCRUD(
        "Categorias", CategoriaForm, CategoriaRepository,
        ("ID", "Tipo", "Descrição", "Margem (%)"),
        _categoria_entidade,
        lambda item: {
            "tipo_categoria": item.tipo_categoria,
            "descricao": item.descricao,
            "margem_lucro": item.margem_lucro,
        },
        lambda item: (item.id, item.tipo_categoria, item.descricao, item.margem_lucro),
    ),
    "produtos": RecursoCRUD(
        "Produtos", ProdutoForm, ProdutoRepository,
        ("ID", "Nome", "Descrição", "Preço (R$)", "Estoque", "Categoria"),
        _produto_entidade,
        lambda item: {
            "nome": item.nome,
            "descricao": item.descricao,
            "preco": item.preco,
            "quantidade_estoque": item.quantidade_estoque,
            "alerta_estoque_baixo": item.alerta_estoque_baixo,
            "codigo_interno": item.codigo_interno,
            "margem_lucro": item.margem_lucro,
            "categoria": item.categoria.id if item.categoria else None,
        },
        lambda item: (item.id, item.nome, item.descricao, item.preco,
                      item.quantidade_estoque, item.categoria.descricao if item.categoria else "—"),
    ),
    "vendas": RecursoCRUD(
        "Vendas", VendaForm, VendaRepository,
        ("ID", "Data e hora", "Desconto (R$)"),
        _venda_entidade,
        lambda item: {"desconto": item.desconto},
        lambda item: (item.id, item.datahora_venda or "—", item.desconto),
    ),
    "pagamentos": RecursoCRUD(
        "Formas de pagamento", FormaPagamentoForm, FormaPagamentoRepository,
        ("ID", "Tipo", "Valor pago (R$)", "Venda"),
        _pagamento_entidade,
        lambda item: {
            "tipo_pagamento": int(item.tipo_pagamento),
            "valor_pago": item.valor_pago,
            "venda": item.venda.id if item.venda else None,
        },
        lambda item: (item.id, item.tipo_pagamento.name, item.valor_pago,
                      item.venda.id if item.venda else "—"),
    ),
    "itens-venda": RecursoCRUD(
        "Itens de venda", VendaProdutoForm, VendaProdutoRepository,
        ("ID", "Venda", "Produto", "Quantidade", "Preço na venda (R$)"),
        _item_venda_entidade,
        lambda item: {
            "venda": item.venda.id if item.venda else None,
            "produto": item.produto.id if item.produto else None,
            "quantidade_vendida": item.quantidade_vendida,
            "preco_momento_venda": item.preco_momento_venda,
        },
        lambda item: (item.id, item.venda.id if item.venda else "—",
                      item.produto.nome if item.produto else "—",
                      item.quantidade_vendida, item.preco_momento_venda),
    ),
}


def _recurso(slug: str) -> RecursoCRUD:
    try:
        return RECURSOS[slug]
    except KeyError as exc:
        raise Http404("Recurso não encontrado") from exc


def inicio(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "core/index.html",
        {"recursos": [(slug, recurso.titulo) for slug, recurso in RECURSOS.items()]},
    )


@require_http_methods(["GET"])
def listar(request: HttpRequest, recurso: str) -> HttpResponse:
    config = _recurso(recurso)
    itens = config.repositorio().listar()
    return render(
        request,
        "core/list.html",
        {
            "slug": recurso,
            "titulo": config.titulo,
            "colunas": config.colunas,
            "linhas": [(item.id, config.para_linha(item)) for item in itens],
        },
    )


@require_http_methods(["GET", "POST"])
def criar(request: HttpRequest, recurso: str) -> HttpResponse:
    return _formulario(request, recurso)


@require_http_methods(["GET", "POST"])
def editar(request: HttpRequest, recurso: str, id: int) -> HttpResponse:
    return _formulario(request, recurso, id)


def _formulario(request: HttpRequest, recurso: str, id: int | None = None) -> HttpResponse:
    config = _recurso(recurso)
    repositorio = config.repositorio()
    entidade = repositorio.obter_por_id(id) if id is not None else None
    if id is not None and entidade is None:
        raise Http404("Registro não encontrado")

    if request.method == "POST":
        form = config.form_class(request.POST)
        if form.is_valid():
            dados = config.para_entidade(form.cleaned_data, id)
            try:
                if id is None:
                    repositorio.incluir(dados)
                    messages.success(request, "Registro criado com sucesso.")
                else:
                    repositorio.alterar(dados)
                    messages.success(request, "Registro atualizado com sucesso.")
                return redirect("core:listar", recurso=recurso)
            except IntegrityError:
                form.add_error(None, "Não foi possível salvar: verifique códigos duplicados e vínculos existentes.")
    else:
        initial = config.para_formulario(entidade) if entidade is not None else None
        form = config.form_class(initial=initial)

    return render(
        request,
        "core/form.html",
        {
            "slug": recurso,
            "titulo": config.titulo,
            "form": form,
            "editando": id is not None,
        },
    )


@require_http_methods(["GET", "POST"])
def excluir(request: HttpRequest, recurso: str, id: int) -> HttpResponse:
    config = _recurso(recurso)
    repositorio = config.repositorio()
    entidade = repositorio.obter_por_id(id)
    if entidade is None:
        raise Http404("Registro não encontrado")

    if request.method == "POST":
        try:
            repositorio.excluir(id)
            messages.success(request, "Registro excluído com sucesso.")
        except ProtectedError:
            messages.error(request, "Este registro está relacionado a outros e não pode ser excluído.")
        return redirect("core:listar", recurso=recurso)

    return render(
        request,
        "core/confirm_delete.html",
        {"slug": recurso, "titulo": config.titulo, "entidade": entidade},
    )
