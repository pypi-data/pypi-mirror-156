from .base import BaseMiner

class NEclatClosed(BaseMiner):
    min_support: float

    def arguments(self) -> list[str]:
        return [f"{int(self.min_support * 100)}%"]
