#
# A very basic and simple example of the Strategy pattern. Code taken from:
#
#       https://auth0.com/blog/strategy-design-pattern-in-python/
#
from abc import ABC, abstractmethod


# The (abstract) Strategy interface
class Strategy(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass


# Concrete strategies

# Strategy A
class ConcreteStrategyA(Strategy):
    def execute(self) -> str:
        return "ConcreteStrategy A.execute()"


# Strategy B
class ConcreteStrategyB(Strategy):
    def execute(self) -> str:
        return "ConcreteStrategy B.execute()"


# Strategy C
class ConcreteStrategyC(Strategy):
    def execute(self) -> str:
        return "ConcreteStrategy C.execute()"


# Default strategy
class DefaultStrategy(Strategy):
    def execute(self) -> str:
        return "DefaultStrategy.execute()"


# Context - the primary class
class Context:
    strategy: Strategy

    def setStrategy(self, strategy: Strategy = None) -> None:
        if strategy is not None:
            self.strategy = strategy
        else:
            self.strategy = DefaultStrategy()

    def executeStrategy(self) -> str:
        print(self.strategy.execute())


if __name__ == "__main__":
    appA = Context()
    appB = Context()
    appC = Context()

    # select and set strategies
    appA.setStrategy(ConcreteStrategyA())
    appB.setStrategy(ConcreteStrategyB())
    # appC.setStrategy()                      # => set DefaultStrategy()

    appA.executeStrategy()
    appB.executeStrategy()
    appC.executeStrategy()
