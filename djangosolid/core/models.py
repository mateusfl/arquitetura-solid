from django.db import models


class Categoria(models.Model):
    tipo_categoria = models.PositiveSmallIntegerField()
    descricao = models.CharField(max_length=120)
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return self.descricao


class Venda(models.Model):
    datahora_venda = models.DateTimeField(auto_now_add=True)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class FormaPagamento(models.Model):
    class Tipo(models.IntegerChoices):
        PIX = 1, "Pix"
        CREDITO = 2, "Crédito"
        DEBITO = 3, "Débito"
        ESPECIE = 4, "Espécie"

    tipo_pagamento = models.PositiveSmallIntegerField(choices=Tipo.choices)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    venda = models.ForeignKey(Venda, on_delete=models.PROTECT, related_name="pagamentos")


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    alerta_estoque_baixo = models.PositiveIntegerField(default=0)
    codigo_interno = models.CharField(max_length=64, unique=True)
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
    )

    def __str__(self) -> str:
        return self.nome


class VendaProduto(models.Model):
    quantidade_vendida = models.PositiveIntegerField()
    preco_momento_venda = models.DecimalField(max_digits=10, decimal_places=2)
    venda = models.ForeignKey(Venda, on_delete=models.PROTECT, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="itens_vendidos")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("venda", "produto"),
                name="unique_produto_por_venda",
            )
        ]
