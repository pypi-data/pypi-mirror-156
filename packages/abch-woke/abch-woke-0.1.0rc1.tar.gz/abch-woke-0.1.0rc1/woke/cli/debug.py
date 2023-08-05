import asyncio
import sys
from pathlib import Path
from typing import AnyStr, Generator, Iterable, Optional, Tuple

import click
from click.core import Context
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from sympy import Symbol

from woke.ast.b_solc.c_ast_nodes import (
    AstSolc,
    SolcContractDefinition,
    SolcFunctionDefinition,
    SolcVariableDeclaration,
    SrcParsed,
)
from woke.compile import SolcOutputSelectionEnum, SolidityCompiler
from woke.compile.solc_frontend import SolcOutputErrorSeverityEnum
from woke.compile.source_unit_name_resolver import SourceUnitNameResolver
from woke.config import WokeConfig
from woke.regex_parsing import SolidityVersion
from woke.symbolic_execution.ast.engine import AstExecutionEngine

from ..symbolic_execution.ast.variable import AstDeclaredVariable
from .console import console


@click.command(name="debug")
@click.argument("file", nargs=1, type=click.Path(exists=True))
@click.argument("contract_name", nargs=1)
@click.argument("function_name", nargs=1)
@click.pass_context
def run_debug(ctx: Context, file: AnyStr, contract_name: str, function_name: str) -> None:
    config = WokeConfig()
    config.load_configs()  # load ~/.woke/config.toml and ./woke.toml

    path = Path(file)
    if not path.is_file() or not path.match("*.sol"):
        raise ValueError(f"Argument `{file}` is not a Solidity file.")

    asyncio.run(debug(config, path, contract_name, function_name))


def _line_number_from_offset(s: str, byte_offset: int) -> int:
    substr = s[:byte_offset]
    return len(substr.splitlines())


def _generate_local_variables_table(width: int, local_variables: Iterable[AstDeclaredVariable]) -> Table:
    table = Table(title="Local variables", width=width)
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Value")

    for variable in local_variables:
        table.add_row(variable.name, variable.expression.type, str(variable.expression))
    return table


def _generate_state_variables_table(width: int, state_variables: Iterable[AstDeclaredVariable]) -> Table:
    table = Table(title="State variables", width=width)
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Value")

    for variable in state_variables:
        table.add_row(variable.name, variable.expression.type, str(variable.expression))
    return table


def _compute_code_lines(func_start: int, func_end: int, total_file_lines: int, layout_height: int, current_statement_start: int) -> Tuple[Optional[int], Optional[int]]:
    if total_file_lines <= layout_height:
        # whole file fits into the viewport
        return 0, None
    if func_end - func_start <= layout_height:
        # whole function fits into the viewport
        if func_start + layout_height > total_file_lines:
            start = total_file_lines - layout_height
            return max(0, start), start + layout_height
        return func_start, func_start + layout_height
    return current_statement_start, current_statement_start + layout_height


class GeneratorWithRet:
    __f: Generator

    def __init__(self, f: Generator):
        self.__f = f

    def __iter__(self):
        self.value = yield from self.__f


async def debug(config: WokeConfig, path: Path, contract_name: str, function_name: str) -> None:
    compiler = SolidityCompiler(config, [path])
    out = await compiler.compile([SolcOutputSelectionEnum.AST], write_artifacts=True)

    if len(out) != 1:
        raise NotImplementedError()
    out = out[0]

    if out.errors is not None:
        if any(err for err in out.errors if err.severity == SolcOutputErrorSeverityEnum.ERROR):
            m = "\n".join(err.formatted_message for err in out.errors if err.severity == SolcOutputErrorSeverityEnum.ERROR)
            raise Exception(m)

    source_unit_name_resolver = SourceUnitNameResolver(config)
    source_unit_name = source_unit_name_resolver.resolve_cmdline_arg(str(path))

    if out.sources is None:
        raise Exception()

    raw_ast = next(data.ast for unit_name, data in out.sources.items() if unit_name == source_unit_name)
    ast = AstSolc.parse_obj(raw_ast)

    contract = next(node for node in ast.nodes if isinstance(node, SolcContractDefinition) and node.name == contract_name)

    engine = AstExecutionEngine(contract)

    #console.print_json(function.json(exclude_none=True))

    # UI part
    code = path.read_text(encoding="utf-8")
    file_lines_count = len(code.splitlines())

    layout = Layout()
    layout.split_column(
        Layout(name="upper", ratio=2),
        Layout(name="lower", ratio=1)
    )
    layout["upper"].split_row(
        Layout(name="code", ratio=1),
        Layout(name="variables", ratio=1),
    )

    syntax = Syntax(code, "Solidity", theme="material", background_color="default", line_numbers=True)
    #syntax.line_pointers = {18: "● "}
    code_size = (console.width // 3 * 2, console.height // 3 * 2)
    layout["code"].update(syntax)

    locals_size = (console.width // 2, console.height // 3 * 2)
    variables = Group(
        _generate_local_variables_table(locals_size[0], []),
        _generate_state_variables_table(locals_size[0], []),
    )
    layout["variables"].update(variables)

    command = None
    #stepper = GeneratorWithRet(engine.run(SolidityVersion.fromstring("0.8.10"), state_variables, {"_addr1": 0x12345, "_i": 10}, {"nested": {10: {}, 0x12345: {10: True, 11: False}}}))
    #stepper = GeneratorWithRet(engine.run(SolidityVersion.fromstring("0.8.10"), state_variables, {"_addr": 0x12345}, {"myMap": {10: 12, 0x12345: 20}}))
    stepper = GeneratorWithRet(engine.run(function_name, SolidityVersion.fromstring("0.8.10"), {"a": 3, "b": Symbol("b")}, {}))


    with Live(layout, console=console, auto_refresh=False, screen=True, transient=True):
        for node, context in stepper:
            func_start_line = _line_number_from_offset(code, context.executed_function.src.byte_offset)
            func_end_line = _line_number_from_offset(code, context.executed_function.src.byte_offset + context.executed_function.src.byte_length)

            start_line = _line_number_from_offset(code, node.src.byte_offset)
            end_line = _line_number_from_offset(code, node.src.byte_offset + node.src.byte_length)
            syntax.line_range = _compute_code_lines(func_start_line, func_end_line, file_lines_count, code_size[1], start_line)
            syntax.highlight_lines = set(range(start_line, end_line + 1))
            syntax.style_overrides = [((node.src.byte_offset, node.src.byte_offset + node.src.byte_length), Style(underline=True))]

            layout["code"].update(syntax)
            variables = Group(
                _generate_local_variables_table(locals_size[0], context.get_local_variables()),
                _generate_state_variables_table(locals_size[0], context.get_state_variables()),
            )
            layout["variables"].update(variables)

            prev_command = command
            command = Prompt.ask(">>>", console=console)
            while command != "n":
                if len(command) == 0 and prev_command is not None:
                    command = prev_command

                if command in {"q", "quit", "exit"}:
                    sys.exit(0)
                elif command in {"n", "next"}:
                    break

                command = Prompt.ask("Command")

    if isinstance(stepper.value, AstDeclaredVariable):
        print(f"Returned {repr(stepper.value.expression)}")
    else:
        print(f"Returned {repr(stepper.value)}")
