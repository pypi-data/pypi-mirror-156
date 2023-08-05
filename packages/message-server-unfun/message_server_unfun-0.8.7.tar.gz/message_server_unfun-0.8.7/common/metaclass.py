import dis


class ServerMaker(type):
    """Метакласс, проверяющий что в результирующем классе нет клиентскихвызовов таких как: connect.
    Также проверяется, что серверный сокет является TCP и работает по IPv4 протоколу."""

    def __init__(cls, clsname, bases, clsdict):
        methods = []
        attrs = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])

            except TypeError:
                pass
            else:

                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        if 'connect' in methods:
            raise TypeError('Using the connect method is not allowed in the server class')

        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(clsname, bases, clsdict)


class ClientMaker(type):
    """Метакласс, проверяющий что в результирующем классе нет серверных вызовов таких как: accept, listen.
    Также проверяется, что сокет не создаётся внутри конструктора класса."""

    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError(
                    'The use of a prohibited method was detected in the class')
        if 'do_decode' in methods or 'do_encode' in methods:
            pass
        else:
            raise TypeError(
                'There are no calls to functions that work with sockets.')
        super().__init__(clsname, bases, clsdict)
