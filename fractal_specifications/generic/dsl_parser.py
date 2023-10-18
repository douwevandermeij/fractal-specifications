from lark import Transformer

from fractal_specifications.generic.collections import AndSpecification, OrSpecification
from fractal_specifications.generic.operators import (
    ContainsSpecification,
    EqualsSpecification,
    GreaterThanEqualSpecification,
    GreaterThanSpecification,
    InSpecification,
    IsNoneSpecification,
    LessThanEqualSpecification,
    LessThanSpecification,
    NotEqualsSpecification,
    NotSpecification,
    RegexStringMatchSpecification,
)
from fractal_specifications.generic.specification import EmptySpecification

grammar = r"""
    ?start: expression
    expression: and_expression | or_expression | comparison_expression
    or_expression: expression ("||" comparison_expression)+
    and_expression: expression ("&&" comparison_expression)+
    comparison_expression: field_name comparison_operator field_value
        | atom_expression -> atom_expression
        | not_expression -> atom_expression
        | field_name "in" "[" field_values "]" -> in_expression
        | field_name "matches" string_value -> match_expression
        | field_name "is" "None" -> is_none_expression
        | field_name "contains" field_value -> contains_expression
        | empty_expression
    empty_expression: "#"
    not_expression: "!" atom_expression
    atom_expression: "(" expression ")"
    field_values: (field_value ",")* field_value?
    field_value: string_value | number_value | boolean_value | none_value
    comparison_operator: "==" -> eq_op
        | "!=" -> neq_op
        | "<" -> lt_op
        | "<=" -> lte_op
        | ">" -> gt_op
        | ">="-> gte_op
    field_name: CNAME ("." CNAME)*
    string_value: ESCAPED_STRING | DOUBLE_QUOTED_STRING | SINGLE_QUOTED_STRING
    number_value: SIGNED_FLOAT | SIGNED_INT
    boolean_value: "True" -> true | "False" -> false
    none_value: "None" -> none
    DOUBLE_QUOTED_STRING  : /"[^"]*"/
    SINGLE_QUOTED_STRING  : /'[^']*'/
    %import common.ESCAPED_STRING
    %import common.SIGNED_FLOAT
    %import common.SIGNED_INT
    %import common.CNAME
    %import common.WS
    %ignore WS
"""


class DSLTransformer(Transformer):
    def expression(self, items):
        return items[0]

    def and_expression(self, items):
        return AndSpecification(items)

    def or_expression(self, items):
        return OrSpecification(items)

    def not_expression(self, items):
        return NotSpecification(items[0])

    def comparison_expression(self, items):
        from fractal_specifications.generic.specification import Specification

        if issubclass(type(items[0]), Specification):
            return items[0]
        field_name, op, value = items
        if op == "==":
            return EqualsSpecification(field_name, value)
        elif op == "!=":
            return NotEqualsSpecification(field_name, value)
        elif op == "<":
            return LessThanSpecification(field_name, value)
        elif op == "<=":
            return LessThanEqualSpecification(field_name, value)
        elif op == ">":
            return GreaterThanSpecification(field_name, value)
        elif op == ">=":
            return GreaterThanEqualSpecification(field_name, value)

    def empty_expression(self, items):
        return EmptySpecification()

    def atom_expression(self, items):
        return items[0]

    def eq_op(self, items):
        return "=="

    def neq_op(self, items):
        return "!="

    def lt_op(self, items):
        return "<"

    def lte_op(self, items):
        return "<="

    def gt_op(self, items):
        return ">"

    def gte_op(self, items):
        return ">="

    def in_expression(self, items):
        field_name, values = items
        return InSpecification(field_name, values)

    def match_expression(self, items):
        field_name, value = items
        return RegexStringMatchSpecification(field_name, value)

    def contains_expression(self, items):
        field_name, value = items
        return ContainsSpecification(field_name, value)

    def field_name(self, items):
        return ".".join(items)

    def is_none_expression(self, items):
        return IsNoneSpecification(items[0])

    def field_values(self, tokens):
        return tokens

    def field_value(self, tokens):
        token = tokens[0]
        if token is None:
            return None
        elif type(token) is str:
            return token
        elif type(token) is bool:
            return token
        elif token.type == "SIGNED_INT":
            return int(token)
        elif token.type == "SIGNED_FLOAT":
            return float(token)

    def string_value(self, items):
        return str(items[0])[1:-1]

    def number_value(self, items):
        return items[0]

    def true(self, items):
        return True

    def false(self, items):
        return False

    def none(self, items):
        return None
