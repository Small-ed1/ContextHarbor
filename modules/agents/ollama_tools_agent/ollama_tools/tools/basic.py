from __future__ import annotations

import datetime

from pydantic import BaseModel

from ollama_tools.toolcore import ToolRegistry, ToolSpec


class CalcArgs(BaseModel):
    op: str
    a: float
    b: float


def calc(args: CalcArgs) -> float:
    op = args.op.lower().strip()

    if op in {"+", "add"}:
        return args.a + args.b
    if op in {"-", "sub", "subtract"}:
        return args.a - args.b
    if op in {"*", "mul", "multiply"}:
        return args.a * args.b
    if op in {"/", "div", "divide"}:
        return args.a / args.b

    raise ValueError("op must be one of add/sub/mul/div (or + - * /)")


CALC = ToolSpec(
    name="calc",
    description="Basic arithmetic. op is add/sub/mul/div (also accepts + - * /).",
    args_schema=CalcArgs,
    handler=calc,
)


class EchoArgs(BaseModel):
    text: str


def echo(args: EchoArgs) -> str:
    return f"Echo: {args.text}"


ECHO = ToolSpec(
    name="echo",
    description="Echo back the provided text.",
    args_schema=EchoArgs,
    handler=echo,
)


class GetTimeArgs(BaseModel):
    pass


def get_time(_: GetTimeArgs) -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


GET_TIME = ToolSpec(
    name="get_time",
    description="Get the current local time (HH:MM:SS).",
    args_schema=GetTimeArgs,
    handler=get_time,
)


def register_basic_tools(reg: ToolRegistry) -> None:
    reg.register(CALC)
    reg.register(ECHO)
    reg.register(GET_TIME)
