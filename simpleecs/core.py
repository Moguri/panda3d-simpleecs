import collections
import dataclasses
import weakref


class Component():
    def __init__(self):
        pass

    def __call__(self, cls):
        cls = dataclasses.dataclass(cls, eq=False)
        def _entity_prop(self):
            return self._entity()
        cls.entity = property(_entity_prop)
        return cls


class Entity():
    __slots__ = [
        '__weakref__',
        '_world',
        'guid',
    ]

    def __init__(self, world):
        self._world = weakref.ref(world)
        self.guid = None

    @property
    def world(self):
        return self._world()

    def add_component(self, component):
        return self.world.add_component(self, component)

    def remove_component(self, component):
        return self.world.remove_component(self, component)

    def get_component(self, typeid):
        return self.world.get_component(self, typeid)

    def has_component(self, typeid):
        return self.world.has_component(self, typeid)


class System():
    def init_components(self, components):
        pass

    def destroy_components(self, components):
        pass

    def update(self, dt, components):
        pass


class DuplicateSystemException(Exception):
    pass


class World():
    def __init__(self):
        self.entities = set()
        self.systems = {}
        self.next_entity_guid = 0
        self._dead_entities = set()
        self._components = collections.defaultdict(list)
        self._new_components = collections.defaultdict(list)
        self._dead_components = collections.defaultdict(list)

    def create_entity(self, components=None):
        entity = Entity(self)
        self._add_entity(entity)

        if components:
            for comp in components:
                self.add_component(entity, comp)

        return entity

    def _add_entity(self, entity):
        entity.guid = self.next_entity_guid
        self.next_entity_guid += 1
        self.entities.add(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)
        for compdict in (self._new_components, self._components):
            for typeid in compdict:
                _ = [
                    self.remove_component(entity, comp)
                    for comp in compdict[typeid]
                    if comp.entity.guid == entity.guid
                ]
        self._dead_entities.add(entity)

    def add_system(self, system):
        system_type = type(system)
        if self.has_system(system_type):
            raise DuplicateSystemException("{} has already been added.".format(system_type))
        self.systems[system_type] = system
        system.init_components(self._components)

    def has_system(self, system_type):
        return system_type in self.systems

    def get_system(self, system_type):
        if not self.has_system(system_type):
            raise KeyError('No system found with the name of {}'.format(system_type))
        return self.systems[system_type]

    def remove_system(self, system_type):
        if not self.has_system(system_type):
            raise KeyError('No system found with the name of {}'.format(system_type))
        del self.systems[system_type]

    def add_component(self, entity, component):
        typeid = type(component)
        component._entity = weakref.ref(entity) # pylint: disable=protected-access
        self._new_components[typeid].append(component)

    def remove_component(self, _, component):
        typeid = type(component)
        found_component = False
        try:
            self._components[typeid].remove(component)
            found_component = True
        except ValueError:
            pass
        try:
            self._new_components[typeid].remove(component)
            found_component = True
        except ValueError:
            pass

        if found_component:
            self._dead_components[typeid].append(component)
        else:
            raise KeyError('World has no component with typeid of {}'.format(typeid))

    def get_component(self, entity, typeid):
        comps = self.get_components(entity, typeid)
        if not comps:
            raise ValueError(
                'Entity has no component with a typeid of {}'.format(typeid)
            )
        elif len(comps) > 1:
            raise RuntimeError(
                'Entity has more than one component with typeid of {}'.format(typeid)
            )

        return comps[0]

    def get_components(self, entity, typeid):
        return [
            comp for comp in self._components[typeid]
            if comp.entity.guid == entity.guid
        ] + [
            comp for comp in self._new_components[typeid]
            if comp.entity.guid == entity.guid
        ]

    def has_component(self, entity, typeid):
        return bool(self.get_components(entity, typeid))

    def update(self, dt):
        for system in self.systems.values():
            system.init_components(
                self._new_components
            )
            system.destroy_components(
                self._dead_components
            )

        for typeid, clist in self._new_components.items():
            self._components[typeid].extend(clist)
        self._new_components.clear()
        self._dead_components.clear()
        self._dead_entities.clear()

        for system in self.systems.values():
            system.update(dt, self._components)
