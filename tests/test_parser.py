"""testing yaml and message parsers"""

import unittest
from parsers import CmdParser

YAML = """

requests:
  - name: sayhello
    pattern: hello
    webhook: http://api.hello.com
    text: hello
  
  - name: order tracking
    pattern: (track\s+order\s+(?P<track>.*)?
    webhook: http://api.helloworld.com
    text: your order infomation {{response.description}}
    params: 
       - track

"""

class ParserTest(unittest.TestCase):
    """ Parsing to actions"""
    def setUp(self):
        self.YAML = YAML
        self.parser = CmdParser(YAML)