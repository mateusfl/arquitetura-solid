from django import forms

from app_django.models import Categoria, Produto, Venda


DB_ALIAS = "db_solid"


class CategoriaForm(forms.Form):
    tipo_categoria = forms.IntegerField(label="Tipo da categoria", min_value=0)
    descricao = forms.CharField(label="Descrição", max_length=120)
    margem_lucro = forms.DecimalField(
        label="Margem de lucro (%)", max_digits=5, decimal_places=2, min_value=0
    )


class VendaForm(forms.Form):
    desconto = forms.DecimalField(
        label="Desconto (R$)", max_digits=10, decimal_places=2, min_value=0
    )


class ProdutoForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=150)
    descricao = forms.CharField(label="Descrição", max_length=255)
    preco = forms.DecimalField(
        label="Preço (R$)", max_digits=10, decimal_places=2, min_value=0
    )
    quantidade_estoque = forms.IntegerField(label="Quantidade em estoque", min_value=0)
    alerta_estoque_baixo = forms.IntegerField(label="Alerta de estoque baixo", min_value=0)
    codigo_interno = forms.CharField(label="Código interno", max_length=64)
    margem_lucro = forms.DecimalField(
        label="Margem de lucro (%)", max_digits=5, decimal_places=2, min_value=0
    )
    categoria = forms.ModelChoiceField(
        label="Categoria",
        queryset=Categoria.objects.using(DB_ALIAS).order_by("descricao"),
    )


class FormaPagamentoForm(forms.Form):
    tipo_pagamento = forms.ChoiceField(
        label="Forma de pagamento",
        choices=((1, "Pix"), (2, "Crédito"), (3, "Débito"), (4, "Espécie")),
    )
    valor_pago = forms.DecimalField(
        label="Valor pago (R$)", max_digits=10, decimal_places=2, min_value=0
    )
    venda = forms.ModelChoiceField(
        label="Venda",
        queryset=Venda.objects.using(DB_ALIAS).order_by("-datahora_venda"),
    )


class VendaProdutoForm(forms.Form):
    venda = forms.ModelChoiceField(
        label="Venda",
        queryset=Venda.objects.using(DB_ALIAS).order_by("-datahora_venda"),
    )
    produto = forms.ModelChoiceField(
        label="Produto",
        queryset=Produto.objects.using(DB_ALIAS).order_by("nome"),
    )
    quantidade_vendida = forms.IntegerField(label="Quantidade vendida", min_value=1)
    preco_momento_venda = forms.DecimalField(
        label="Preço unitário na venda (R$)",
        max_digits=10,
        decimal_places=2,
        min_value=0,
    )
