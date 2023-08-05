from typing import Sequence
import math

import attrs
from numpy.random import RandomState

from vkit.utility import rnd_choice
from ..interface import (
    PipelineStep,
    PipelineStepFactory,
    PipelineState,
)


@attrs.define
class PageShapeStepConfig:
    aspect_ratios: Sequence[float] = attrs.field(factory=lambda: (1 / 1.4142, 1.4142))
    area: int = 1024**2


@attrs.define
class PageShapeStepOutput:
    height: int
    width: int


class PageShapeStep(
    PipelineStep[
        PageShapeStepConfig,
        PageShapeStepOutput,
    ]
):  # yapf: disable

    def run(self, state: PipelineState, rnd: RandomState):
        aspect_ratio = rnd_choice(rnd, self.config.aspect_ratios)
        height = round(math.sqrt(self.config.area / aspect_ratio))
        width = round(aspect_ratio * height)
        assert height > 0 and width > 0

        return PageShapeStepOutput(height=height, width=width)


page_shape_step_factory = PipelineStepFactory(PageShapeStep)
