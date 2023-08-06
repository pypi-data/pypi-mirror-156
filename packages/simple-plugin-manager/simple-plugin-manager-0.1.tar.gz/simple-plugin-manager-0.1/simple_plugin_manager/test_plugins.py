class PlainTestPlugin:
    pass


class TestPlugin:
    SECRET_STRING = 'secret'

    def __init__(
            self,
            name='',
            state=None,
            bubble_up=True,
            return_value=None,
            raise_runtime_error=False,
    ):

        self.name = name
        self.state = state
        self.bubble_up = bubble_up
        self.return_value = return_value
        self.raise_runtime_error = raise_runtime_error

        if state is None:
            self.state = []

    def handle_data(self, data):
        if self.raise_runtime_error:
            raise RuntimeError()

        self.state.append(
            (self.name, data, )
        )

        if self.return_value:
            return self.return_value

        if self.bubble_up:
            return data
