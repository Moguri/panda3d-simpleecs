import pytest

import simpleecs

#pylint:disable=redefined-outer-name
#pylint:disable=invalid-name


@pytest.fixture
def world():
    return simpleecs.World()


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


def test_add_remove_system(world):
    world.add_system(CountingSystem())
    assert world.has_system(CountingSystem)

    world.remove_system(CountingSystem)
    assert not world.has_system(CountingSystem)


def test_update(world):
    world.update(0.1)


def test_system_init_destroy_components(world):
    counting_system = CountingSystem()
    entity = world.create_entity()
    entity.add_component(CountComponent(name='foo'))
    world.add_system(counting_system)

    assert counting_system.num_components == 0

    world.update(0)
    assert counting_system.num_components == 1

    world.remove_entity(entity)
    entity = None
    world.update(0)
    assert counting_system.num_components == 0

    world.update(0)
    assert counting_system.num_components == 0
