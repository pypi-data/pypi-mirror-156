from __future__ import annotations

from typing import Any, List
import importlib
import logging
import runpy

default_logger = logging.getLogger('simple_plugin_manager')


def load(
        import_string: str,
        logger=default_logger,
) -> Any:

    logger.debug('importing %r', import_string)

    # script attribute ('/foo/bar.py::Plugin')
    if '::' in import_string:
        logger.debug('performing script import (runpy)')

        script, attribute_name = import_string.split('::')
        attributes = runpy.run_path(script, run_name=script)

        if attribute_name not in attributes:
            raise ImportError(
                f"script '{script}' has no attribute '{attribute_name}'",
            )

        return attributes[attribute_name]

    # module attribute ('foo.bar.baz')
    elif '.' in import_string:
        logger.debug('performing module import (importlib)')

        module_name, attribute_name = import_string.rsplit('.', 1)
        module = importlib.import_module(module_name)

        if not hasattr(module, attribute_name):
            raise ImportError(
                f"module '{module_name}' has no attribute '{attribute_name}'",
            )

        return getattr(module, attribute_name)

    # module ('foo')
    logger.debug('performing module import (importlib)')

    return importlib.import_module(import_string)


class Loader:
    def __init__(self, logger=default_logger):
        self.logger = logger

        self._attributes = {}

    def load(self, import_string: str) -> Any:
        if import_string not in self._attributes:
            self._attributes[import_string] = load(
                import_string=import_string,
                logger=self.logger,
            )

        return self._attributes[import_string]

    def get_import_strings(self) -> List[str]:
        return list(self._attributes.keys())
