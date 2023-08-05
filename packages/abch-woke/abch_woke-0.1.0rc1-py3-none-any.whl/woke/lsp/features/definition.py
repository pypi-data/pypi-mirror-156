from typing import Union, List

from woke.lsp.common_structures import WorkDoneProgressOptions, TextDocumentRegistrationOptions, \
    TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, Location, LocationLink
from woke.lsp.context import LspContext


class DefinitionOptions(WorkDoneProgressOptions):
    pass


class DefinitionRegistrationOptions(TextDocumentRegistrationOptions, DefinitionOptions):
    pass


class DefinitionParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams):
    pass


def definition(context: LspContext, params: DefinitionParams) -> Union[Location, List[Location], List[LocationLink], None]:
    pass