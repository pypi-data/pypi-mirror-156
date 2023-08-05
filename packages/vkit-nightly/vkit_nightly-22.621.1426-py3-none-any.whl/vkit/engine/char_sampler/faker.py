from typing import Sequence, List, Dict, Optional
from collections import OrderedDict

import attrs
from numpy.random import RandomState
from faker import Faker

from vkit.utility import rnd_choice
from vkit.engine.interface import Engine
from .type import CharSamplerEngineResource, CharSamplerEngineRunConfig


@attrs.define
class FakerCharSamplerEngineConfig:
    local_to_weight: Dict[str, float] = {
        'zh_CN': 3,
        'zh_TW': 2,
        'en_US': 1,
    }
    method_to_weight: Dict[str, float] = {
        'address': 1,
        'ascii_email': 1,
        'dga': 1,
        'uri': 1,
        'word': 1,
        'name': 1,
        'country_calling_code': 1,
        'phone_number': 1,
    }


class FakerCharSamplerEngine(
    Engine[
        FakerCharSamplerEngineConfig,
        CharSamplerEngineResource,
        CharSamplerEngineRunConfig,
        Sequence[str],
    ]
):  # yapf: disable

    @classmethod
    def get_type_name(cls) -> str:
        return 'faker'

    def __init__(
        self,
        config: FakerCharSamplerEngineConfig,
        resource: Optional[CharSamplerEngineResource] = None,
    ):
        super().__init__(config, resource)

        assert resource
        self.lexicon_collection = resource.lexicon_collection

        self.methods = sorted(config.method_to_weight)
        weights = [config.method_to_weight[method] for method in self.methods]
        total = sum(weights)
        self.methods_probs = [weight / total for weight in weights]

    def sample_from_faker(self, rnd: RandomState):
        faker = Faker(OrderedDict(self.config.local_to_weight))
        seed = rnd.get_state()[1].tobytes()  # type: ignore
        for local in self.config.local_to_weight:
            faker[local].seed(seed)

        method = rnd_choice(rnd, self.methods, probs=self.methods_probs)
        while True:
            text = getattr(faker, method)()
            segments: List[str] = []
            for segment in text.split():
                segment = ''.join(char for char in text if self.lexicon_collection.has_char(char))
                if segment:
                    segments.append(segment)
            if segments:
                return ' '.join(segments)

    def run(self, config: CharSamplerEngineRunConfig, rnd: RandomState) -> Sequence[str]:
        num_chars = config.num_chars

        texts: List[str] = []
        num_chars_in_texts = 0
        while num_chars_in_texts + len(texts) - 1 < num_chars:
            text = self.sample_from_faker(rnd)
            texts.append(text)
            num_chars_in_texts += len(text)

        chars = list(' '.join(texts))

        # Trim and make sure the last char is not space.
        if len(chars) > num_chars:
            rest = chars[num_chars:]
            chars = chars[:num_chars]
            if chars[-1].isspace():
                chars.pop()
                assert not rest[0].isspace()
                chars.append(rest[0])

        return chars
