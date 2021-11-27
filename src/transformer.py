from lark import Lark, Transformer, v_args

class ToPythonSource(Transformer):

    def start(self, args):
        args[0] = f"from archetype import Archetype, header\nclass {args[0]}(Archetype):\n"
        if args[1].data == 'parameters' and len(args[1].children) > 0:
            args[1] = f"    def __init__(self, {args[1].children[0].value}):\n        self.{args[1].children[0].value} = {args[1].children[0].value}\n"
        return "".join(args)
    
    def entry(self, args):
        transferred_in_rule = False
        indent_effect = False
        for index, arg in enumerate(args):
            if hasattr(arg, 'data') and arg.data == 'require':
                for ar in arg.children:
                    if ar.__contains__("transferred"):
                        transferred_in_rule = True
                indent_effect = True
                args[index] = f"        if {' and '.join(arg.children)}:\n"
        for index, arg in enumerate(args):
            if hasattr(arg, 'data') and arg.data == 'transfer':
                args[index] = f'        self.transfer({"".join(arg.children)})'
            if hasattr(arg, 'data') and arg.data == 'effect':
                if indent_effect:
                    args[index] = "        " + "        ".join(arg.children)
                else:
                    args[index] = "    " + "    ".join(arg.children)
        
        if hasattr(args[1], 'data') and args[1].data == 'parameters' and len(args[1].children) > 0:
            if transferred_in_rule:
                args[1] = f", {args[1].children[0].value}, transferred):\n"
                args[0] = f"    @header\n{args[0]}"
            else:
                args[1] = f", {args[1].children[0].value}):\n"
        else:
            if transferred_in_rule:
                args[0] = f"    @header\n{args[0]}, transferred):\n"
            else:
                args[0] = f"{args[0]}):\n"
        
        return "".join(args)
        
    def states(self, args):
        states_list = ", ".join(f"'{arg}'" for arg in args)
        return f'        self.states = [{states_list}]\n        self.currentState = "{args[0]}"\n'
    
    def STATE(self, args):
        return args.value
    
    def transition(self, args):
        when_value = ""
        transferred_value = ""
        header_value = ""
        for index, arg in enumerate(args):
            if hasattr(arg, 'data') and arg.data == "when":
                arg_0 = arg.children[0].value if hasattr(arg.children[0], 'value') else arg.children[0]
                arg_2 = arg.children[2].value if hasattr(arg.children[2], 'value') else arg.children[2]
                when_value = f"        if {arg_0} {arg.children[1]} {arg_2}:\n"
                args[index] = ""
                if arg_0 == "transferred" or arg_2 == "transferred":
                    header_value = "    @header\n"
                    transferred_value = ", transferred"
            if hasattr(arg, 'data') and arg.data == "effect":
                for idx, child in enumerate(arg.children):
                    if hasattr(child, 'data') and child.data == "transfer":
                        arg.children[idx] = f'        self.transfer({"".join(child.children)})\n'
                args[index] = f"{''.join(arg.children)}"
        
        indent = "        "
        if when_value != "":
            indent = "            "
        for ix, ar in enumerate(args):
            if hasattr(ar, 'data') and ar.data == "from_":
                args[ix] = f"{indent}self.from_(self.state('{ar.children[0]}'), self.state('{ar.children[1]}'))\n"
        args[0] = f"{header_value}    def {args[0]}(self{transferred_value}):\n{when_value}"
        return "".join(args)
            
    def COMPARATOR(self, args):
        return args.value
    
    def ENTRY_NAME(self, args):
        return f"    def {args.value}(self"
    
    def called_by(self, args):
        return f"        self.called_by('{args[0].value}')\n"
    
    def rule(self, args):
        arg_1 = args[1].value if hasattr(args[1], 'value') else args[1]
        arg_3 = args[3].value if hasattr(args[3], 'value') else args[3]
        if arg_1 == "now":
            arg_1 = "self.now()"
        if arg_3 == "now":
            arg_3 = "self.now()"
        return f"{arg_1} {args[2]} {arg_3}"
        
    def EFFECT_TARGET(self, args):
        return f"    self.{args.value}"
    
    def EFFECT_VALUE(self, args):
        return args.value

    def assignment(self, args):
        return f"{args[0]} = {args[1]}\n"
    
    def sum(self, args):
        return f"({args[0]} + {args[1]})"
    def product(self, args):
        return f"({args[0]} * self.duration_convert({args[1]}))"
    def minus(self, args):
        return f"({args[0]} - {args[1]})"
    def NUMBER(self, args):
        return args.value
    def PERCENT_LIT(self, args):
        return f"{args.value[:-1]} / 100."
    def DURATION(self, args):
        return f"self.parse_timedelta('{args.value}')"
    def DATE(self, args):
        return f"self.strptime('{args.value}', '%Y-%m-%d').date()"
    def NOW(self, args):
        return "self.now()"
    def TRANSITION_NAME(self, args):
        return args.value
    def NAME(self, args):
        if args.value == "now":
            return f"self.now()"
        elif args.value == "transferred":
            return args.value
        else:
            return f"self.{args.value}"
    def START_NAME(self, args):
        return args.value
