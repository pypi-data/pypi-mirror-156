"""
Wsgirouter3 extension for pdf generation using weasyprint.

Homepage: https://github.com/andruskutt/wsgirouter3_weasyprint

License: MIT
"""

import functools
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, NoReturn, Optional, Tuple

from weasyprint import HTML  # type: ignore

__all__ = ['Pdf', 'PdfConfig', 'install']


@dataclass
class PdfConfig:
    html_generator: Callable[[str, Any], str]
    url_fetcher: Optional[Callable[[str, int, Any], Dict[str, Any]]] = None
    default_headers: Optional[Mapping[str, str]] = None


@dataclass
class Pdf:
    html_id: str
    context: Any = None
    headers: Optional[Mapping[str, str]] = None


def _disable_url_fetching(url: str, timeout: int = 10, ssl_context=None) -> NoReturn:
    raise NotImplementedError('Url fetching is disabled')


def pdf_generator(config: PdfConfig, pdf: Pdf, headers: Dict[str, str]) -> Tuple[bytes]:
    html = config.html_generator(pdf.html_id, pdf.context)
    url_fetcher = config.url_fetcher or _disable_url_fetching
    response = HTML(string=html, url_fetcher=url_fetcher).write_pdf()

    headers['Content-Type'] = 'application/pdf'
    headers['Content-Length'] = str(len(response))

    if config.default_headers:
        headers.update(config.default_headers)
    if pdf.headers:
        headers.update(pdf.headers)

    return (response,)


def install(wsgirouter3: Any, config: PdfConfig) -> None:
    wsgirouter3.config.result_converters.append((
        lambda result: isinstance(result, Pdf),
        functools.partial(pdf_generator, config)
    ))
