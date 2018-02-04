import logging
import sys

import random

from exceptions.exceptions import VariableAlreadyDeclared, \
    ConstantAlreadyDeclared, InvalidType, CannotAssignConstant, \
    AssignmentToUndefinedVariable, WrongAssignment, CannotReadArray, \
    VariableUndeclared, UndeclaredSymbol, UnimplementedOperation, SymbolAlreadyInUse, CallWithWrongArity, \
    UndeclaredFunction
from variables.variables import LanceScriptScalarVariable, LanceScriptArrayVariable
from variables.constants import LanceConstant
from functions.functions import LanceFunction, LanceFunctionParameter
from variables.types import VarTypes


class LanceInterpreter:
    def __init__(self, log_level=logging.WARNING, **kwargs):
        self.vars = [{}]
        self.constants = {}
        self.functions = {}
        self.LOG = logging.getLogger("AST2Intermediate")
        self.LOG.setLevel(log_level)
        self.mock_input = kwargs.get('mock_input', False)

    def evaluate(self, tree, variables=None):
        if variables is not None:
            self.vars.append(variables)

        f = getattr(self, tree.data, self.__default__)
        ret = f(tree)

        if variables is not None:
            self.vars.pop()

        return ret

    def __default__(self, tree):
        self.LOG.log(logging.WARNING, "Action %s not implemented", tree.data)
        return tree

    def program(self, tree):
        for child in tree.children:
            if child.data == 'return_stmt':
                return
            else:
                self.evaluate(child)

    def code_block(self, tree):
        for child in tree.children:
            if child.data == 'return_stmt':
                return
            else:
                self.evaluate(child)

    # ------------------ VARIABLES & CONSTANTS ------------------

    def const_decl(self, matches):
        const_name = matches.children[0]
        const_val = self.evaluate(matches.children[1])

        if self.var_is_decl(const_name):
            raise VariableAlreadyDeclared("Symbol %s already used for a variable", const_name)

        if self.const_is_declared(const_name):
            raise ConstantAlreadyDeclared("Cannot redefine constant %s", const_name)

        self.LOG.log(logging.DEBUG, "Declaring constant %s as %s", const_name, const_val)

        self.constants[const_name] = LanceConstant(VarTypes.INT, const_name, const_val)

    def var_decl(self, matches):
        var_type = self.str_to_type(matches.children[0])

        declarations = matches.children[1].children

        for declaration in declarations:
            decl_type = declaration.data
            var_name = declaration.children[0]

            if self.var_is_decl(var_name):
                raise VariableAlreadyDeclared("Cannot declare variable %s twice", var_name)

            if var_name in self.constants:
                raise ConstantAlreadyDeclared("The symbol %s is already defined as constant", var_name)

            if decl_type == 'scalar_declaration':
                self.current_context()[var_name] = LanceScriptScalarVariable(var_name, var_type)

            elif decl_type == 'array_declaration':
                size = self.evaluate(declaration.children[1])
                self.current_context()[var_name] = LanceScriptArrayVariable(var_name, var_type, size)

            elif decl_type == 'declaration_and_assignment':
                value = self.evaluate(declaration.children[1])
                self.current_context()[var_name] = LanceScriptScalarVariable(var_name, var_type, value)

    def scalar_assignment(self, matches):
        var_name = matches.children[0]
        value = self.evaluate(matches.children[1])

        if self.const_is_declared(var_name):
            raise CannotAssignConstant("Trying to assign constant {}", var_name)

        if not self.var_is_decl(var_name):
            raise AssignmentToUndefinedVariable("Variable {} is not declared", var_name)

        if not self.var_is_scalar(var_name):
            raise WrongAssignment("Cannot assign array as scalar")

        self.resolve_scoped_var(var_name).set(value)

    def array_assignment(self, matches):
        var_name = matches.children[0]
        idx = self.evaluate(matches.children[1])
        val = self.evaluate(matches.children[2])

        if self.const_is_declared(var_name):
            raise CannotAssignConstant("Cannot assign constant %s", var_name)

        if not self.var_is_decl(var_name):
            raise AssignmentToUndefinedVariable("Variable %s is not declared", var_name)

        if not self.var_is_array(var_name):
            raise WrongAssignment("Variable %s is scalar, trying to assign as array", var_name)

        self.resolve_scoped_var(var_name).set(idx, val)

    # ------------------ FUNCTIONS ------------------
    def function_declaration(self, matches):
        function_type = self.str_to_type(matches.children[0])
        function_name = matches.children[1]

        if self.symbol_is_declared(function_name):
            raise SymbolAlreadyInUse("The symbol %s is already declared", function_name)

        if len(matches.children) == 4:
            function_parameters = self.evaluate(matches.children[2])
            code = matches.children[3]
        else:
            code = matches.children[2]

        self.functions[function_name] = LanceFunction(function_name, function_parameters, code)

    def function_parameters_declaration(self, matches):
        parameters = []
        for parameter in matches.children:
            parameters.append(self.evaluate(parameter))
        return parameters

    def scalar_parameter(self, matches):
        type = self.str_to_type(matches.children[0])
        name = matches.children[1]
        return LanceFunctionParameter(name, type)

    def array_parameter(self, matches):
        type = self.str_to_type(matches.children[0])
        name = matches.children[1]
        return LanceFunctionParameter(name, type, True)

    def function_call(self, matches):
        function_name = matches.children[0]
        if not self.func_is_declared(function_name):
            raise UndeclaredFunction("Call to undeclared function %s", function_name)

        function = self.functions[function_name]
        formal_parameters = function.parameters

        parameters_expressions = matches.children[1].children

        parameters = self.evaluate_parameters(formal_parameters, parameters_expressions)

        return self.evaluate(function.code, parameters)

    def evaluate_parameters(self, formal_parameters, parameters_expressions):
        formal_nparams = len(formal_parameters)
        nparams = len(parameters_expressions)
        if formal_nparams != nparams:
            raise CallWithWrongArity("Function %s expects %n parameters, %n given", formal_nparams, nparams)

        # TODO: check types, when and if we will ever support anything other than integers

        parameters = {}
        for fparam, expr in zip(formal_parameters, parameters_expressions):
            name = fparam.name
            type = fparam.type
            is_array = fparam.is_array
            if is_array:
                # TODO: check this, it's probably broken
                parameters[name] = self.resolve_scoped_var(expr.children[0])
            else:
                val = self.evaluate(expr)
                parameters[name] = LanceScriptScalarVariable(name, type, val)

        return parameters

    # ------------------ IO ------------------

    def read_stmt(self, matches):
        var_name = matches.children[0]
        if self.var_is_array(var_name):
            raise CannotReadArray()

        if self.const_is_declared(var_name):
            raise CannotAssignConstant("Cannot read into a constant")

        if not self.var_is_decl(var_name):
            raise VariableUndeclared("Trying to read into undefined variable")

        sys.stdout.write("Input value for {} > ".format(var_name))
        if self.mock_input:
            val = random.randint(0, 256)
            sys.stdout.write(str(val) + "\n")
        else:
            val = int(input())

        self.resolve_scoped(var_name).set(val)

    def write_stmt(self, matches):
        val = self.evaluate(matches.children[0])
        sys.stdout.write(str(val))
        sys.stdout.write("\n")

    # ------------------ EXPRESSIONS ------------------

    def binexpr(self, matches):
        op1 = self.evaluate(matches.children[0])
        op = matches.children[1]
        op2 = self.evaluate(matches.children[2])

        if op == '+':
            return op1 + op2
        elif op == '-':
            return op1 - op2
        elif op == '*':
            return op1 * op2
        elif op == '/':
            return op1 // op2
        elif op == '%':
            return op1 % op2
        elif op == '!=':
            return self.bool_to_int(op1 != op2)
        elif op == '==':
            return self.bool_to_int(op1 == op2)
        elif op == '>':
            return self.bool_to_int(op1 > op2)
        elif op == '>=':
            return self.bool_to_int(op1 >= op2)
        elif op == '<':
            return self.bool_to_int(op1 < op2)
        elif op == '<=':
            return self.bool_to_int(op1 <= op2)
        elif op == '&&':
            # Just to be sure operations get short circuited
            if self.evaluate(op1) == 0:
                return 0
            elif self.evaluate(op2) == 0:
                return 0
            else:
                return 1
        elif op == '||':
            if self.evaluate(op1) != 0:
                return 1
            elif self.evaluate(op2) != 0:
                return 1
            else:
                return 0
        elif op == '&':
            return op1 & op2
        elif op == '|':
            return op1 | op2
        elif op == '^':
            return op1 ^ op2
        else:
            raise UnimplementedOperation("Operation %s is not implemented", op)
            # TODO: handle other operations

    @staticmethod
    def intexpr(matches):
        return int(matches.children[0])

    def scalar_expr(self, matches):
        name = matches.children[0]
        val = self.resolve_scoped(name).get()
        return val

    def array_expr(self, matches):
        name = matches.children[0]
        idx = self.evaluate(matches.children[1])
        val = self.resolve_scoped_var(name).get(idx)
        return val

    def lnot_expr(self, matches):
        """Evaluates expression of type '! expr' (logical not)."""
        subexpr_val = self.evaluate(matches.children[0])
        return self.bool_to_int(subexpr_val != 0)

    def neg_expr(self, matches):
        """Evaluates arithmetic negative of an expression"""
        subexpr_val = self.evaluate(matches.children[1])
        return - subexpr_val

    # ------------------ CONTROL FLOW ------------------

    def if_statement(self, matches):
        expr_val = self.evaluate(matches.children[0])

        if expr_val != 0:
            self.evaluate(matches.children[1])

    def if_else_statement(self, matches):
        if_statement = matches.children[0]
        condition_expression = if_statement.children[0]
        if_block = if_statement.children[1]
        else_block = matches.children[1]

        expr_val = self.evaluate(condition_expression)

        if expr_val != 0:
            self.evaluate(if_block)
        else:
            self.evaluate(else_block)

    def while_construct(self, matches):
        condition = matches.children[0]
        code = matches.children[1]

        while self.evaluate(condition) != 0:
            self.evaluate(code)

    def do_while_construct(self, matches):
        code = matches.children[0]
        condition = matches.children[1]

        self.evaluate(code)
        while self.evaluate(condition) != 0:
            self.evaluate(code)

    def for_construct(self, matches):
        initialization = matches.children[0]
        condition = matches.children[1]
        assignment = matches.children[2]
        code = matches.children[3]

        self.evaluate(initialization)
        while self.evaluate(condition) != 0:
            self.evaluate(code)
            self.evaluate(assignment)

    # ------------------ HELPERS ------------------

    def var_is_decl(self, var_name):
        try:
            self.resolve_scoped(var_name)
            return True
        except UndeclaredSymbol as e:
            return False

    def const_is_declared(self, const_name):
        return const_name in self.constants

    def func_is_declared(self, func_name):
        return func_name in self.functions

    def symbol_is_declared(self, symbol_name):
        return (self.var_is_decl(symbol_name)
                or self.const_is_declared(symbol_name)
                or self.func_is_declared(symbol_name))

    def var_is_scalar(self, var_name):
        return isinstance(self.resolve_scoped_var(var_name), LanceScriptScalarVariable)

    def var_is_array(self, var_name):
        return isinstance(self.resolve_scoped_var(var_name), LanceScriptArrayVariable)

    @staticmethod
    def bool_to_int(val):
        if val:
            return 1
        else:
            return 0

    @staticmethod
    def str_to_type(val):
        # TODO: handle types (kinda pointless while we have only integers in the grammar)
        if val == 'int':
            var_type = VarTypes.INT
        else:
            raise InvalidType("This type is not implemented yet")

        return var_type

    def current_context(self):
        return self.vars[-1]

    def resolve_scoped_var(self, name):
        def helper(name, contexts):
            if len(contexts) == 0:
                raise UndeclaredSymbol("%s is not declared", name)

            curr_context = contexts[-1]

            if name in curr_context:
                return curr_context[name]
            else:
                return helper(name, contexts[:-1])

        return helper(name, self.vars)

    def resolve_scoped(self, name):
        if name in self.constants:
            return self.constants[name]

        return self.resolve_scoped_var(name)