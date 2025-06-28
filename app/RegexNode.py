
from collections import defaultdict


class RegexNode:
    """Représente un nœud dans l'arbre syntaxique de la regex"""
    pass

class SymbolNode(RegexNode):
    def __init__(self, symbol: str):
        self.symbol = symbol

class ConcatNode(RegexNode):
    def __init__(self, left: RegexNode, right: RegexNode):
        self.left = left
        self.right = right

class UnionNode(RegexNode):
    def __init__(self, left: RegexNode, right: RegexNode):
        self.left = left
        self.right = right

class StarNode(RegexNode):
    def __init__(self, child: RegexNode):
        self.child = child

class PlusNode(RegexNode):
    def __init__(self, child: RegexNode):
        self.child = child

class OptionalNode(RegexNode):
    def __init__(self, child: RegexNode):
        self.child = child


class ASTProperties:
    __slots__ = ('positions', 'first', 'last', 'nullable', 'follow')
    
    def __init__(self):
        self.positions = {}     # Map: position -> symbol
        self.first = set()      # Set of starting positions
        self.last = set()       # Set of ending positions
        self.nullable = False   # Can match empty string?
        self.follow = defaultdict(set)  # Map: position -> set of following positions

