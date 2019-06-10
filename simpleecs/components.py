import panda3d.core as p3d

from . import core


@core.Component()
class NullComponent:
    number: int = 0


@core.Component()
class NodePathComponent:
    name: str
    parent: p3d.NodePath
    nodepath: p3d.NodePath = None


@core.Component()
class StaticMeshComponent:
    modelpath: str
