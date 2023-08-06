import functools
import typing
from os import PathLike

import fastapi
from fastapi.templating import Jinja2Templates

__version__ = '1.0'
__all__ = ["Jinja2TemplatesDependency", "Renderable"]

Renderable = typing.Callable[[str, dict], fastapi.Response]


class Jinja2TemplatesDependency:
    """
    Quality-of-life wrapper for Jinja2Templates provided by fastapi.

    Example usage:

    ```
    jinja = Jinja2TemplatesDependency("/templates")

    @app.get("/")
    def my_view(..., render: JinjaTemplatesDependency = Depends(jinja)):
        ...
        return render("my_template.html.jinja2", context={"name": name})
    ```
    """
    def __init__(self,
                 template_dir: typing.Union[str, PathLike],
                 env_options: typing.Optional[dict] = None,
                 env_globals: typing.Optional[dict] = None,
                 ):
        self.templates = Jinja2Templates(directory=template_dir, **(env_options or {}))
        self._set_globals(self.templates, env_globals or {})

    @staticmethod
    def _set_globals(template_cls, env_globals: dict):
        for key, value in env_globals.items():
            template_cls.env.globals[key] = value

    def _render(self, request, name, context):
        context.update({"request": request})
        return self.templates.TemplateResponse(name, context)

    def __call__(self, request: fastapi.Request) -> Renderable:
        return functools.partial(self._render, request)
