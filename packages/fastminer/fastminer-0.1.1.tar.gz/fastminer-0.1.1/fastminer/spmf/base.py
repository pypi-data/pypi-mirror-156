import logging
import os
import pathlib
import subprocess
import tempfile
from abc import abstractmethod

from pydantic import BaseModel

SPMF_JAR_PATH = pathlib.Path(__file__).parent.parent / "jars/spmf.jar"
OUTPUT_FILE_PATH = "spmf-output.txt"
FIM_SPLITTER = "#SUP:"
ENCODING = "UTF-8"

logger = logging.getLogger(__name__)

FIMResult = list[tuple[list[int], int]]
Transaction = list[int]


class BaseMiner(BaseModel):
    memory: int = 8192

    @abstractmethod
    def arguments(self) -> list[str]:
        ...

    def process(self, transactions: list[Transaction]) -> FIMResult:
        self.run(transactions)
        return self._export()

    def run(self, transactions: list[Transaction]) -> None:
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(
                bytes("\n".join(" ".join(map(str, t)) for t in transactions), ENCODING)
            )
            tf.flush()
            # http://www.philippe-fournier-viger.com/spmf/index.php?link=FAQ.php#memory
            subprocess_arguments = [
                "java",
                f"-Xmx{self.memory}m",
                "-jar",
                SPMF_JAR_PATH.as_posix(),
                "run",
                # use the class's name as the algorithm's name, it has to be a exact match
                self.__class__.__name__,
                tf.name,
                OUTPUT_FILE_PATH,
            ]
            subprocess_arguments.extend(self.arguments())

            proc = subprocess.check_output(subprocess_arguments)
            proc_output = proc.decode()
            print(proc_output)
            if "java.lang.IllegalArgumentException" in proc_output:
                raise TypeError("java.lang.IllegalArgumentException")

    # only freq itemset mining format is supported now
    def _export(self) -> FIMResult:
        with open(OUTPUT_FILE_PATH, "r") as f:
            res = []
            for line in f.readlines():
                items, support = list(
                    map(lambda x: x.strip(), line.strip().split(FIM_SPLITTER))
                )
                res.append((list(map(int, items.split())), int(support)))
            os.remove(f.name)  # cleanup
            return res
