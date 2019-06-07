import sys
import time

import simpleecs

COMP_TEMPLATE = """
@simpleecs.Component()
class NullComponent{}:
    name: str = ""
"""


for i in range(10_000):
    exec(COMP_TEMPLATE.format(i)) # pylint:disable=exec-used


class NullSystem:
    component_types = [
    ]
    def init_components(self, components):
        pass

    def destroy_components(self, components):
        pass

    def update(self, _dt, _components):
        pass


def benchmark(num_entities=1, num_components=1):
    print('Entities: {}, Components: {}'.format(num_entities, num_components))
    start = time.perf_counter_ns()
    world = simpleecs.ECSManager()
    system = NullSystem()
    system.component_types = [
        globals()['NullComponent{}'.format(i)]
        for i in range(num_components)
    ]
    world.add_system(system)
    for _ in range(num_entities):
        entity = world.create_entity()
        for j in range(num_components):
            comp = globals()['NullComponent{}'.format(j)]()
            entity.add_component(comp)
    setup_end = time.perf_counter_ns()
    world.update(0)
    update_end = time.perf_counter_ns()

    setup_time = (setup_end - start) / 100_000
    update_time = (update_end - setup_end) / 100_000
    total_time = setup_time + update_time
    print('\t{:0.2f}ms (setup: {:0.2f}ms, update: {:0.2f}ms)'.format(
        total_time,
        setup_time,
        update_time,
    ))

    return total_time, setup_time, update_time


if __name__ == '__main__':
    INCS = [100, 1000, 10000]
    print('Memory:')
    print('\tEntity: {}, NullComponent: {}'.format(
        sys.getsizeof(simpleecs.ECSManager().create_entity()),
        sys.getsizeof(globals()['NullComponent0']())
    ))
    benchmark()
    for inc in INCS:
        benchmark(num_entities=inc)
    for inc in INCS:
        benchmark(num_components=inc)
