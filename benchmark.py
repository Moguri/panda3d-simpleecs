import sys
import time

import simpleecs

@simpleecs.Component()
class NullComponent:
    name: str = ""


for i in range(10_000):
    compname = 'NullComponent{}'.format(i)
    globals()[compname] = type(compname, NullComponent.__bases__, dict(NullComponent.__dict__))


class NullSystem:
    def init_components(self, components):
        pass

    def destroy_components(self, components):
        pass

    def update(self, _dt, _components):
        pass


def benchmark(num_entities=1, num_components=1):
    print('Entities: {}, Components: {}'.format(num_entities, num_components))
    start = time.perf_counter_ns()
    world = simpleecs.World()
    system = NullSystem()
    world.add_system(system)
    globals_dict = globals()
    for _ in range(num_entities):
        world.create_entity([
            globals_dict['NullComponent{}'.format(compnum)]()
            for compnum in range(num_components)
        ])
    setup_end = time.perf_counter_ns()
    world.update(0)
    update_end = time.perf_counter_ns()
    world.update(0)
    warm_update_end = time.perf_counter_ns()

    setup_time = (setup_end - start) / 100_000
    update_time = (update_end - setup_end) / 100_000
    warm_update_time = (warm_update_end - update_end) / 100_000
    total_time = setup_time + update_time
    print('\t{:0.2f}ms (setup: {:0.2f}ms, update: {:0.2f}ms, warm update: {:0.2f}ms)'.format(
        total_time,
        setup_time,
        update_time,
        warm_update_time,
    ))

    return total_time, setup_time, update_time


if __name__ == '__main__':
    print('=Memory=')
    print('Entity: {}, NullComponent: {}'.format(
        sys.getsizeof(simpleecs.World().create_entity()),
        sys.getsizeof(globals()['NullComponent0']())
    ))
    print()

    print('=Time=')
    INCS = [1, 100, 1000]
    for num_ent in INCS:
        for num_comp in INCS:
            benchmark(num_entities=num_ent, num_components=num_comp)
