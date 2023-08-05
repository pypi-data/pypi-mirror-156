from ctypes import Union
from msilib import sequence
from pathlib import Path
from typing import Dict, List, Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, root_validator, validator


class FileOperationConfiguration(BaseModel):
    source_path: Path = Field(..., alias="sourcePath", description="Source path")
    destination_path: Path = Field(
        ..., alias="destionationPath", description="Destination path"
    )
    echo: bool = Field(..., description="Logging information about the file operation")
    recursive: bool = Field(..., description="Recursive file operation")


class FileOperation(BaseModel):
    configuration: FileOperationConfiguration
    node_step: bool = Field(...)
    type: Literal["copyfile"] = Field(...)


class CommandExec(BaseModel):
    exec: str = Field(..., description="Command to execute")


class ScriptExec(BaseModel):
    script: str
    args: str
    description: Optional[str]
    file_extension: Optional[str] = Field(
        alias="fileExtension", description="File extension"
    )
    interpreter_args_quoted: bool = Field(
        False,
        alias="interpreterArgsQuoted",
        description="Quoted script path and arguments",
    )
    script_interpreter: Optional[str] = Field(
        alias="scriptInterpreter", description="Script interpreter"
    )


class JobRefImpl(BaseModel):
    name: str
    args: str
    uuid: str = Field(description="UUID of reference job")
    group: Optional[str] = Field("")
    node_step: Optional[str] = Field("true", alias="nodeStep", description="")
    use_name: Optional[str] = Field("true", alias="useName", description="")


class JobRef(BaseModel):
    jobref: JobRefImpl


class JobSequence(BaseModel):
    sequence: List[Union[CommandExec, FileOperation, JobRef]] = Field()
    keepgoing: bool = Field(
        False, description="If True, run remaining steps before failing"
    )
    strategy: Literal["node-first", "parallel", "sequential"] = Field(
        "node-first",
        description="node-first: Execute all steps on a node before proceeding to the next node.\n"
        "parallel: Run all steps in parallel\n"
        "sequential: Run each step in order. Execute a step on all nodes before proceeding to the next step",
    )


class Option(BaseModel):
    name: str = Field(description="Name of the option")
    value: str = Field(description="Value of the option")
    delimiter: Optional[str] = Field(None, description="Delimiter for multiple values")
    label: Optional[str] = Field(None, description="Label for the option")
    multivalued: bool = Field(
        False, description="If True, the option is a list of values"
    )
    hidden: bool = Field(
        False, description="If True, the option is not shown in the UI"
    )
    required: bool = Field(False, description="If True, the option is required")


class JobDefinition(BaseModel):
    default_tab: str = Field(
        "nodes",
        alias="defaultTab",
        description="Default opening tab on the job definition page",
    )
    name: Optional[str] = Field(description="Name of the job")
    description: Optional[str] = Field(description="Label of the job")
    execution_enabled: Optional[bool] = Field(
        True, alias="executionEnabled", description="A permission to run the job"
    )
    id: str = Field(uuid4(), description="Id of the job definition")
    loglevel: Literal["DEBBUG", "INFO", "WARN", "ERROR"] = Field(
        description="Filtering by a log level."
    )
    max_multiple_execution: Optional[str] = Field(
        alias="maxMultipleExecutions", description=""
    )
    multiple_executions: bool = Field(
        True,
        alias="multipleExecutions",
        description="If True, allow multiple executions",
    )
    node_filter_editable: str = Field(alias="nodeFilterEditable", description="")
    sequence: JobSequence = Field(..., description="Sequence of job steps")
    plugins: Optional[List[Dict[str, Optional[str]]]] = Field(description="")
    options: Optional[List[Option]] = Field(description="List of options")
    retry: Optional[str] = Field(
        None, description="Maximum retry if failing to execute the job"
    )
    schedule_enabled: Optional[bool] = Field(
        True, description="If true, allow scheduling"
    )
    uuid: str = Field(uuid4(), description="UUID of the job definition")

    @root_validator
    def id_validator(cls, values):
        if "id" not in values:
            values["id"] = values["uuid"]
