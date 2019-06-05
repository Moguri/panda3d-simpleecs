import pytest

import simpleecs

#pylint:disable=redefined-outer-name
#pylint:disable=invalid-name


@pytest.fixture
def manager():
    return simpleecs.ECSManager()


@simpleecs.Component()
class CountComponent:
    name: str


class CountingSystem:
    num_components = 0
    component_types = [
        CountComponent,
    ]
    def init_components(self, components):
        for _ in components[CountComponent]:
            self.num_components += 1

    def destroy_components(self, components):
        for _ in components[CountComponent]:
            self.num_components -= 1

    def update(self, _dt, _components):
        pass


def test_add_remove_system(manager):
    manager.add_system(CountingSystem())
    assert manager.has_system(CountingSystem)

    manager.remove_system(CountingSystem)
    assert not manager.has_system(CountingSystem)


def test_update(manager):
    manager.update(0.1)


def test_system_init_destroy_components(manager):
    counting_system = CountingSystem()
    entity = manager.create_entity()
    entity.add_component(CountComponent(name='foo'))
    manager.add_system(counting_system)

    assert counting_system.num_components == 0

    manager.update(0)
    assert counting_system.num_components == 1

    manager.remove_entity(entity)
    entity = None
    manager.update(0)
    assert counting_system.num_components == 0

    manager.update(0)
    assert counting_system.num_components == 0
