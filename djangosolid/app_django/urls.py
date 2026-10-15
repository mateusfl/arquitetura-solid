from django.urls import path

from app_django import views


app_name = "core"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("<str:recurso>/", views.listar, name="listar"),
    path("<str:recurso>/novo/", views.criar, name="criar"),
    path("<str:recurso>/<int:id>/editar/", views.editar, name="editar"),
    path("<str:recurso>/<int:id>/excluir/", views.excluir, name="excluir"),
]
