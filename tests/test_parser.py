"""testing yaml and message parsers"""

import asyncio
import unittest
from unittest.mock import patch
from .base import AsyncMock, AioTestCase
from parsers import YamlCommand, YamlExecutor

YAML = """

default:
  name: default
  pattern: ".*"
  text: can't get you

requests:
  - name: sayhello
    pattern: "hello"
    webhook: http://api.hello.com
    text: hello
  
  - name: order tracking
    pattern: track\s+order\s+(?P<track>.*)?
    webhook: http://api.helloworld.com
    text: your order infomation {{response.description}}
    params: 
       - track

"""


class TestYamlCommand(AioTestCase):
    
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

    async def test_execute(self):
        input_sent = "track order 123123213"
        with patch.object(YamlCommand, '_send', new_callable=AsyncMock) as send_mock:
            command = YamlCommand(**self.command_dict)
            value = await command.execute(input_sent, sender_id=2342433)
        self.assertTrue(send_mock.called)
        

class TestYamlExecutor(AioTestCase):
    
    def setUp(self):
        self._raw_yaml = YAML
        
        class TestYamlCommand(YamlCommand):
            def send(self, *args):
                return True
        
        class TestYamlExecutor(YamlExecutor):
            command_class = TestYamlCommand
        
        self.YCommand = TestYamlCommand
        self.YExecute = TestYamlExecutor
        
    async def test_respond_method(self):
        """test the execution of respond method"""
        
        found = "hello"
        not_found ="How are you!"
        
        executor = self.YExecute(self._raw_yaml)
        executor.default_command  = AsyncMock(return_value=None)
        executor.default_command.execute = dmock = AsyncMock(return_value=None)
        
        with patch.object(self.YCommand, 'execute', new_callable=AsyncMock) as cm:
            await executor.respond("1213132", found)
            self.assertTrue(cm.called)
            await executor.respond("1213132", not_found)
            self.assertTrue(dmock.called)