#!/usr/bin/env python

from glob import glob
from typing import Optional, List
from functools import partial
from multiprocessing import Pool, cpu_count
import logging
import os

import importlib

from deeprankcore.models.query import Query


_log = logging.getLogger(__name__)


def _preprocess_one_query(prefix: str, feature_names: List[str], query: Query):

    # because only one process may access an hdf5 file at the time:
    output_path = f"{prefix}-{os.getpid()}.hdf5"

    feature_modules = [importlib.import_module(name) for name in feature_names]

    graph = query.build_graph(feature_modules)

    graph.write_to_hdf5(output_path)


def preprocess(feature_modules: List, queries: List[Query],
               prefix: Optional[str] = None,
               process_count: Optional[int] = None):

    """
    Args:
        feature_modules: the feature modules used to generate features, each must implement the add_features function
        queries: all the queri objects that have to be preprocessed
        prefix: prefix for the output files, ./preprocessed-data- by default
        process_count: how many subprocesses will I run simultaneously, by default takes all available cpu cores.
    """

    if process_count is None:
        process_count = cpu_count()

    if prefix is None:
        prefix = "preprocessed-data"

    pool_function = partial(_preprocess_one_query, prefix,
                            [m.__name__ for m in feature_modules])

    with Pool(process_count) as pool:
        pool.map(pool_function, queries)

    output_paths = glob(f"{prefix}-*.hdf5")
    return output_paths
