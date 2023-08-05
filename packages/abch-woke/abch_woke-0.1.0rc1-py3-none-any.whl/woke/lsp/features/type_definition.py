import logging
from typing import Union, List

from woke.lsp.common_structures import WorkDoneProgressOptions, TextDocumentRegistrationOptions, \
    StaticRegistrationOptions, TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, Location, \
    LocationLink
from woke.lsp.context import LspContext
from woke.lsp.utils.uri import uri_to_path

logger = logging.getLogger(__name__)


class TypeDefinitionOptions(WorkDoneProgressOptions):
    pass


class TypeDefinitionRegistrationOptions(TextDocumentRegistrationOptions, TypeDefinitionOptions, StaticRegistrationOptions):
    pass


class TypeDefinitionParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams):
    pass


def type_definition(context: LspContext, params: TypeDefinitionParams) -> Union[None, Location, List[Location], List[LocationLink]]:
    logger.info(f"Declaration for file {params.text_document.uri} at position {params.position} requested")

    type_definitions = []
    path = uri_to_path(params.text_document.uri).resolve()

    if path in context.compiler.interval_trees:
        tree = context.compiler.interval_trees[path]

        byte_offset = context.compiler.get_byte_offset_from_line_pos(path, params.position.line, params.position.character)
        nodes = tree.at(byte_offset)
        logger.info(f"Found {len(nodes)} nodes at byte offset {byte_offset}:\n{nodes}")
    return type_definitions
