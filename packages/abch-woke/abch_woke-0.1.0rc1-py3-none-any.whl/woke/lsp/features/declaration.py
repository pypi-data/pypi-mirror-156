import logging
from typing import Union, List

from woke.ast.ir.expression.identifier import Identifier
from woke.ast.ir.meta.identifier_path import IdentifierPath
from woke.ast.ir.type_name.user_defined_type_name import UserDefinedTypeName
from woke.lsp.common_structures import TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams, \
    Location, WorkDoneProgressOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions, Range, Position
from woke.lsp.context import LspContext
from woke.lsp.utils.uri import uri_to_path, path_to_uri

logger = logging.getLogger(__name__)


class DeclarationOptions(WorkDoneProgressOptions):
    pass


class DeclarationRegistrationOptions(DeclarationOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions):
    pass


class DeclarationParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams):
    pass


def declaration(context: LspContext, params: DeclarationParams) -> Union[None, Location, List[Location]]:
    logger.info(f"Declaration for file {params.text_document.uri} at position {params.position} requested")

    declarations = []
    path = uri_to_path(params.text_document.uri).resolve()

    if path in context.compiler.interval_trees:
        tree = context.compiler.interval_trees[path]

        byte_offset = context.compiler.get_byte_offset_from_line_pos(path, params.position.line, params.position.character)
        nodes = tree.at(byte_offset)
        logger.info(f"Found {len(nodes)} nodes at byte offset {byte_offset}:\n{nodes}")

        for interval in nodes:
            node = interval.data
            if isinstance(node, IdentifierPath) or isinstance(node, UserDefinedTypeName) or isinstance(node, Identifier):
                referenced_declaration = node.referenced_declaration
                if referenced_declaration is None:
                    continue
                path = referenced_declaration.file
                uri = path_to_uri(path)
                assert referenced_declaration.name_location is not None
                byte_start, byte_length = referenced_declaration.name_location
                start_line, start_column = context.compiler.get_line_pos_from_byte_offset(path, byte_start)
                end_line, end_column = context.compiler.get_line_pos_from_byte_offset(path, byte_start + byte_length)

                declarations.append(Location(
                    uri=uri,
                    range=Range(
                        start=Position(line=start_line, character=start_column),
                        end=Position(line=end_line, character=end_column)
                    )
                ))
    return declarations
