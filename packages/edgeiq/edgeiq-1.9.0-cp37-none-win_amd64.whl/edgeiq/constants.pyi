from _typeshed import Incomplete
from enum import Enum

NCS2_VID: int
NCS2_PID: int
CUDA_SUPPORTED_BOARDS: Incomplete
TEGRA_CHIP_PATH: str
CPU_COUNT_PATH: str
MYRIAD_SUPPORTED_OS: Incomplete
HAILO_SUPPORTED_OS: Incomplete
EYECLOUD_SUPPORTED_MODEL_PURPOSES: Incomplete

class Engine(Enum):
    DNN: str
    DNN_OPENVINO: str
    DNN_CUDA: str
    TENSOR_RT: str
    HAILO_RT: str

class Accelerator(Enum):
    DEFAULT: str
    CPU: str
    GPU: str
    MYRIAD: str
    NVIDIA: str
    NVIDIA_FP16: str
    HAILO: str

class SupportedDevices(Enum):
    EYECLOUD: str
    OAK: str
    NANO: str
    XAVIER_NX: str
    AGX_XAVIER: str
