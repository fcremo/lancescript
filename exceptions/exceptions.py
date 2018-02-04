class VariableAlreadyDeclared(Exception):
    pass


class ConstantAlreadyDeclared(Exception):
    pass


class FunctionAlreadyDeclared(Exception):
    pass


class SymbolAlreadyInUse(Exception):
    pass


class InvalidType(Exception):
    pass


class CannotAssignConstant(Exception):
    pass


class AssignmentToUndefinedVariable(Exception):
    pass


class WrongAssignment(Exception):
    pass


class OutOfBoundsAssignment(Exception):
    pass


class OutOfBoundsAccess(Exception):
    pass


class UninitializedValueAccess(Exception):
    pass


class CannotReadArray(Exception):
    pass


class VariableUndeclared(Exception):
    pass


class UndeclaredSymbol(Exception):
    pass


class UndeclaredFunction(Exception):
    pass


class UnimplementedOperation(Exception):
    pass


class CallWithWrongArity(Exception):
    pass
