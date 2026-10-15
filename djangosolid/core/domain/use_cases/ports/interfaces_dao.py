from abc import ABC, abstractmethod
from typing import Any


class ICrudDAO(ABC):
    """Porta de persistencia. Sua implementacao pertence ao adaptador externo."""

    @abstractmethod
    def incluir(self, obj: Any) -> Any: ...

    @abstractmethod
    def alterar(self, obj: Any) -> Any: ...

    @abstractmethod
    def excluir(self, id: int) -> None: ...

    @abstractmethod
    def obter_por_id(self, id: int) -> Any | None: ...

    @abstractmethod
    def listar(self) -> list[Any]: ...
