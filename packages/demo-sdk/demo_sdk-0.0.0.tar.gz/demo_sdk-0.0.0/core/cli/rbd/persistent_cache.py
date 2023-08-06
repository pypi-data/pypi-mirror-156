import logging
from copy import deepcopy

from fabric.tasks import execute

import core.cli.fabfile as fabfile
from core.utilities import core_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Persistent_Cache:
    """
    This Class provides wrappers for rbd persistence cache commands.
    """

    def __init__(self, base_cmd):
        self.base_cmd = base_cmd + " persistent-cache"

    def flush(self, **kw):
        """Wrapper for rbd persistent-cache flush.

        Flush persistent cache.

        Args:
            kw: Key value pair of method arguments
        Example::
        Supported keys:
            image_spec(str): image specification
                             [<pool-name>/[<namespace>/]]<image-name>)
            pool(str): Name of the pool of which peer is to be bootstrapped.
            namespace(str): name of the namespace
            image(str): image name
            image-id(str): image id

        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} flush {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return execute(fabfile.run_cmd_in_serial, cmd)

    def invalidate(self, **kw):
        """Wrapper for rbd persistent-cache invalidate.

        Invalidate (discard) existing / dirty persistent cache.

        Args:
            kw: Key value pair of method arguments
        Example::
        Supported keys:
            image_spec(str): image specification
                             [<pool-name>/[<namespace>/]]<image-name>)
            pool(str): Name of the pool of which peer is to be bootstrapped.
            namespace(str): name of the namespace
            image(str): image name
            image-id(str): image id

        Returns:
            Dict(str):
            A mapping of host strings to the given task's return value for that host's execution run.
        """
        kw = kw.get("kw")

        kw_copy = deepcopy(kw)
        image_spec = kw_copy.pop("image_spec", "")
        cmd_args = core_utils.build_cmd_args(kw=kw_copy)

        cmd = f"{self.base_cmd} invalidate {image_spec}{cmd_args}"
        logger.info(f"Running command {cmd}")
        return execute(fabfile.run_cmd_in_serial, cmd)
