from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class IConexaoBD(ABC):
    DB_ALIAS: str

    @abstractmethod
    def obter_conexao(self):
        """Retorna a conexão Django configurada para o alias do app."""


class InterfaceDAO(ABC, Generic[T]):
    """Contrato CRUD comum aos DAOs e repositórios por entidade."""

    @abstractmethod
    def incluir(self, entidade: T) -> T:
        """Insere uma entidade e retorna a versão persistida."""

    @abstractmethod
    def alterar(self, entidade: T) -> T:
        """Atualiza uma entidade existente e retorna a versão persistida."""

    @abstractmethod
    def excluir(self, id: int) -> None:
        """Exclui uma entidade pela chave primária."""

    @abstractmethod
    def obter_por_id(self, id: int) -> T | None:
        """Busca uma entidade pela chave primária."""

    @abstractmethod
    def listar(self) -> list[T]:
        """Retorna as entidades persistidas."""
