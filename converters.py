# libs
# local


class CIDRConverter:
    regex = r'([a-fA-F0-9]{0,4}(:|\.)){1,7}(:|\.)?[a-fA-F0-9]{0,4}/\d{1,3}'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
