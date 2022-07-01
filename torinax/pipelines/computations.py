from typing import Dict, List, Tuple, Optional
from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from abc import ABC, abstractclassmethod
from torinax.clients import SlurmClient
#from dask.distributed import Client
from time import time
import dask as da
from . import SqlBase


def model_lookup_by_table_name(table_name: str):
    registry_instance = getattr(SqlBase, "registry")
    for mapper_ in registry_instance.mappers:
        model = mapper_.class_
        model_class_name = model.__tablename__
        if model_class_name == table_name:
            return model
    # if no module found, raise an error
    raise ValueError("Unknown table name {}. It does not exist in metadata.".format(table_name))

def _comp_sql_model_creator(comp_name: str, results_attr: Dict[str, Column]):
    """Method to dynamically make SQLAlchemy models for each computation to store their results and status"""
    attr_dict = {
        "__tablename__": comp_name,
        "id": Column(String(500), primary_key=True),
        "__table_args__": {'extend_existing': True}
    }
    attr_dict.update(results_attr)
    return type(comp_name, (SqlBase, ), attr_dict)


class Computation (ABC):

    """Abstract computation object"""

    tablename = "computation"
    name = "computation"
    __results_columns__ = {}

    def __init__(self):
        self.successful = False
        if self.tablename:
            self.sql_model = _comp_sql_model_creator(self.tablename, self.__results_columns__)

    @abstractclassmethod
    def execute(self, db_session) -> List[SqlBase]:
        """Method to execute the computation.
        ARGS:
            - db_session: session of SQL database with previous computation results"""
        pass

    def post_execution(self, db_session):
        """Method to run after computation is done"""
        pass

    def pre_execution(self, db_session):
        """Method to run before a computation is ran"""
        pass

    def _execute(self, db_session):
        """Internal method to execute a computation"""
        # executing all commands
        self.pre_execution(db_session)
        entries = self.execute(db_session)
        self.post_execution(db_session)
        # updating db with new results
        if len(entries) > 0:
            db_session.add_all(entries)
            db_session.commit()


class SlurmComputation (Computation):

    """Abstract computation to be executed in parallel on a SLURM cluster"""

    tablename = "slurm_computation"

    def __init__(self, slurm_client: SlurmClient):
        self.client = slurm_client
        super().__init__()

    @abstractclassmethod
    def make_cmd_list(self, db_session) -> Tuple[List[SqlBase], List[str]]:
        """Method to make list of command line strings for a single run in SLURM"""
        pass

    def execute(self, db_session) -> List[SqlBase]:
        """Execute list of command-line arguments on a SLURM cluster"""
        entries, cmds = self.make_cmd_list(db_session)
        # submit to client
        self.client.submit(cmds)
        # wating for task completion
        self.client.wait()
        return entries

class DaskComputation (Computation):

    tablename = "dask_computation"

    def __init__(self, dask_client, n_workers: int=1):
        self.n_workers = n_workers
        self.client = dask_client
        super().__init__()

    @abstractclassmethod
    def make_futures(self, db_session):
        """Method to future objects to be executed on Dask client"""
        pass

    def execute(self, db_session) -> List[SqlBase]:
        """Execute list of dask futures on a Dask cluster"""
        #self.client.cluster.scale(self.n_workers)
        futures = self.make_futures(db_session)
        dicts = da.compute(futures)[0]
        #self.client.cluster.scale(0)
        return [self.sql_model(**d) for d in dicts]

def run_computations(computations: List[Computation], db_path: Optional[str]=None, db_engine=None, db_session=None, verbose: int=1):
    """Method to execute multiple computations consecutively, and save results to a database file"""
    if not db_engine and not db_path and not db_session:
        raise ValueError("Must provide a value for either db_engine or db_path or db_session")
    # creating database session
    if not db_session:
        if db_engine:
            engine = db_engine
        elif db_path:
            engine = create_engine("sqlite3///{}".format(db_path))
        SqlBase.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
    else:
        session = db_session
    for comp in computations:
        if verbose > 0:
            print("Running {}".format(comp.name))
        t1 = time()
        comp._execute(session)
        t2 = time()
        if verbose > 0:
            print("{} done in {} seconds".format(comp.name, round(t2 - t1, 3)))
