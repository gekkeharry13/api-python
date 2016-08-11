#
# Copyright (C) 2014-2016 Conjur Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Defines configuration settings needed to connect to a Conjur appliance.

For convenience, a "global" `conjur.config.Config` instance is available as
`conjur.config.config`.  This object is used when a `conjur.api.API` instance
is created without a config.

The most important settings are `url`, `account`, and `cert_file`.

  * `url` points the client to your Possum instance.

  * `account` is an organizational name you want to use.  This value is required.

  * `cert_file` is the path to a `pem` formated certificate used to make a secure connection to
     Possum.  This option is **required** if you are using https with a self-signed certificate.
"""

import os

_DEFAULT = object()

class ConfigException(Exception):
    pass


def _setting(name, default=_DEFAULT, doc=''):
    def fget(self):
        return self.get(name, default)

    def fset(self, value):
        self.set(name, value)

    return property(fget, fset, doc=doc)


class Config(object):
    def __init__(self, **kwargs):
        self._config = {}
        self.update(kwargs)

    def load(self, input):
        import yaml

        if isinstance(input, str):
            input = open(input, 'r')
        conf = yaml.safe_load(input)
        self.update(conf)

    def update(self, *dicts, **kwargs):
        for d in dicts + (kwargs, ):
            self._config.update(d)

    def get(self, key, default=_DEFAULT):
        if key in self._config:
            return self._config[key]
        env_key = 'CONJUR_' + key.upper()
        if env_key in os.environ:
            value = os.environ[env_key]
            self._config[key] = value
            return value
        if default is _DEFAULT:
            raise Exception("config setting %s is required" % key)
        return default

    def set(self, key, value):
        self._config[key] = value

    cert_file = _setting('cert_file', None,
                         "Path to certificate to verify ssl requests \
                         to appliance")

    account = _setting('account', 'conjur', 'Conjur account identifier')

    url = _setting('url', None, 'URL for Possum')

    @property
    def verify(self):
        '''
        Argument to be passed to `requests` methods `verify` keyword argument.
        '''
        if self.cert_file is not None:
            return self.cert_file
        else:
            return True


config = Config()
"""
A global `conjur.Config` instance, used when creating an `conjur.API` instance
by default.
"""

default = config

__all__ = ('Config', 'config', 'default')
