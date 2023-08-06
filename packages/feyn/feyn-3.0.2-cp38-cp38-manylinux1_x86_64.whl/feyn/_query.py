import random
from typing import List, Tuple
from ._program import Program
import os

from lark import Lark, Tree, Token

DIR, _ = os.path.split(__file__)
QUERY_GRAMMAR = os.path.join(DIR, "qlang/query_grammar.lark")

PARSER = Lark.open(QUERY_GRAMMAR, start="expr", parser="lalr")

SPECIAL_OPCODES = {
    "register_any": 0,
    "interact1": 1,
    "interact2": 2,
    "wildcard": 3,
    "exclude": 4,
    # 50-80 are also reserved
}
class Parser:
    @staticmethod
    def _translate_ast(context, ast) -> int:
        """Translate a node in a lark AST to an opcode."""
        if isinstance(ast, Token):
            term_name = ast.value.strip("\"'")
            if term_name not in context.registers:
                raise ValueError(f"Input '{term_name}' in query but not in input_names.")
            return context.lookup_by_fname(term_name, 0)

        dat = ast.data
        special_code = SPECIAL_OPCODES.get(dat)
        if special_code is not None:
            return special_code
        if dat == "expr":
            return context.lookup_by_fname("add", 2)
        if dat == "term":
            return context.lookup_by_fname("multiply", 2)

        if dat == "gaussian":
            dat += str(len(ast.children))

        return context.lookup_by_fname(dat, len(ast.children))

    @staticmethod
    def query_to_codes(context, output_name: str, user_query: str) -> Tuple[int, List[int]]:
        """Convert a user-written query into the program representation."""
        res_codes = [context.lookup_by_fname(output_name, 0)]
        min_complexity = 0

        ast = PARSER.parse(user_query)

        def _recurse(node):
            nonlocal res_codes, min_complexity
            if isinstance(node, Tree) and node.data == "wildcard":
                wc_codes = [SPECIAL_OPCODES["wildcard"]]
                max_wc_complexity = 80
                wc_terms = set()
                wc_banned = set()

                for child in node.children:
                    if isinstance(child, Tree):
                        wc_codes.append(SPECIAL_OPCODES["exclude"])
                        term_code = Parser._translate_ast(context, child.children[0])
                        wc_banned.add(term_code)
                        wc_codes.append(term_code)
                    elif child.type in ["SINGLE_ESCAPED_STRING", "DOUBLE_ESCAPED_STRING"]:
                        term_name = child.value.strip("\"'")
                        if term_name not in context.registers:
                            raise ValueError(f"Input '{term_name}' in query but not in input_names.")
                        term_code = context.lookup_by_fname(term_name, 0)
                        wc_terms.add(term_code)
                        wc_codes.append(term_code)
                    else:
                        max_wc_complexity = min(int(child.value) + 50, 80)

                wc_codes.append(max_wc_complexity)
                res_codes += wc_codes

                min_wc_complexity = max(1, 2 * (len(wc_terms) - 1))
                complexity_diff = min_wc_complexity - (max_wc_complexity - 50)
                if complexity_diff > 0:
                    raise ValueError(
                        f"\n\nToo much complexity requested in wildcard subtree. Either increase the allowed complexity (currently {max_wc_complexity-50}) or remove {complexity_diff} input(s) from the wildcard."
                    )
                inconsistent = [context.registers[c - 10000] for c in wc_terms.intersection(wc_banned)]
                if inconsistent:
                    msg = "Inconsistent required inclusion and exclusion of terminal"
                    if len(inconsistent) >= 2:
                        msg += "s"
                    msg += " " + ", ".join([f"'{t}'" for t in inconsistent]) + "."
                    raise ValueError(msg)
                min_complexity += min_wc_complexity
                return

            min_complexity += 1
            res_codes.append(Parser._translate_ast(context, node))
            if isinstance(node, Tree):
                nchildren = len(node.children)
                if nchildren:
                    _recurse(node.children[0])
                if nchildren == 2:
                    _recurse(node.children[1])
                if nchildren > 2:
                    _recurse(Tree(node.data, node.children[1:]))

        _recurse(ast)
        return min_complexity, res_codes

class Query:
    def __init__(self, context, query_string: str, max_complexity, input_names, function_names, output_name):
        self.ar0_codes = context.get_codes(0, input_names)
        self.ar1_codes = context.get_codes(1, function_names)
        self.ar2_codes = context.get_codes(2, function_names)
        self.output_code = context.lookup_by_fname(output_name, 0)

        self.max_complexity = max_complexity
        query_complexity, query_codes = Parser.query_to_codes(context, output_name, query_string)

        if query_complexity > max_complexity:
            raise ValueError(
                f"The complexity of the query, {query_complexity}, is greater than the max_complexity {max_complexity} of this sample_models."
            )

        self.query_codes = query_codes
        self.query_size = len(query_codes)

        self.output_code = query_codes[0]

    def __call__(self, p: Program) -> bool:
        """Match programs p to this query sequence."""

        plen = len(p)
        ixP = 0
        ixQP = 0
        while 1:
            if ixQP >= self.query_size and ixP >= plen:
                return True

            qcode = self.query_codes[ixQP]

            if qcode == 0:
                if not p.arity_at(ixP) == 0:
                    return False
            elif qcode == 1:
                if not p.arity_at(ixP) == 1:
                    return False
            elif qcode == 2:
                if not p.arity_at(ixP) == 2:
                    return False

            elif qcode == 3:
                offset = self._consume_wildcard(self.query_codes[ixQP:])
                ixQP += offset

                st_end = p.find_end(ixP)
                program_subtree = p._codes[ixP:st_end]
                ixP = st_end - 1
                if len(program_subtree) - 1 > self.n_edges:
                    return False

                subtree_terminals = set(filter(lambda code: Program.arity_of(1, code) == 0, program_subtree))
                if self.must_contain.difference(subtree_terminals):
                    return False
                if self.cant_contain.intersection(subtree_terminals):
                    return False

            elif qcode == 4:
                ixQP += 1
                banned_terminal = self.query_codes[ixQP]
                if not p.arity_at(ixP) == 0:
                    return False
                if p[ixP] == banned_terminal:
                    return False

            else:
                if not qcode == p[ixP]:
                    return False

            ixP += 1
            ixQP += 1

        return True

    def partial_codes(self) -> List:
        """Return a partially filled out code sequence for the QCell to complete.
        The complete program is always expected to match the user query.

        The partially filled out code sequence either has elements (op_codes, reg_codes) or (None, None)."""
        res = []
        ix = 0
        while ix < len(self.query_codes):
            code = self.query_codes[ix]

            if code == 0:
                res.append(([], self.ar0_codes))
            elif code == 1:
                res.append((self.ar1_codes, []))
            elif code == 2:
                res.append((self.ar2_codes, []))

            elif code == 3:
                ix += self._consume_wildcard(self.query_codes[ix:])
                if self.must_contain:
                    available_terms = set(random.choices(self.ar0_codes, k=max(len(self.must_contain), 30)))
                    available_terms = list(available_terms.union(self.must_contain).difference(self.cant_contain))
                    available_codes = self.ar1_codes + self.ar2_codes
                else:
                    available_codes, available_terms = None, None

                min_size = 2 * (len(self.must_contain) - 1)
                max_size = min(10, self.n_edges)
                subtree_size = random.randint(min_size, max_size)
                res.extend([(available_codes, available_terms)] * subtree_size)

            elif code == 4:
                ix += 1
                available = self.ar0_codes[:]
                available.remove(self.query_codes[ix])
                res.append(([], available))

            else:
                a = code // 1000
                a = 0 if a >= 10 else a
                if a:
                    res.append(([code], []))
                else:
                    res.append(([], [code]))

            ix += 1

        return res + [(None, None)] * (Program.SIZE - len(res))

    def _consume_wildcard(self, codes):
        self.must_contain = set()
        self.cant_contain = set()
        ix = 1
        while 1:
            code = codes[ix]
            if code >= 50 and code <= 80:
                self.n_edges = code - 50
                break

            if code == 4:
                self.cant_contain.add(codes[ix + 1])
                ix += 2
                continue

            self.must_contain.add(codes[ix])
            ix += 1

        return ix + 1
