class DateConverter:
    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
