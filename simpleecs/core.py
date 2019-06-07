import collections
import dataclasses
import weakref


class Component():
    def __init__(self, unique=True):
        self.unique = unique

    def __call__(self, cls):
        cls = dataclasses.dataclass(cls, eq=False)
        cls.is_unique = self.unique
        def _entity_prop(self):
            return self._entity()
        cls.entity = property(_entity_prop)
        return cls


class Entity():
    __slots__ = [
        '_components',
        '_new_components',
        '_dead_components',
        '__weakref__',
        'guid',
    ]

    def __init__(self):
        self._components = collections.defaultdict(list)
        self._new_components = collections.defaultdict(list)
        self._dead_components = collections.defaultdict(list)
        self.guid = None

    def add_component(self, component):
        typeid = type(component)

        enforce_unique = component.is_unique
        if not enforce_unique:
            try:
                enforce_unique = bool([i for i in self.get_components(typeid) if i.is_unique])
            except KeyError:
                enforce_unique = False

        if enforce_unique and self.has_component(typeid):
            raise RuntimeError('Entity already has component with typeid of {}'.format(typeid))
        component._entity = weakref.ref(self) # pylint: disable=protected-access

        self._new_components[typeid].append(component)

    def remove_component(self, component):
        typeid = type(component)
        if typeid in self._components:
            cdict = self._components
            clist = self._components[typeid]
        elif typeid in self._new_components:
            cdict = self._new_components
            clist = self._new_components[typeid]
        else:
            raise KeyError('Entity has no component with typeid of {}'.format(typeid))

        self._dead_components[typeid].append(component)

        clist.remove(component)
        if not clist:
            del cdict[typeid]

    def clear_components(self):
        self._dead_components = {
            **self._dead_components,
            **self._new_components,
            **self._components
        }
        self._new_components.clear()
        self._components.clear()

    def clear_new_components(self):
        for typeid, clist in self._new_components.items():
            if typeid in self._components:
                self._components[typeid].extend(clist)
            else:
                self._components[typeid] = clist[:]
        self._new_components.clear()

    def clear_dead_components(self):
        self._dead_components.clear()

    def get_component(self, typeid):
        if len(self.get_components(typeid)) > 1:
            raise RuntimeError(
                'Entity has more than one component with typeid of {}'.format(typeid)
            )

        return self.get_components(typeid)[0]

    def get_components(self, typeid):
        if typeid in self._components:
            return self._components[typeid]
        elif typeid in self._new_components:
            return self._new_components[typeid]
        else:
            raise KeyError('Entity has no component with typeid of {}'.format(typeid))

    def has_component(self, typeid):
        return typeid in self._components or typeid in self._new_components


class System():
    def init_components(self, components):
        pass

    def destroy_components(self, components):
        pass

    def update(self, dt, components):
        pass


class DuplicateSystemException(Exception):
    pass


class ECSManager():
    def __init__(self):
        self.entities = set()
        self.systems = {}
        self.next_entity_guid = 0
        self._dead_entities = set()

    def create_entity(self):
        entity = Entity()
        self._add_entity(entity)

        return entity

    def _add_entity(self, entity):
        entity.guid = self.next_entity_guid
        self.next_entity_guid += 1
        self.entities.add(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)
        entity.clear_components()
        self._dead_entities.add(entity)

    def add_system(self, system):
        system_type = type(system)
        if self.has_system(system_type):
            raise DuplicateSystemException("{} has already been added.".format(system_type))
        self.systems[system_type] = system

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

    def _get_components_by_type(self, component_list, component_types):
        components = {k: [] for k in component_types}
        for entity in self.entities | self._dead_entities:
            for typeid in component_types:
                components[typeid] += getattr(entity, component_list).get(typeid, [])

        return components

    def update(self, dt):
        for system in self.systems.values():
            system.init_components(
                self._get_components_by_type('_new_components', system.component_types)
            )
            system.destroy_components(
                self._get_components_by_type('_dead_components', system.component_types)
            )

        for entity in self.entities:
            entity.clear_new_components()
            entity.clear_dead_components()
        self._dead_entities.clear()

        for system in self.systems.values():
            system.update(dt, self._get_components_by_type('_components', system.component_types))
