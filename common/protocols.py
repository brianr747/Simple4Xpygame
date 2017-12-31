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
            '*': 'error',
            '#': 'notification',
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
            ('?', 'T', (('repeat','bool','F'),('step', 'strictly_positive_int', 1)) ),
            ('=', 'T', (('time', 'int', None),) ),
            ('!', 'JOIN_PLAYER', ()),
            # Query: list of exchanges
            ('?', 'W', ()),
            # Response: ;ist of exchanges ("worlds")
            ('=', 'W', (('exchanges', 'list', None),)),
            # Query: get template string (commodity list) for an exchange
            ('?', 'W1', (('exchange', 'str', None),)),
            # Response: template string for an exchange
            ('=', 'W1', (('exchange', 'str', None), ('template', 'list', None),)),
            # Production command
            ('!', 'P', (('exchange', 'str', None), ('technique', 'str', None),
                        ('amount', 'strictly_positive_int', None)) ),
            # Production finished notification
            ('#', 'P', (('exchange', 'str', None), ('technique', 'str', None),
                        ('amount', 'strictly_positive_int', None))),
            # Order to exchange
            ('!', 'O', (('exchange', 'str', None), ('commodity', 'str', None),
                         ('order_type', 'order_type', None), ('amount', 'strictly_positive_int', None),
                        ('price', 'strictly_positive_int', None))),
            # Order failure message
            ('#', 'O_FAIL', (('error_message', 'str', None),)),
            # Order filled
            ('#', 'O_FILL', (('exchange', 'str', None), ('commodity', 'str', None),
                         ('order_type', 'order_type', None), ('amount', 'strictly_positive_int', None),
                        ('price', 'strictly_positive_int', None))),
            # Get quote
            ('?', 'Q', (('exchange', 'str', None), ('commodity', 'str', None),
                        ('quote_type', 'quote_type', None))),
            # Response
            ('=', 'Q', (('exchange', 'str', None), ('commodity', 'str', None),
                        ('quote_type','quote_type', None), ('bid', 'list', None),
                        ('offer', 'list', None))),
            # Cash level query
            ('?', 'C', ()),
            # Cash level response
            ('=', 'C', (('cash', 'int', None), ('credit_limit', 'int', None))),
            # Remove orders
            ('!', 'O_REMOVE', (('exchange','str', None), ('commodity','str', None),
                               ('remove_type', 'remove_type', None))),
        )
        self.MessageLookup = {}
        self.Enums = {
            'order_type': ('B', 'S'),
            'quote_type': ('BEST', 'MINE'),
            'remove_type': ('BID', 'ASK', 'ALL'),
        }
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
            elif ttype in ('int', 'strictly_positive_int'):
                try:
                    value = int(value)
                except:
                    raise EncodingError('Invalid int value: ' + varname)
                if ttype == 'strictly_positive_int':
                    if value < 1:
                        raise EncodingError('Variable must be strictly positive: ' + varname)
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
            elif ttype in self.ProtocolInfo.Enums:
                if value not in self.ProtocolInfo.Enums[ttype]:
                    raise EncodingError('Value {0} not in enumerated list: {1}'.format(value, varname))
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
            elif ttype in ('int', 'strictly_positive_int'):
                try:
                    args[pos] = int(val)
                except:
                    raise ParsingError('Invalid int value passed for: ' + varname)
                if ttype == 'strictly_positive_int':
                    if args[pos] < 1:
                        raise ParsingError('Value must be strictly positive: ' + varname)
            elif ttype == 'str':
                args[pos] = val
            elif ttype in self.ProtocolInfo.Enums:
                if val not in self.ProtocolInfo.Enums[ttype]:
                    raise ParsingError('Value not in accepted list: ' + varname)
                args[pos] = val
            else:
                raise NotImplementedError('Type not implemented')
        if front not in self.Handlers:
            raise NoHandlerError('No handler for ' + front)
        args.insert(0, ID)
        self.Handlers[front](*args)






