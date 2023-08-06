import abc
from functools import reduce
from typing import Any, Callable, Iterable, List

class Pipeline(abc.ABC):
    def __init__(self, target:Any, items:Iterable[Any]):
        self.target = target
        self.items = items

    @abc.abstractmethod
    def run():
        pass

class ReducerPipeline(Pipeline):
    """
    It implements a Pipeline receiving just one item and passing it through multiple functions.
    The output of the previous function is the input of the following one.
    Ex: 
        text = "Olá, quem é você?"
        function_list = [to_lower, remove_accentuation, remove_punctuation]
    Pipeline: 
        "Olá, quem é você?" -> "olá, quem é você" -> "ola, quem e voce?" -> "ola quem e voce"
        output = "ola quem e voce"
    """
    def run(self)->Any:
        item:Any = self.target
        func_list:Iterable[Callable] = self.items
        output = reduce(
            lambda value, func: func(value),
            func_list,
            item,
        )
        return output

class MapperPipeline(Pipeline):
    """
    It implements a Pipeline receiving just one function and passing it through multiple items.
    The output of each function run is stored in a list of the same size of the input.
    Ex: 
        function = remove_accentuation
        text_list = ["Hortência", "Sebastião", "José"]
    Pipeline: 
        remove_accentuation("Hortência") -> remove_accentuation("Sebastião") -> remove_accentuation("José")
        output = ["Hortencia", "Sebastiao", "Jose"]
    """
    def run(self)->List[Any]:
        func:Callable = self.target
        items:Iterable = self.items
        output = list(map(lambda item: func(item), items))
        return output
