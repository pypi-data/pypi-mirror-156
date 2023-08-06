from dataclasses import dataclass
from typing import List, Tuple, Dict, ByteString
import json
from ._core import Decoder


@dataclass
class Msg:
    template_id: str
    template_name: str
    msg_json: dict


class MfastDecoder():
    def __init__(self, template: str) -> None:
        # valid?
        self.dec = Decoder(template)

    def add_template(self, template: str) -> None:
        # valid?
        self.dec = Decoder(template)

    def decode(self, msg: ByteString) -> Tuple[List[Msg], ByteString]:
        msgs, rest_start = self.dec.decode(msg)
        res = [Msg(m.id, m.name, json.loads(m.json))
               for m in msgs]
        return res, None if rest_start == 0 else msg[-rest_start:]

if __name__ == '__main__':
    temp = '''
    <?xml version="1.0" encoding="UTF-8" ?>
    <templates xmlns="http://www.fixprotocol.org/ns/fast/td/1.1">
        <template dictionary="1" id="1" name="HelloWorld">
             <string id="58" name="Text">
                 <default value=""></default>
             </string>
        </template>
    </templates>
    '''
    dec = MfastDecoder(temp)
    by = b'\xE0\x81\x48\x65\x6C\x6C\x6F\x57\x6F\x72\x6C\xE4'
    msg_li, rest = dec.decode(by)
    print(msg_li)
    print(rest)
