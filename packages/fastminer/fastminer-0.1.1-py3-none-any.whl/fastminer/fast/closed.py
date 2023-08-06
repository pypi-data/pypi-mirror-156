import os
import pathlib

LIB_PATH = (pathlib.Path(__file__).parent.parent / 'jars/fastminer.jar').as_uri()
os.environ['CLASSPATH'] = LIB_PATH

from jnius import autoclass

NEclatClosedClass = autoclass("fastminer.algo.closed.NEclatClosed")

class NEclatClosed:
    def __init__(self, min_support: float) -> None:
        self.min_support = min_support

    def process(self, transactions: list[list[int]]) -> list[tuple[list[int], int]]:
        neclat = NEclatClosedClass()
        res =  neclat.process(transactions, self.min_support)
        return [([i for i in itemset.indices], itemset.support) for itemset in res]
