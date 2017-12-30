"""
protocols.py Message Protocols


"""


class ProtocolError(ValueError):
    ErrorCode = 0


class EncodingError(ProtocolError):
    ErrorCode = 1


class UnsupportedMessage(ProtocolError):
    ErrorCode = 2

class ParsingError(ProtocolError):
    ErrorCode = 3


class NoHandlerError(ValueError):
    pass


class ProtocolInfo(object):
    def __init__(self, version=''):
        if not version=='':
            # Eventually, we will need to handle different protocol versions. Leave this as a stub...
            raise NotImplementedError('Versioning not yet supported')
        # Lead characters is not currently used, but is for informational purposes
        self.LeadCharacters = {
            '?': 'query',
            '!': 'command',
            '=': 'response',
            '*': 'error'
        }
        # Message definition:
        # (first character, code, [list of arguments])
        # Each argument is defined by a triple: (variable_name, "type", default)
        # If the default is None, the value must be supplied.
        # The supported "types" are:
        # bool = either a bool, or 'T' or 'F'
        # str = string: passed as-is (No | characters!)
        # list = semi-colon delimited list (No '|' characters!)
        self.Messages = (
            ('?', 'T', (('REPEAT','bool','F'),('STEP', 'int', 0)) ),
            ('=', 'T', (('Time', 'int', None),) ),
            ('!', 'JOIN_PLAYER', ()),
            ('?', 'W', ()),
            ('=', 'W', (('EXCHANGES', 'list', None),)),
            ('?', 'W1', (('EXCHANGE', 'str', None),)),
            ('=', 'W1', (('EXCHANGE', 'str', None), ('TEMPLATE', 'list', None),))
        )
        self.MessageLookup = {}
        for leadchar, code, variables in self.Messages:
            front = leadchar + code
            self.MessageLookup[front] = variables


class Protocol(object):
    def __init__(self):
        self.ProtocolInfo = ProtocolInfo()
        self.Handlers = {}

    def BuildMessage(self, front, *args, **kwargs ):
        try:
            variables = self.ProtocolInfo.MessageLookup[front]
        except KeyError:
            raise UnsupportedMessage('Unknown front code: ' + str(front))
        info = [None,] * len(variables)
        for pos in range(0,len(variables)):
            varname, ttype, default = variables[pos]
            value = None
            if pos < len(args):
                value = args[pos]
            elif varname in kwargs:
                value = kwargs[varname]
            else:
                value = default
            if value is None:
                raise EncodingError('Missing variable: ' + varname)
            if ttype == 'bool':
                if type(value) == bool:
                    if value:
                        value = 'T'
                    else:
                        value = 'F'
                if value not in ('T', 'F'):
                    raise EncodingError('Invalid bool value: ' + varname)
                info[pos] = value
            elif ttype == 'int':
                try:
                    value = int(value)
                except:
                    raise EncodingError('Invalid int value: ' + varname)
                value = str(value)
                info[pos] = value
            elif ttype == 'list':
                try:
                    value = ';'.join(value)
                except:
                    raise EncodingError('Invalid list: ' + varname)
                if '|' in value:
                    raise EncodingError('Values cannot contain | character: ' + varname)
                info[pos] = value
            elif ttype == 'str':
                if '|' in value:
                    raise EncodingError('Values cannot contain | character: ' + varname)
                info[pos] = value
            else:
                raise NotImplementedError('Unknown variable type')
        return front + '|' + '|'.join(info)

    def HandleMessage(self, msg, ID=-1):
        info = msg.split('|')
        front = info[0]
        if front not in self.ProtocolInfo.MessageLookup:
            raise UnsupportedMessage('Unsupported Message Type')
        variables = self.ProtocolInfo.MessageLookup[front]
        passed = info[1:]
        if len(passed) > len(variables):
            raise ParsingError('Too many variables')
        args = [None,] * len(variables)
        for pos in range(0, len(variables)):
            varname, ttype, default = variables[pos]
            if pos >= len(passed):
                val = default
            else:
                val = passed[pos]
            if val is None:
                raise ParsingError('Missing required variable: ' + varname)
            if ttype == 'bool':
                if val == 'T':
                    args[pos] = True
                elif val == 'F':
                    args[pos] = False
                else:
                    raise ParsingError('Invalid bool value passed for: ' + varname)
            elif ttype == 'int':
                try:
                    args[pos] = int(val)
                except:
                    raise ParsingError('Invalid int value passed for: ' + varname)
            elif ttype == 'str':
                args[pos] = val
            else:
                raise NotImplementedError('Type not implemented')
        if front not in self.Handlers:
            raise NoHandlerError('No handler for ' + front)
        args.insert(0, ID)
        self.Handlers[front](*args)






