"""testing yaml and message parsers"""

import asyncio
import unittest
from unittest.mock import patch
from .base import AsyncMock
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
       
    def test_parser(self):
        input_sent = "track order 12312312"
        command = YamlCommand(**self.command_dict)
        self.assertDictEqual({
            "track": "12312312"
        }, command.parse(input_sent))

    @patch.object(YamlCommand, '_send', new_callable=AsyncMock)
    @asyncio.coroutine        
    def test_execute(self, send_mock):
        input_sent = "track order 123123213"
        command = YamlCommand(**self.command_dict)
        value = yield from command.execute(input_sent, sender_id=2342433)
        self.assertFalse(send_mock.called)