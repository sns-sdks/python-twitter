class PyTwitterError(Exception):
    """Base class for Twitter errors"""

    @property
    def message(self):
        """Returns the first argument used to construct this error."""
        return self.args[0]


class PythonTwitterDeprecationWarning(DeprecationWarning):
    """Base class for python-twitter deprecation warnings"""

    pass
