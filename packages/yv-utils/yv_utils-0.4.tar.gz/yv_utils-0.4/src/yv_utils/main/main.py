from tqdm.auto import tqdm
import multiprocessing as mp
import numpy as np
import pandas as pd

""" VERIFICATION UTILS """
def run_sample_tqdm():
    for i in tqdm(range(100000)):
        pass



""" FASTER CODE """

def _initialize_mp():
    cores = mp.cpu_count()
    print(f"Making processes faster with {cores} cores!")
    return cores


def pd_parallel_apply(Series, fun):
    cores = _initialize_mp()
    split_ser = np.array_split(Series, cores)
    with mp.Pool(cores) as p:
        app = pd.concat(p.map(fun, split_ser), axis=0)

    return app
