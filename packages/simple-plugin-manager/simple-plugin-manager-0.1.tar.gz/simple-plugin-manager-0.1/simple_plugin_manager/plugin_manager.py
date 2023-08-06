from __future__ import annotations

from typing import Any, Callable, Iterator
from inspect import isclass
from copy import copy
import logging

from simple_plugin_manager.loading import Loader

default_logger = logging.getLogger('simple_plugin_manager')


class PluginManager:
    HOOK_NAMES: list[str] = []

    def __init__(
            self,
            logger=default_logger,
            hook_names: list[str] | None = None,
    ) -> None:

        self.logger = logger

        self._hook_names: list[str] = hook_names or self.HOOK_NAMES
        self._plugins: list[Any] = []
        self._hooks: dict[str, Any] = {}
        self.loader: Loader = Loader(logger=self.logger)

    # loading #################################################################
    def check_hook(
            self,
            plugin: Any,
            hook_name: str,
            hook: Any,
    ) -> bool:

        return True

    def _discover_hooks(self) -> None:
        self.logger.debug('discovering hooks')

        # clear cache
        self.logger.debug('clearing hook cache')

        self._hooks.clear()

        # check if hook names are specified
        if not self._hook_names:
            self.logger.debug('no hook names defined; nothing to do')

            return

        # setup hook cache
        self.logger.debug('setting up hook cache')

        for hook_name in self._hook_names:
            self._hooks[hook_name] = []

        # discover hooks
        for plugin in self._plugins:
            self.logger.debug('analyzing %r', plugin)

            for hook_name in self._hook_names:
                if not hasattr(plugin, hook_name):
                    continue

                hook = getattr(plugin, hook_name)

                # run checks
                if not self.check_hook(
                        plugin=plugin,
                        hook_name=hook_name,
                        hook=hook,
                ):

                    self.logger.debug('hook %r rejected by hook checker', hook)

                    continue

                # cache hook
                self._hooks[hook_name].append(
                    (plugin, hook),
                )

                self.logger.debug('%r.%s discovered', plugin, hook_name)

    def initialize_plugin(
            self,
            plugin_class: Any,
    ) -> Any:

        return plugin_class()

    def load(
            self,
            plugins: list[Any],
    ) -> None:

        if not isinstance(plugins, list):  # pragma: no cover
            raise ValueError("'plugins' has to be a list")

        self.logger.debug('loading plugins')

        # load plugins
        for raw_plugin in plugins:
            self.logger.debug('loading %r', raw_plugin)

            # import strings
            if isinstance(raw_plugin, str):
                self.logger.debug(
                    "%r gets handled as import string",
                    raw_plugin,
                )

                plugin_class = self.loader.load(
                    import_string=raw_plugin,
                )

            else:
                plugin_class = raw_plugin

            # classes
            if isclass(plugin_class):
                self.logger.debug(
                    '%r gets handled as class',
                    raw_plugin,
                )

                plugin = self.initialize_plugin(
                    plugin_class=plugin_class,
                )

            # pre initialized plugins
            else:
                self.logger.debug(
                    '%r gets handled as plain object',
                    raw_plugin,
                )

                plugin = raw_plugin

            # cache plugin
            self._plugins.append(plugin)

        # discover hooks
        self._discover_hooks()

    # hook helper #############################################################
    def get_plugins(self) -> list[Any]:
        return copy(self._plugins)

    def get_hook_names(self) -> list[str]:
        return copy(self._hook_names)

    def iter_hooks(
            self,
            hook_name: str,
    ) -> Iterator:

        if hook_name not in self._hooks:  # pragma: no cover
            raise RuntimeError(f"Unknown hook name '{hook_name}'")

        for plugin, hook in self._hooks[hook_name]:
            yield plugin, hook

    # hook execution ##########################################################
    def handle_hook_exception(
            self,
            hook_name: str,
            plugin: Any,
            hook: Callable,
            exception: Exception,
    ) -> Any:

        self.logger.error(
            'Exception raised while running %s.%s',
            plugin,
            hook_name,
            exc_info=exception,
        )

        return exception

    def _run_hook(
            self,
            hook_name: str,
            plugin: Any,
            hook: Callable,
            hook_args: list | tuple,
            hook_kwargs: dict,
    ) -> Any:

        try:
            self.logger.debug(
                'running %r.%s(*%r, **%r)',
                plugin,
                hook_name,
                hook_args,
                hook_kwargs,
            )

            return_value = hook(
                *hook_args,
                **hook_kwargs,
            )

            self.logger.debug(
                'running %r.%s returned %r',
                plugin,
                hook_name,
                return_value,
            )

            return return_value

        except Exception as exception:
            return self.handle_hook_exception(
                plugin=plugin,
                hook_name=hook_name,
                hook=hook,
                exception=exception,
            )

    def run_hook(
            self,
            hook_name: str,
            hook_args: list | tuple | None = None,
            hook_kwargs: dict | None = None,
    ) -> list[Any]:

        self.logger.debug('running %r', hook_name)

        hook_args = hook_args or []
        hook_kwargs = hook_kwargs or {}

        return_values = []

        for plugin, hook in self.iter_hooks(hook_name=hook_name):
            return_value = self._run_hook(
                hook_name=hook_name,
                plugin=plugin,
                hook=hook,
                hook_args=hook_args,
                hook_kwargs=hook_kwargs,
            )

            return_values.append(return_value)

        return return_values

    def run_hook_as_chain(
            self,
            hook_name: str,
            hook_arg: Any,
    ) -> Any:

        self.logger.debug('running %r as chain', hook_name)

        for plugin, hook in self.iter_hooks(hook_name=hook_name):
            return_value = self._run_hook(
                hook_name=hook_name,
                plugin=plugin,
                hook=hook,
                hook_args=[hook_arg],
                hook_kwargs={},
            )

            if return_value is hook_arg:
                continue

            if return_value is None:
                self.logger.debug(
                    'chain was stopped by %r.%s by returning None',
                    plugin,
                    hook_name,
                )

            else:
                self.logger.debug(
                    'chain was stopped by %r.%s by returning a custom value',
                    plugin,
                    hook_name,
                )

            return return_value

        return hook_arg
