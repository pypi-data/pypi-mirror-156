import concurrent.futures
from pathlib import Path
from typing import Dict, List, Set, Tuple

from woke.ast.b_solc.c_ast_nodes import AstSolc
from woke.compile import SolcOutput
from woke.compile.compilation_unit import CompilationUnit


def _parse_ast(cu_no: int, path: Path, raw_ast: dict) -> Tuple[int, Path, AstSolc]:
    ast = AstSolc.parse_obj(raw_ast)
    return cu_no, path, ast


def normalize(compilation_out: List[Tuple[CompilationUnit, SolcOutput]], modified_files: Set[Path]):
    asts: Dict[int, Dict[Path, AstSolc]] = {}

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for no, (cu, solc_output) in enumerate(compilation_out):
            asts[no] = {}
            for source_unit_name, raw_ast in solc_output.sources.items():
                path = cu.source_unit_name_to_path(source_unit_name)
                futures.append(executor.submit(_parse_ast, no, path, raw_ast.ast))

        for future in concurrent.futures.as_completed(futures):
            cu_no, path, ast = future.result()
            asts[cu_no][path] = ast

    # compilation unit number -> (AST node id -> AST node order)
    nodes_by_order: Dict[int, Dict[int, int]] = {}
