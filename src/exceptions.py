class SecretSantaException(Exception):
    pass


class ValidationError(SecretSantaException):
    pass


class FileOperationError(SecretSantaException):
    pass


class AssignmentError(SecretSantaException):
    pass


class InsufficientEmployeesError(AssignmentError):
    pass


class NoValidAssignmentError(AssignmentError):
    pass