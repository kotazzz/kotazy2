from rich import print


def tokenize(text):
    token = lambda t, v: {"type": t, "value": v}
    tokens = []
    state = "start"
    value = ""

    def process_char(char):
        nonlocal state, value, tokens, token
        if char == ";":
            state = "start"
        if state == "start":
            if char.isalpha():
                state = "name"
                value = char
            elif char.isdigit():
                state = "number"
                value = char
            elif char in ["(", ")", "{", "}", ">", "$", "."]:
                tokens.append(token(char, char))
            elif char == '"':
                state = "string"
        elif state == "string":
            if char != '"':
                value += char
            else:
                tokens.append(token("string", value))
                state, value = "start", ""
        elif state == "name":
            if char.isalpha() or char.isdigit() or char == "_":
                value += char
            else:
                tokens.append(token("name", value))
                state, value = "start", ""
                process_char(char)
        elif state == "number":
            if char.isdigit():
                value += char
            else:
                tokens.append(token("number", value))
                state, value = "start", ""
                process_char(char)

    for char in text:
        process_char(char)
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens + [{"type": "EOF", "value": "EOF"}]

    def consume(self, *types):
        if not types:
            return self.tokens.pop(0)

        token = self.tokens.pop(0)
        if token["type"] in types:
            return token
        else:
            print("---")
            print("NEXT:", " ".join(i["value"] for i in [token] + self.tokens[:5]))
            print(f"EXPECTED: {types} | GOT: {token}")
            exit(-1)

    def preview(self, *types):
        token = self.tokens[0]
        if not types:
            return token
        if token["type"] in types:
            return token
        else:
            return False

    def parse_expression(self, close=None):
        c = self.consume
        p = self.preview

        tree_children = []

        
            
        if p("number"):
            tree = int(c()["value"])
        elif p("string"):
            tree = c()["value"]
        else:
                
                
            tree = {
                "name": c("name")["value"],
                "children": tree_children,
            }
            while p("(", "{"):
                if p("("):
                    c()
                    args_children = []
                    args = {"type": "args", "value": args_children}

                    while not p(")"):
                        child = self.parse_expression()
                        args_children.append(child)
                    c()

                    tree_children.append(args)
                elif p("{"):
                    c()
                    args_children = []
                    args = {"type": "body", "value": args_children}

                    while not p("}"):
                        child = self.parse_expression()
                        args_children.append(child)
                    c()

                    tree_children.append(args)
            
                

        if p("$", ">"):
            t = c()
            expr = self.parse_expression()
            if t["value"] == ">":
                expr, tree = tree, expr
            tree = {
                "name": tree["name"],
                "children": [*tree["children"], {"type": "args", "value": [expr]}],
            }
        if p("."):
            c()
            # a . b
            expr = self.parse_expression()  # b
            args_kw = {"name": "_a", "children": []}

            if isinstance(expr, dict) and expr["name"] == "_":
                # Оптимизация множественной композиции
                inner = expr["children"][1]["value"][0]
                tree["children"].append({"type": "args", "value": [inner]})  # a(_a)
            else:

                expr["children"].append({"type": "args", "value": [args_kw]})  # a(_a)
                tree["children"].append({"type": "args", "value": [expr]})  # b(a(_a))
            # Создание функции-обертки
            tree = {
                "name": "_",
                "children": [
                    {"type": "args", "value": [args_kw]},
                    {"type": "body", "value": [tree]},
                ],
            }
            

        return tree


def build_tree(c):
    return Parser(tokenize(c)).parse_expression()


def unparse(expr):
    text = ""
    if isinstance(expr, dict):
        if "name" in expr:
            text += expr["name"]
            for c in expr["children"]:
                text += unparse(c)
        if "type" in expr:
            if expr["type"] == "args":
                text += "("
                for v in expr["value"]:
                    text += unparse(v) + " "
                text += ")"
            if expr["type"] == "body":
                text += "{"
                for v in expr["value"]:
                    text += unparse(v) + " "
                text += "}"
    elif isinstance(expr, int):
        text += str(expr)
    elif isinstance(expr, str):
        text += repr(expr)
    return text.replace(" )", ")").replace(" }", "}")


class Program:
    def __init__(self, code):
        self.tree = build_tree(code)


tree = Program(
    """
test(){
    a . b
}
"""
).tree
print(tree)
print(unparse(tree))
