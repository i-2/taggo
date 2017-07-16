"""testing yaml and message parsers"""

import asyncio
import unittest
from unittest.mock import patch
from parsers import YamlCommand

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


class TestYamlCommand(unittest.TestCase):
    
    def setUp(self):
        """setup the initial command dict"""
        self.command_dict = {
            "name": "sayhello",
            "pattern": "track\s+order\s+(?P<track>.*)?",
            "webhook": "http://api.helloworld.com",
            "text": "your order information {{response.description}}",
            "params": ("track",)
        }
    
    def test_must_produce_matching_result(self):
        input_sent = "track order 1231213"
        command = YamlCommand(**self.command_dict)
        self.assertTrue(command.is_matched(input_sent))
        
    def test_mustnot_produce_matching_result(self):
        input_sent = "track order1231231"
        command = YamlCommand(**self.command_dict)
        self.assertFalse(command.is_matched(input_sent))
        
    @asyncio.coroutine
    def test_hello(self):
        self.assertTrue(True)