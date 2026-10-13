from django.db import models


class Categoria(models.Model):
    id = models.IntegerField()
    tipo_categoria = models.IntegerField()
    descricao = models.CharField()
    margem_lucro = models.FloatField()


class Venda(models.Model):
    id = models.IntegerField()
    datahora_venda = models.DateTimeField()
    desconto = models.FloatField()


TIPO_PAGAMENTO_CHOICES = (
    (1, "Pix"),
    (2, "Crédito"),
    (3, "Débito"),
    (3, "Espécie"),
)


class FormaPagamento(models.Model):
    id = models.IntegerField()
    tipo_pagamento = models.IntegerField(choices=TIPO_PAGAMENTO_CHOICES)
    valor_pago = models.FloatField()
    venda = models.ForeignKey(Venda, on_delete=models.PROTECT)


class Produto(models.Model):
    id = models.IntegerField()
    nome = models.CharField()
    descricao = models.CharField()
    preco = models.FloatField()
    quantidade_estoque = models.IntegerField()
    alerta_estoque_baixo = models.IntegerField()
    codigo_interno = models.CharField()
    margem_lucro = models.FloatField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)


class VendaProduto(models.Model):
    quantidade_vendida = models.IntegerField()
    preco_momento_venda = models.FloatField()
    venda = models.ForeignKey(Venda, on_delete=models.PROTECT)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
