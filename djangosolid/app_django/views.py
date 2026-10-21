from django.contrib import messages
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

from app_django.forms import CategoriaForm, FormaPagamentoForm, ProdutoForm, VendaForm, VendaProdutoForm
from app_django.implementation.services.dao import (
    CategoriaDAO_ORM,
    ConexaoBD_ORM,
    FormaPagamentoDAO_ORM,
    ProdutoDAO_ORM,
    VendaDAO_ORM,
    VendaProdutoDAO_ORM,
)
from core.domain.entities.dominio import (
    CategoriaModel,
    FormaPagamentoModel,
    ProdutoModel,
    TipoPagamento,
    VendaModel,
    VendaProduto,
)
from core.domain.use_cases.repository import (
    CategoriaRepository,
    FormaPagamentoRepository,
    ProdutoRepository,
    VendaProdutoRepository,
    VendaRepository,
)


def _venda(dados):
    venda = dados.get("venda")
    return VendaModel(id=venda.pk) if venda else None


def _produto(dados, id=None):
    categoria = dados["categoria"]
    return ProdutoModel(
        id=id,
        nome=dados["nome"],
        descricao=dados["descricao"],
        preco=dados["preco"],
        quantidade_estoque=dados["quantidade_estoque"],
        alerta_estoque_baixo=dados["alerta_estoque_baixo"],
        codigo_interno=dados["codigo_interno"],
        margem_lucro=dados["margem_lucro"],
        categoria=CategoriaModel(id=categoria.pk),
    )


def _mostrar_lista(request, titulo, colunas, itens, linha, urls):
    return render(request, "core/list.html", {
        "titulo": titulo,
        "colunas": colunas,
        "linhas": [(item.id, linha(item)) for item in itens],
        **urls,
    })


def _mostrar_formulario(request, repository, form_class, converter, initial, titulo, list_url, id=None):
    item = repository.obter_por_id(id) if id is not None else None
    if id is not None and item is None:
        raise Http404("Registro não encontrado")

    form = form_class(
        request.POST if request.method == "POST" else None,
        initial=initial(item) if item else None,
    )
    if request.method == "POST" and form.is_valid():
        try:
            entidade = converter(form.cleaned_data, id)
            if id is None:
                repository.incluir(entidade)
                messages.success(request, "Registro criado com sucesso.")
            else:
                repository.alterar(entidade)
                messages.success(request, "Registro atualizado com sucesso.")
            return redirect(list_url)
        except (IntegrityError, ValueError):
            form.add_error(None, "Não foi possível salvar: verifique os dados e os vínculos informados.")

    return render(request, "core/form.html", {
        "titulo": titulo,
        "form": form,
        "editando": id is not None,
        "list_url": list_url,
    })


def _confirmar_exclusao(request, repository, titulo, list_url, id):
    item = repository.obter_por_id(id)
    if item is None:
        raise Http404("Registro não encontrado")
    if request.method == "POST":
        try:
            repository.excluir(id)
            messages.success(request, "Registro excluído com sucesso.")
        except ProtectedError:
            messages.error(request, "Este registro está relacionado a outros e não pode ser excluído.")
        return redirect(list_url)
    return render(request, "core/confirm_delete.html", {
        "titulo": titulo,
        "entidade": item,
        "list_url": list_url,
    })


class InicioView(View):
    def get(self, request):
        recursos = (
            ("core:categoria_list", "Categorias"),
            ("core:produto_list", "Produtos"),
            ("core:venda_list", "Vendas"),
            ("core:pagamento_list", "Formas de pagamento"),
            ("core:item_venda_list", "Itens de venda"),
        )
        return render(request, "core/index.html", {"recursos": recursos})


class CategoriaView(View):
    acao = ""
    list_url = "core:categoria_list"
    def repository(self):
        return CategoriaRepository(CategoriaDAO_ORM(ConexaoBD_ORM()))

    def get(self, request, id=None):
        if self.acao == "listar": return self.listar(request)
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def post(self, request, id=None):
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def listar(self, request):
        return _mostrar_lista(request, "Categorias", ("ID", "Tipo", "Descrição", "Margem (%)"),
            self.repository().listar(), lambda item: (item.tipo_categoria, item.descricao, item.margem_lucro), {
                "create_url": "core:categoria_create", "update_url": "core:categoria_update",
                "delete_url": "core:categoria_delete"})

    def criar(self, request):
        return _mostrar_formulario(request, self.repository(), CategoriaForm,
            lambda dados, id: CategoriaModel(id, dados["tipo_categoria"], dados["descricao"], dados["margem_lucro"]),
            vars, "Categorias", self.list_url)

    def editar(self, request, id):
        return _mostrar_formulario(request, self.repository(), CategoriaForm,
            lambda dados, pk: CategoriaModel(pk, dados["tipo_categoria"], dados["descricao"], dados["margem_lucro"]),
            vars, "Categorias", self.list_url, id)

    def excluir(self, request, id):
        return _confirmar_exclusao(request, self.repository(), "Categorias", self.list_url, id)


class ProdutoView(View):
    acao = ""
    list_url = "core:produto_list"
    def repository(self):
        return ProdutoRepository(ProdutoDAO_ORM(ConexaoBD_ORM()))

    def get(self, request, id=None):
        if self.acao == "listar": return self.listar(request)
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def post(self, request, id=None):
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def listar(self, request):
        return _mostrar_lista(request, "Produtos", ("ID", "Nome", "Descrição", "Preço (R$)", "Estoque", "Categoria"),
            self.repository().listar(), lambda item: (item.nome, item.descricao, item.preco,
                item.quantidade_estoque, item.categoria.descricao), {
                "create_url": "core:produto_create", "update_url": "core:produto_update",
                "delete_url": "core:produto_delete"})

    def criar(self, request):
        return _mostrar_formulario(request, self.repository(), ProdutoForm, _produto,
            lambda item: None, "Produtos", self.list_url)

    def editar(self, request, id):
        initial = lambda item: {"nome": item.nome, "descricao": item.descricao, "preco": item.preco,
            "quantidade_estoque": item.quantidade_estoque, "alerta_estoque_baixo": item.alerta_estoque_baixo,
            "codigo_interno": item.codigo_interno, "margem_lucro": item.margem_lucro,
            "categoria": item.categoria.id}
        return _mostrar_formulario(request, self.repository(), ProdutoForm, _produto,
            initial, "Produtos", self.list_url, id)

    def excluir(self, request, id):
        return _confirmar_exclusao(request, self.repository(), "Produtos", self.list_url, id)


class VendaView(View):
    acao = ""
    list_url = "core:venda_list"
    def repository(self):
        return VendaRepository(VendaDAO_ORM(ConexaoBD_ORM()))

    def get(self, request, id=None):
        if self.acao == "listar": return self.listar(request)
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def post(self, request, id=None):
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def listar(self, request):
        return _mostrar_lista(request, "Vendas", ("ID", "Data e hora", "Desconto (R$)"),
            self.repository().listar(), lambda item: (item.datahora_venda or "—", item.desconto), {
                "create_url": "core:venda_create", "update_url": "core:venda_update",
                "delete_url": "core:venda_delete"})

    def criar(self, request):
        return _mostrar_formulario(request, self.repository(), VendaForm,
            lambda dados, id: VendaModel(id=id, desconto=dados["desconto"]),
            lambda item: {"desconto": item.desconto}, "Vendas", self.list_url)

    def editar(self, request, id):
        return _mostrar_formulario(request, self.repository(), VendaForm,
            lambda dados, pk: VendaModel(id=pk, desconto=dados["desconto"]),
            lambda item: {"desconto": item.desconto}, "Vendas", self.list_url, id)

    def excluir(self, request, id):
        return _confirmar_exclusao(request, self.repository(), "Vendas", self.list_url, id)


class PagamentoView(View):
    acao = ""
    list_url = "core:pagamento_list"
    def repository(self):
        return FormaPagamentoRepository(FormaPagamentoDAO_ORM(ConexaoBD_ORM()))

    def get(self, request, id=None):
        if self.acao == "listar": return self.listar(request)
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def post(self, request, id=None):
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def listar(self, request):
        return _mostrar_lista(request, "Formas de pagamento", ("ID", "Tipo", "Valor pago (R$)", "Venda"),
            self.repository().listar(), lambda item: (item.tipo_pagamento.name, item.valor_pago,
                item.venda.id if item.venda else "—"), {
                "create_url": "core:pagamento_create", "update_url": "core:pagamento_update",
                "delete_url": "core:pagamento_delete"})

    def _converter(self, dados, id=None):
        return FormaPagamentoModel(id=id, tipo_pagamento=TipoPagamento(int(dados["tipo_pagamento"])),
            valor_pago=dados["valor_pago"], venda=_venda(dados))

    def _initial(self, item):
        return {"tipo_pagamento": int(item.tipo_pagamento), "valor_pago": item.valor_pago,
            "venda": item.venda.id if item.venda else None}

    def criar(self, request):
        return _mostrar_formulario(request, self.repository(), FormaPagamentoForm,
            self._converter, self._initial, "Formas de pagamento", self.list_url)

    def editar(self, request, id):
        return _mostrar_formulario(request, self.repository(), FormaPagamentoForm,
            self._converter, self._initial, "Formas de pagamento", self.list_url, id)

    def excluir(self, request, id):
        return _confirmar_exclusao(request, self.repository(), "Formas de pagamento", self.list_url, id)


class ItemVendaView(View):
    acao = ""
    list_url = "core:item_venda_list"
    def repository(self):
        return VendaProdutoRepository(VendaProdutoDAO_ORM(ConexaoBD_ORM()))

    def get(self, request, id=None):
        if self.acao == "listar": return self.listar(request)
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def post(self, request, id=None):
        if self.acao == "excluir": return self.excluir(request, id)
        if self.acao == "editar": return self.editar(request, id)
        return self.criar(request)

    def listar(self, request):
        return _mostrar_lista(request, "Itens de venda", ("ID", "Venda", "Produto", "Quantidade", "Preço na venda (R$)"),
            self.repository().listar(), lambda item: (item.venda.id, item.produto.nome,
                item.quantidade_vendida, item.preco_momento_venda), {
                "create_url": "core:item_venda_create", "update_url": "core:item_venda_update",
                "delete_url": "core:item_venda_delete"})

    def _converter(self, dados, id=None):
        return VendaProduto(id=id, quantidade_vendida=dados["quantidade_vendida"],
            preco_momento_venda=dados["preco_momento_venda"], venda=_venda(dados),
            produto=ProdutoModel(id=dados["produto"].pk))

    def _initial(self, item):
        return {"venda": item.venda.id, "produto": item.produto.id,
            "quantidade_vendida": item.quantidade_vendida,
            "preco_momento_venda": item.preco_momento_venda}

    def criar(self, request):
        return _mostrar_formulario(request, self.repository(), VendaProdutoForm,
            self._converter, self._initial, "Itens de venda", self.list_url)

    def editar(self, request, id):
        return _mostrar_formulario(request, self.repository(), VendaProdutoForm,
            self._converter, self._initial, "Itens de venda", self.list_url, id)

    def excluir(self, request, id):
        return _confirmar_exclusao(request, self.repository(), "Itens de venda", self.list_url, id)
