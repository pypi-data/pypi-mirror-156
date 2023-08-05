from dynamic_imports.tests.test_pkg.base import Base


class C1(Base):
    def __init__(self) -> None:
        super().__init__()


class C2(Base):
    def __init__(self) -> None:
        super().__init__()


c22 = C2()
