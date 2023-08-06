import multiprocessing as mp


def initialize_mp():
    cores = mp.cpu_count()
    print(f"Making processes faster with {cores} cores!")
    return cores


def pd_parallel_apply(Series, fun):
    cores = initialize_mp()
    with mp.Pool(cores) as p:
        app = p.map(Series, fun)

    return app

