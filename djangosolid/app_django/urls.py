from django.urls import path

from app_django.views import (
    CategoriaView,
    InicioView,
    ItemVendaView,
    PagamentoView,
    ProdutoView,
    VendaView,
)

app_name = "core"

urlpatterns = [
    path("", InicioView.as_view(), name="inicio"),
    path("categorias/", CategoriaView.as_view(acao="listar"), name="categoria_list"),
    path("categorias/novo/", CategoriaView.as_view(acao="criar"), name="categoria_create"),
    path("categorias/<int:id>/editar/", CategoriaView.as_view(acao="editar"), name="categoria_update"),
    path("categorias/<int:id>/excluir/", CategoriaView.as_view(acao="excluir"), name="categoria_delete"),
    path("produtos/", ProdutoView.as_view(acao="listar"), name="produto_list"),
    path("produtos/novo/", ProdutoView.as_view(acao="criar"), name="produto_create"),
    path("produtos/<int:id>/editar/", ProdutoView.as_view(acao="editar"), name="produto_update"),
    path("produtos/<int:id>/excluir/", ProdutoView.as_view(acao="excluir"), name="produto_delete"),
    path("vendas/", VendaView.as_view(acao="listar"), name="venda_list"),
    path("vendas/novo/", VendaView.as_view(acao="criar"), name="venda_create"),
    path("vendas/<int:id>/editar/", VendaView.as_view(acao="editar"), name="venda_update"),
    path("vendas/<int:id>/excluir/", VendaView.as_view(acao="excluir"), name="venda_delete"),
    path("pagamentos/", PagamentoView.as_view(acao="listar"), name="pagamento_list"),
    path("pagamentos/novo/", PagamentoView.as_view(acao="criar"), name="pagamento_create"),
    path("pagamentos/<int:id>/editar/", PagamentoView.as_view(acao="editar"), name="pagamento_update"),
    path("pagamentos/<int:id>/excluir/", PagamentoView.as_view(acao="excluir"), name="pagamento_delete"),
    path("itens-venda/", ItemVendaView.as_view(acao="listar"), name="item_venda_list"),
    path("itens-venda/novo/", ItemVendaView.as_view(acao="criar"), name="item_venda_create"),
    path("itens-venda/<int:id>/editar/", ItemVendaView.as_view(acao="editar"), name="item_venda_update"),
    path("itens-venda/<int:id>/excluir/", ItemVendaView.as_view(acao="excluir"), name="item_venda_delete"),
]
