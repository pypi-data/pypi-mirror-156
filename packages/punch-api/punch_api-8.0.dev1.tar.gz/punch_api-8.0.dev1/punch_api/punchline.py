#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License Agreement
# This code is licensed under the outer restricted Tiss license:
#
#  Copyright [2014]-[2019] Thales Services under the Thales Inner Source Software License
#  (Version 1.0, InnerPublic -OuterRestricted the "License");
#
#  You may not use this file except in compliance with the License.
#
#  The complete license agreement can be requested at contact@punchplatform.com.
#
#  Refer to the License for the specific language governing permissions and limitations
#  under the License.
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Column:
    """
    Column definition
    """

    name: str
    type: str | None = None


@dataclass
class Out:
    """
    Link Between nodes
    """

    id: str
    table: str = "default"
    columns: list[Column] = field(default_factory=list)

    def __post_init__(self):
        self.columns = [Column(**column) for column in self.columns]

    def __hash__(self):
        return hash((self.id, self.table))


@dataclass
class Node:
    """
    Generic node structure
    """

    id: str
    kind: str
    type: str
    settings: dict[str, Any] = field(default_factory=dict)
    out: list[Out] = field(default_factory=list)
    engine_settings: Any = None
    load_control: Any = None
    exit_conditions: Any = None

    def __post_init__(self):
        self.out: list[Out] = [Out(**out) for out in self.out]


@dataclass
class Metadata:
    """
    Kubernetes Metadata
    """

    name: str
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    uid: Any = None
    namespace: Any = None
    creationTimestamp: Any = None
    ownerReferences: Any = None
    resourceVersion: Any = None
    selfLink: Any = None
    generation: Any = None
    managedFields: Any = None
    finalizers: Any = None


@dataclass
class Spec:
    """
    Kubernetes Spec
    """

    dag: list[Node]
    engineSettings: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    jobSettings: Any = None
    configs: Any = None
    debug: Any = None
    containers: Any = None

    def __post_init__(self) -> None:
        self.dag: list[Node] = [Node(**node) for node in self.dag]


@dataclass
class Punchline:
    """
    Top level Punchline file structure
    """

    apiVersion: str
    kind: str
    metadata: Metadata
    spec: Spec
    status: Any = None

    def __post_init__(self) -> None:
        self.metadata: Metadata = Metadata(**self.metadata)
        self.spec: Spec = Spec(**self.spec)
