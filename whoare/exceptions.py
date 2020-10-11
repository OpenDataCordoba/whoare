class WhoIsCommandError(Exception):
    pass


class ZoneNotFoundError(Exception):
    pass


class TooManyQueriesError(Exception):
    """ Registrar ask to stop querying """
    pass


class ServiceUnavailableError(Exception):
    """ Registrar ask to stop querying """
    pass

class UnknownError(Exception):
    """ Registrar asks to stop querying """
    pass

class UnexpectedParseError(Exception):
    """ Registrar asks to stop querying """
    pass
