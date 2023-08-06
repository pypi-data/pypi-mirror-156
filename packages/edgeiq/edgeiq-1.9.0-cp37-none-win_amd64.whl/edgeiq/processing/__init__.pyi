from .image import *
from .object_detection import *
from .results import *
from .semantic_segmentation import *
from .image_classification import *
from .trt_plugin import *
from .libhuman_pose import *
from .hailo_processing import *
from .instance_segmentation import *
from _typeshed import Incomplete

class Processor:
    funcs: Incomplete
    def __init__(self, funcs: Incomplete | None = ...) -> None: ...
    def __call__(self, data, runtime_params: Incomplete | None = ...): ...
