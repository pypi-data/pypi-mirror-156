import logging
from typing import Optional, List, Any, Union

from woke.ast.ir.declaration.contract_definition import ContractDefinition
from woke.ast.nodes import AstNodeId
from woke.lsp.common_structures import WorkDoneProgressOptions, TextDocumentRegistrationOptions, \
    StaticRegistrationOptions, TextDocumentPositionParams, WorkDoneProgressParams, SymbolKind, SymbolTag, DocumentUri, \
    Range, PartialResultParams, Position
from woke.lsp.context import LspContext
from woke.lsp.lsp_data_model import LspModel
from woke.lsp.utils.uri import uri_to_path, path_to_uri

logger = logging.getLogger(__name__)


class TypeHierarchyOptions(WorkDoneProgressOptions):
    pass


class TypeHierarchyRegistrationOptions(TextDocumentRegistrationOptions, TypeHierarchyOptions, StaticRegistrationOptions):
    pass


class TypeHierarchyPrepareParams(TextDocumentPositionParams, WorkDoneProgressParams):
    pass


class TypeHierarchyItemData(LspModel):
    ast_node_id: int
    cu_hash: str


class TypeHierarchyItem(LspModel):
    name: str
    """
    The name of this item.
    """
    kind: SymbolKind
    """
    The kind of this item.
    """
    tags: Optional[List[SymbolTag]]
    """
    Tags for this item.
    """
    detail: Optional[str]
    """
    More detail for this item, e.g. the signature of a function.
    """
    uri: DocumentUri
    """
    The resource identifier of this item.
    """
    range: Range
    """
    The range enclosing this symbol not including leading/trailing whitespace
    but everything else, e.g. comments and code.
    """
    selection_range: Range
    """
    The range that should be selected and revealed when this symbol is being
    picked, e.g. the name of a function. Muse be contained by the
    [`range`](#TypeHierarchyItem.range).
    """
    data: TypeHierarchyItemData
    """
    A data entry field that is preserved between a type hierarchy prepare and
    supertypes or subtypes requests. It could also be used to identify the
    type hierarchy in the server, helping improve the performance on
    resolving supertypes and subtypes.
    """


class TypeHierarchySupertypesParams(WorkDoneProgressParams, PartialResultParams):
    item: TypeHierarchyItem


class TypeHierarchySubtypesParams(WorkDoneProgressParams, PartialResultParams):
    item: TypeHierarchyItem


def prepare_type_hierarchy(context: LspContext, params: TypeHierarchyPrepareParams) -> Union[List[TypeHierarchyItem], None]:
    logger.info(f"Type hierarchy for file {params.text_document.uri} at position {params.position} requested")

    type_items = []
    path = uri_to_path(params.text_document.uri).resolve()

    if path in context.compiler.interval_trees:
        tree = context.compiler.interval_trees[path]

        byte_offset = context.compiler.get_byte_offset_from_line_pos(path, params.position.line, params.position.character)
        nodes = tree.at(byte_offset)
        logger.info(f"Found {len(nodes)} nodes at byte offset {byte_offset}:\n{nodes}")

        for interval in nodes:
            node = interval.data
            if isinstance(node, ContractDefinition):
                name_byte_offset, name_byte_length = node.name_location
                name_start_line, name_start_column = context.compiler.get_line_pos_from_byte_offset(path, name_byte_offset)
                name_end_line, name_end_column = context.compiler.get_line_pos_from_byte_offset(path, name_byte_offset + name_byte_length)
                contract_start_line, contract_start_column = context.compiler.get_line_pos_from_byte_offset(path, interval.begin)
                contract_end_line, contract_end_column = context.compiler.get_line_pos_from_byte_offset(path, interval.end)

                type_items.append(TypeHierarchyItem(
                    name=node.name,
                    kind=SymbolKind.CLASS,
                    tags=None,
                    detail=None,
                    uri=path_to_uri(node.file),
                    range=Range(
                        start=Position(line=name_start_line, character=name_start_column),
                        end=Position(line=name_end_line, character=name_end_column)
                    ),
                    selection_range=Range(
                        start=Position(line=contract_start_line, character=contract_start_column),
                        end=Position(line=contract_end_line, character=contract_end_column)
                    ),
                    data=TypeHierarchyItemData(ast_node_id=node.ast_node_id, cu_hash=node.cu_hash.hex())
                ))

    return type_items


def supertypes(context: LspContext, params: TypeHierarchySupertypesParams) -> Union[List[TypeHierarchyItem], None]:
    ast_node_id = params.item.data.ast_node_id
    cu_hash = bytes.fromhex(params.item.data.cu_hash)
    node = context.compiler.ir_reference_resolver.resolve_node(AstNodeId(ast_node_id), cu_hash)
    path = node.file
    assert isinstance(node, ContractDefinition)

    type_items = []

    linearized_contracts = node.linearized_base_contracts
    for contract in linearized_contracts:
        name_byte_offset, name_byte_length = contract.name_location
        name_start_line, name_start_column = context.compiler.get_line_pos_from_byte_offset(path, name_byte_offset)
        name_end_line, name_end_column = context.compiler.get_line_pos_from_byte_offset(path,
                                                                                        name_byte_offset + name_byte_length)
        contract_start_line, contract_start_column = context.compiler.get_line_pos_from_byte_offset(path,
                                                                                                    contract.byte_location[0])
        contract_end_line, contract_end_column = context.compiler.get_line_pos_from_byte_offset(path, contract.byte_location[1])

        type_items.append(TypeHierarchyItem(
            name=contract.name,
            kind=SymbolKind.CLASS,
            tags=None,
            detail=None,
            uri=path_to_uri(contract.file),
            range=Range(
                start=Position(line=name_start_line, character=name_start_column),
                end=Position(line=name_end_line, character=name_end_column)
            ),
            selection_range=Range(
                start=Position(line=contract_start_line, character=contract_start_column),
                end=Position(line=contract_end_line, character=contract_end_column)
            ),
            data=TypeHierarchyItemData(ast_node_id=node.ast_node_id, cu_hash=node.cu_hash.hex())
        ))

    return type_items


def subtypes(context: LspContext, params: TypeHierarchySubtypesParams) -> Union[List[TypeHierarchyItem], None]:
    return []
