import panda3d.core as p3d

from . import core
from . import components as pcomps


class Panda3DBaseSystem(core.System):
    def get_nodepath(self, component):
        return component.entity.get_component(pcomps.NodePathComponent).nodepath

    def init_components(self, components):
        for comp in components[pcomps.NodePathComponent]:
            comp.nodepath = p3d.NodePath(p3d.PandaNode(comp.name))
            if comp.parent is not None:
                comp.nodepath.reparent_to(comp.parent)

        for comp in components[pcomps.StaticMeshComponent]:
            nodepath = self.get_nodepath(comp)
            comp.model = p3d.NodePath(p3d.Loader().get_global_ptr().load_sync(comp.modelpath))
            comp.model.reparent_to(nodepath)

    def destroy_components(self, components):
        for comp in components[pcomps.NodePathComponent]:
            if comp.nodepath:
                comp.nodepath.remove_node()
