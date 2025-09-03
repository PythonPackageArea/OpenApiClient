from enum import Enum
from typing import Optional, Union, TYPE_CHECKING, Literal, Any, Dict, List
from dataclasses import dataclass

from pydantic import BaseModel, field_validator


class DefaultValue(str, Enum):
    DEFAULT = "DEFAULT"


class Variable(BaseModel):
    value: list[Union["Variable", str]] = []
    wrap_name: Optional[str] = None

    @field_validator("value", mode="before")
    def value_check(cls, value):
        _value = value

        if not isinstance(value, list):
            _value = [value]

        return _value

    def __str__(self):

        _value = self.value

        if isinstance(self.value, list):
            _value = ", ".join([_.__str__() for _ in self.value])

        if self.wrap_name is None:
            return _value

        if set("Literal").intersection({self.wrap_name}):
            _value = ", ".join([_.__repr__() for _ in _value.split(", ")])

        return self.__wrap(_value, self.wrap_name)

    def __iter__(self):
        for _ in self.value:
            if isinstance(_, Variable):
                for __ in _:
                    yield __
            else:
                yield _

    @classmethod
    def __wrap(cls, value: str, wrap_name: str):
        return f"{wrap_name}[{value}]" if value else "any"


class Parameter(BaseModel):
    name: str

    default: Optional[Variable] = None
    var_type: Optional[Variable] = None

    order: int = 0

    def set_default(self, default: Union[str, Variable], **kwargs):
        if isinstance(default, str):
            default = Variable(value=default, **kwargs)

        self.default = default

    def set_type(self, var_type: Union[str, Variable], **kwargs):
        if isinstance(type, str):
            var_type = Variable(value=var_type, **kwargs)

        self.var_type = var_type

    def __str__(self):
        return (
            self.name
            + (f": {self.var_type}" if self.var_type else "")
            + (f" = {self.default}" if self.default else "")
        )
        # return (" " if self.type else "").join(filter(bool, [
        #     self.name + ": " + self.type if self.type else self.name,
        #     ("= " if self.type else "=") + self.default if self.default else ""
        # ]))


class CodeBlock(BaseModel):
    order: int = 0
    code: str = "pass"

    def __str__(self):
        return self.code.replace("\t", "    ")


class Reference(BaseModel):
    file: Optional["CodeFile"] = None
    back: Optional["Class"] = None


@dataclass
class ParameterMetadata:
    """Метаданные параметра из OpenAPI"""

    name: str
    description: Optional[str] = None
    required: bool = False
    deprecated: bool = False
    example: Any = None
    examples: Dict[str, Any] = None
    schema: Dict[str, Any] = None


@dataclass
class FunctionMetadata:
    """Полные метаданные функции из OpenAPI"""

    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    deprecated: bool = False
    tags: List[str] = None
    security: List[Dict[str, List[str]]] = None
    parameters: List[ParameterMetadata] = None
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = None
    examples: Dict[str, Any] = None


@dataclass
class EndpointError:
    """Модель ошибки эндпоинта"""

    status_code: int
    description: str
    schema: Dict[str, Any] = None
    example: Any = None


class Function(BaseModel):
    name: str
    parameters: list[Parameter] = []
    response: str = "None"

    async_def: bool = False
    decorators: list[str] = []

    description: Optional[str] = None
    deprecated: bool = False
    tags: list[str] = []

    # Продвинутые метаданные
    metadata: Optional[FunctionMetadata] = None
    errors: List[EndpointError] = []
    examples: Dict[str, Any] = {}

    code: CodeBlock = CodeBlock(order=0, code="pass")

    references: "Reference"
    order: int = 0

    def __str__(self) -> str:
        many_parameters = len(self.parameters) > 1

        docstring = self._generate_docstring()

        decorators_str = "\n".join(self.decorators)
        if self.deprecated:
            decorators_str = "@deprecated\n" + decorators_str

        return (
            (
                decorators_str
                + "\n".join(
                    [
                        f"{'async ' if self.async_def else ''}def {self.name}("
                        + (
                            ("\n\t" if many_parameters else "")
                            + (",\n\t" if many_parameters else ", ").join(
                                map(
                                    str,
                                    sorted(
                                        self.parameters, key=lambda x: bool(x.default)
                                    ),
                                )
                            )
                            + ("\n||" if many_parameters else "")
                            if self.parameters
                            else ""
                        )
                        + f") -> {self.response}:\n"
                        # "\t" + (',\n\t'.join(map(str, sorted(self.parameters, key=lambda x: bool(x.default))))),
                        # f"||) -> {self.response}:\n"
                    ]
                )
                + (
                    "\n    " + docstring.replace("\n", "\n    ") + "\n"
                    if docstring
                    else ""
                )
                + "\n    "
                + str(self.code).replace(
                    "\n", "\n    "
                )  # Добавляем 4 пробела к коду функции
            )
            .replace("||", "")  # Убираем маркеры
            .replace("\t", "    ")
        )

    def _generate_docstring(self) -> str:
        """Генерация подробного docstring на основе метаданных"""
        if not self.metadata and not self.description:
            return ""

        lines = ['"""']

        # Основное описание
        if self.metadata and self.metadata.summary:
            lines.append(self.metadata.summary)
        elif self.description:
            lines.append(self.description)

        # Подробное описание
        if self.metadata and self.metadata.description:
            lines.append("")
            lines.append(self.metadata.description)

        # Параметры
        if self.parameters:
            lines.append("")
            lines.append("Args:")
            for param in self.parameters:
                param_name = param.name
                param_type = str(param.var_type) if param.var_type else "Any"

                # Ищем описание параметра в метаданных
                param_desc = ""
                if self.metadata and self.metadata.parameters:
                    for meta_param in self.metadata.parameters:
                        if meta_param.name == param.name.replace("_path", "").replace(
                            "_query", ""
                        ).replace("_body", ""):
                            param_desc = meta_param.description or ""
                            break

                lines.append(
                    f"    {param_name} ({param_type}): {param_desc or 'Parameter description'}"
                )

        # Возвращаемое значение
        if self.response and self.response != "None":
            lines.append("")
            lines.append("Returns:")
            lines.append(f"    {self.response}: Response data")

        # Ошибки
        if self.errors:
            lines.append("")
            lines.append("Raises:")
            for error in self.errors:
                lines.append(f"    {error.status_code}: {error.description}")

        # Примеры
        if self.examples:
            lines.append("")
            lines.append("Examples:")
            for example_name, example in self.examples.items():
                lines.append(f"    {example_name}: {example}")

        # Теги
        if self.tags:
            lines.append("")
            lines.append("Tags:")
            for tag in self.tags:
                lines.append(f"    - {tag}")

        lines.append('"""')
        return "\n".join(lines)

    def set_code_block(self, code_block: Union["CodeBlock", str]) -> "CodeBlock":
        if isinstance(code_block, str):
            code_block = CodeBlock(code=code_block)

        self.code = code_block
        return self

    def full_path(self) -> str:
        if self.references.back:
            return self.references.back.full_path() + "." + self.name

        else:
            return self.name


class Class(BaseModel):
    name: str

    functions: dict[str, "Function"] = {}
    classes: dict[str, "Class"] = {}

    code_blocks: list["CodeBlock"] = []
    parameters: list[Parameter] = []

    inherits: list[str] = []

    references: "Reference"

    order: int = 0

    def __str__(self) -> str:
        return (
            (
                f"class {self.name}"
                + (f"({', '.join(self.inherits)})" if self.inherits else "")
                + ":\n"
                + "\n\n".join(
                    filter(
                        bool,
                        [
                            (
                                "\n".join(
                                    map(
                                        lambda f: (
                                            "\n" if not isinstance(f, Parameter) else ""
                                        )
                                        + str(f),
                                        sorted(
                                            (
                                                self.parameters
                                                + self.code_blocks
                                                + list(self.functions.values())
                                                + list(self.classes.values())
                                            ),
                                            key=lambda x: x.order,
                                            reverse=True,
                                        ),
                                    )
                                )
                            ),
                        ],
                    )
                )
                + (
                    ""
                    if any(
                        [
                            self.functions,
                            self.classes,
                            self.parameters,
                            self.code_blocks,
                        ]
                    )
                    else "pass"
                )
            )
            .replace("\n", "\n    ")  # Отступ для содержимого класса
            .replace("\n    ||", "\n")  # Убираем маркеры
            .replace("\t", "    ")
        )

    def add_function(self, function: Union["Function", str], **kwargs) -> "Function":
        if isinstance(function, str):
            function = Function(name=function, **kwargs)

        function.references = Reference(file=self.references.file, back=self)
        self.functions[function.name] = function

        return function

    def add_class(self, cls: Union["Class", str], **kwargs) -> "Class":
        # print(cls)
        if isinstance(cls, str):
            cls = Class(name=cls, **kwargs)

        # print(cls)
        cls.references = Reference(file=self.references.file, back=self)
        self.classes[cls.name] = cls

        return cls

    def add_code_block(
        self, code_block: Union["CodeBlock", str], **kwargs
    ) -> "CodeBlock":
        if isinstance(code_block, str):
            code_block = CodeBlock(code=code_block, **kwargs)

        self.code_blocks.append(code_block)
        return self

    def full_path(self) -> str:
        if self.references.back:
            return self.references.back.full_path() + "." + self.name
        else:
            return self.name


class CodeFile(BaseModel):
    file_name: str

    imports: list[str] = []
    functions: dict[str, "Function"] = {}
    classes: dict[str, "Class"] = {}
    code_blocks: list["CodeBlock"] = []

    def __str__(self):
        return (
            "\n\n".join(
                filter(
                    bool,
                    [
                        ("\n".join(self.imports) if self.imports else ""),
                        (
                            "\n\n".join(
                                map(
                                    lambda f: str(f),
                                    sorted(
                                        (
                                            self.code_blocks
                                            + list(self.functions.values())
                                            + list(self.classes.values())
                                        ),
                                        key=lambda x: x.order,
                                        reverse=True,
                                    ),
                                )
                            )
                        ),
                    ],
                )
            )
        ).replace("\t", "    ")

    def add_function(self, function: Union["Function", str], **kwargs) -> "Function":
        if isinstance(function, str):
            function = Function(name=function, **kwargs)

        function.references = Reference(file=self, back=None)
        self.functions[function.name] = function

        return function

    def add_class(self, cls: Union["Class", str], **kwargs) -> "Class":
        if isinstance(cls, str):
            cls = Class(name=cls, **kwargs)

        cls.references = Reference(file=self, back=None)
        self.classes[cls.name] = cls

        return cls

    def add_code_block(
        self, code_block: Union["CodeBlock", str], **kwargs
    ) -> "CodeBlock":
        if isinstance(code_block, str):
            code_block = CodeBlock(code=code_block, **kwargs)

        self.code_blocks.append(code_block)
        return self

    def get_object(self, path: str):
        path = path.split(".")

        _current_object = self

        for _ in path:
            _current = None
            _current = _current_object.classes.get(_, _current)
            _current = _current_object.functions.get(_, _current)

            if not _current:
                break

            _current_object = _current

        return None if isinstance(_current_object, CodeFile) else _current_object


Reference.model_rebuild()

Class.__fields__["references"].default = Reference()
Class.update_forward_refs()

Function.__fields__["references"].default = Reference()
Function.update_forward_refs()


class Project(BaseModel):
    name: str
    files: list[CodeFile] = []

    def add_file(self, file_name: Union["CodeFile", str], **kwargs) -> "CodeFile":
        if isinstance(file_name, str):
            code_file = CodeFile(file_name=file_name, **kwargs)
            self.files.append(code_file)

            return code_file


# p = Project(name="test")
# A_class = p.add_file(file_name="file.py").add_class("A")

# A_class.add_code_block(
#     code_block=(
#         "with open(file):\n"
#         "    pass"
#     )
# )

# A_class.add_class("f")
#
# print(p.files[0])
#
# pp = Parameter(
#     name="a",
#     var_type=Variable(
#         wrap_name="Optional",
#         value=Variable(
#             wrap_name="Union",
#             value=["int", "str"],
#         ),
#     )
# )
# print(pp)

# f = Function(name="f", parameters=[Parameter(name="a", type="int")])
#
#
#
# t_c = Class(name="C")
# c = Class(name="C", classes={"t_c1": t_c, "t_c2": t_c, "t_c3": t_c}, functions={"f": f, "f2": f})
#
# file = CodeFile(file_name="file.py", classes={"c": c, "t_c": t_c})
# file.imports.append("import a")
# file.imports.append("import b")
#
# print(file)
