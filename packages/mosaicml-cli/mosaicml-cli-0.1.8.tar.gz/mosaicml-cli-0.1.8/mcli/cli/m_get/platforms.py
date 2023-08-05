"""CLI getter for platforms"""
from dataclasses import dataclass
from typing import Dict, Generator, List

from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay
from mcli.config import MCLIConfig, MCLIConfigError
from mcli.models import MCLIPlatform
from mcli.serverside.platforms.platform_instances import InstanceRequest, UserInstanceRegistry
from mcli.utils.utils_logging import FAIL, err_console


@dataclass
class PlatformDisplayItem(MCLIDisplayItem):
    context: str
    namespace: str
    gpu_types_and_nums: str


class MCLIPlatformDisplay(MCLIGetDisplay):
    """`mcli get platforms` display class
    """

    def __init__(self, platforms: List[MCLIPlatform]):
        self.platforms = platforms
        self.registry = UserInstanceRegistry(platforms=platforms)

    def __iter__(self) -> Generator[PlatformDisplayItem, None, None]:
        for platform in self.platforms:
            gpu_info_str = _get_gpu_info_str(platform_name=platform.name)
            yield PlatformDisplayItem(name=platform.name,
                                      context=platform.kubernetes_context,
                                      namespace=platform.namespace,
                                      gpu_types_and_nums=gpu_info_str)


def get_platforms(output: OutputDisplay = OutputDisplay.TABLE, **kwargs) -> int:
    del kwargs

    try:
        conf = MCLIConfig.load_config()
    except MCLIConfigError:
        err_console.print(f'{FAIL} MCLI not yet initialized. Please run `mcli init` and then `mcli create platform` '
                          'to create your first platform.')
        return 1

    display = MCLIPlatformDisplay(conf.platforms)
    display.print(output)
    return 0


def _get_gpu_info_str(platform_name: str) -> str:
    registry = UserInstanceRegistry()
    options = registry.lookup(request=InstanceRequest(platform=platform_name, gpu_type=None, gpu_num=None))

    types_to_nums: Dict[str, List[int]] = {}
    for option in options:
        if option.gpu_type not in types_to_nums:
            types_to_nums[option.gpu_type] = []
        types_to_nums[option.gpu_type].append(option.gpu_num)

    gpu_type_str = ''
    for gpu_type in types_to_nums:
        gpu_type_str += (gpu_type + ' (' + ', '.join(map(lambda x: str(x), sorted(types_to_nums[gpu_type]))) + ')' +
                         '\n')
    return gpu_type_str.strip('\n')
