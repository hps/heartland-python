from securesubmit.infrastructure import HpsException


class HpsBuilderAbstract(object):
    _builder_actions = None
    executed = False
    _validations = None
    _service = None

    def __init__(self, service):
        self._builder_actions = []
        self._validations = []
        self.executed = False

        self._service = service
        self._setup_validations()

    def execute(self):
        for action in self._builder_actions:
            user_func = getattr(self, action.action)
            user_func(action.arguments)

        self.validate()
        self.executed = True

        return self

    def add_action(self, action):
        self._builder_actions.append(action)
        return self

    def check_status(self):
        if not self.executed:
            raise HpsException('Builder actions not executed.')

    def __getattr__(self, name):
        def wrapper(*args):
            if name[:4] == 'with':
                self.set_property_if_exists(name[4:], args[0])
                return self
            else:
                return False

        return wrapper

    def validate(self):
        # actions = self.compile_action_counts()
        for validation in self._validations:
            # result = validation['callback'](actions)
            result = validation['callback']()
            if result is False:
                print validation['exception_message']
                raise validation['exception_type'](validation['exception_message'])

    def compile_action_counts(self):
        counts = {}

        for action in self._builder_actions:
            if action.name in counts:
                counts[action.name] += 1
            else:
                counts[action.name] = 1

        return counts

    def add_validation(self, callback, exception_type, exception_message=''):
        self._validations.append({
            'callback': callback,
            'exception_type': exception_type,
            'exception_message': exception_message
        })

        return self

    def set_property_if_exists(self, *args):
        name = args[0]
        value = args[1]

        if hasattr(self, name):
            action = HpsBuilderAction(name, 'set_property')
            action.arguments = [name, value]
            self.add_action(action)
        else:
            raise HpsUnknownPropertyException(self, name)

    def set_property(self, args):
        name = args[0]
        value = args[1]
        setattr(self, name, value)

    def _setup_validations(self):
        pass


class HpsBuilderAction(object):
    action = None
    name = None
    arguments = None

    def __init__(self, name=None, action=None):
        self.name = name
        self.action = action


class HpsUnknownPropertyException(HpsException):
    def __init__(self, obj, prop, inner=None):
        class_name = obj.__class__.__name__
        message = 'Failed to set non-existant property {0} on class {1}'.format(prop, class_name)
        HpsException.__init__(self, message, inner)