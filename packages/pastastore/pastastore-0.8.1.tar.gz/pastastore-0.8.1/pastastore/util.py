import os
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from numpy.lib._iotools import NameValidator
from tqdm import tqdm


def _custom_warning(message, category=UserWarning, filename='', lineno=-1,
                    *args):
    print(f"{filename}:{lineno}: {category.__name__}: {message}")


class ItemInLibraryException(Exception):
    pass


def delete_pystore_connector(conn=None,
                             path: Optional[str] = None,
                             name: Optional[str] = None,
                             libraries: Optional[List[str]] = None) -> None:
    """Delete libraries from pystore.

    Parameters
    ----------
    conn : PystoreConnector, optional
        PystoreConnector object
    path : str, optional
        path to pystore
    name : str, optional
        name of the pystore
    libraries : Optional[List[str]], optional
        list of library names to delete, by default None which deletes
        all libraries
    """
    import pystore

    if conn is not None:
        name = conn.name
        path = conn.path
    elif name is None or path is None:
        raise ValueError("Please provide 'name' and 'path' OR 'conn'!")

    print(f"Deleting PystoreConnector database: '{name}' ...", end="")
    pystore.set_path(path)
    if libraries is None:
        pystore.delete_store(name)
        print(" Done!")
    else:
        store = pystore.store(name)
        for lib in libraries:
            print()
            store.delete_collection(lib)
            print(f" - deleted: {lib}")


def delete_arctic_connector(conn=None,
                            connstr: Optional[str] = None,
                            name: Optional[str] = None,
                            libraries: Optional[List[str]] = None) -> None:
    """Delete libraries from arctic database.

    Parameters
    ----------
    conn : pastastore.ArcticConnector
        ArcticConnector object
    connstr : str, optional
        connection string to the database
    name : str, optional
        name of the database
    libraries : Optional[List[str]], optional
        list of library names to delete, by default None which deletes
        all libraries
    """
    import arctic

    if conn is not None:
        name = conn.name
        connstr = conn.connstr
    elif name is None or connstr is None:
        raise ValueError("Provide 'name' and 'connstr' OR 'conn'!")

    arc = arctic.Arctic(connstr)

    print(f"Deleting ArcticConnector database: '{name}' ... ", end="")
    # get library names
    if libraries is None:
        libs = []
        for ilib in arc.list_libraries():
            if ilib.split(".")[0] == name:
                libs.append(ilib)
    elif name is not None:
        libs = [name + "." + ilib for ilib in libraries]
    else:
        raise ValueError("Provide 'name' and 'connstr' OR 'conn'!")

    for lib in libs:
        arc.delete_library(lib)
        if libraries is not None:
            print()
            print(f" - deleted: {lib}")
    print("Done!")


def delete_dict_connector(conn, libraries: Optional[List[str]] = None) -> None:
    print(f"Deleting DictConnector: '{conn.name}' ... ", end="")
    if libraries is None:
        del conn
        print(" Done!")
    else:
        for lib in libraries:
            print()
            delattr(conn, f"lib_{conn.libname[lib]}")
            print(f" - deleted: {lib}")
    print("Done!")


def delete_pas_connector(conn, libraries: Optional[List[str]] = None) -> None:
    import shutil
    print(f"Deleting PasConnector database: '{conn.name}' ... ", end="")
    if libraries is None:
        shutil.rmtree(conn.path)
        print(" Done!")
    else:
        for lib in libraries:
            print()
            shutil.rmtree(os.path.join(conn.path, lib))
            print(f" - deleted: {lib}")
        print("Done!")


def delete_pastastore(pstore, libraries: Optional[List[str]] = None) -> None:
    """Delete libraries from PastaStore.

    Note
    ----
    This deletes the original PastaStore object. To access
    data that has not been deleted, it is recommended to create a new
    PastaStore object with the same Connector settings. This also creates
    new empty libraries if they were deleted.

    Parameters
    ----------
    pstore : pastastore.PastaStore
        PastaStore object to delete (from)
    libraries : Optional[List[str]], optional
        list of library names to delete, by default None which deletes
        all libraries

    Raises
    ------
    TypeError
        when Connector type is not recognized
    """
    if pstore.conn.conn_type == "pystore":
        delete_pystore_connector(
            conn=pstore.conn, libraries=libraries)
    elif pstore.conn.conn_type == "dict":
        delete_dict_connector(pstore)
    elif pstore.conn.conn_type == "arctic":
        delete_arctic_connector(conn=pstore.conn, libraries=libraries)
    elif pstore.conn.conn_type == "pas":
        delete_pas_connector(conn=pstore.conn, libraries=libraries)
    else:
        raise TypeError("Unrecognized pastastore Connector type: "
                        f"{pstore.conn.conn_type}")


def validate_names(s: Optional[str] = None, d: Optional[dict] = None,
                   replace_space: Optional[str] = "_",
                   deletechars: Optional[str] = None, **kwargs) \
        -> Union[str, Dict]:
    """Remove invalid characters from string or dictionary keys.

    Parameters
    ----------
    s : str, optional
        remove invalid characters from string
    d : dict, optional
        remove invalid characters from keys from dictionary
    replace_space : str, optional
        replace spaces by this character, by default "_"
    deletechars : str, optional
        a string combining invalid characters, by default None

    Returns
    -------
    str, dict
        string or dict with invalid characters removed
    """
    validator = NameValidator(replace_space=replace_space,
                              deletechars=deletechars,
                              **kwargs)
    if s is not None:
        new_str = validator(s)  # tuple
        if len(new_str) == 1:
            return new_str[0]
        else:
            return new_str
    elif d is not None:
        new_dict = {}
        for k, v in d.items():
            new_dict[validator(k)[0]] = v
        return new_dict
    else:
        raise ValueError("Provide one of 's' (string) or 'd' (dict)!")


def compare_models(ml1, ml2, stats=None, detailed_comparison=False):
    """Compare two Pastas models.

    Parameters
    ----------
    ml1 : pastas.Model
        first model to compare
    ml2 : pastas.Model
        second model to compare
    stats : list of str, optional
        if provided compare these model statistics
    detailed_comparison : bool, optional
        if True return DataFrame containing comparison details,
        by default False which returns True if models are equivalent
        or False if they are not

    Returns
    -------
    bool or pd.DataFrame
        returns True if models are equivalent when detailed_comparison=True
        else returns DataFrame containing comparison details.
    """

    df = pd.DataFrame(columns=["model 0", "model 1"])
    so1 = []  # for storing series_original
    sv1 = []  # for storing series_validated
    ss1 = []  # for storing series

    for i, ml in enumerate([ml1, ml2]):

        counter = 0  # for counting stress timeseries
        df.loc["name:", f"model {i}"] = ml.name

        for k in ml.settings.keys():
            df.loc[f"- settings: {k}", f"model {i}"] = ml.settings.get(k)

        if i == 0:
            oso = ml.oseries.series_original
            osv = ml.oseries.series_validated
            oss = ml.oseries.series
            df.loc["oseries: series_original", f"model {i}"] = True
            df.loc["oseries: series_validated", f"model {i}"] = True
            df.loc["oseries: series_series", f"model {i}"] = True
        elif i == 1:
            try:
                compare_oso = oso.equals(ml.oseries.series_original)
            except ValueError:
                # series are not identical in length or index does not match
                compare_oso = False
            try:
                compare_osv = osv.equals(ml.oseries.series_validated)
            except ValueError:
                # series are not identical in length or index does not match
                compare_osv = False
            try:
                compare_oss = oss.equals(ml.oseries.series)
            except ValueError:
                # series are not identical in length or index does not match
                compare_oss = False

            df.loc["oseries: series_original", f"model {i}"] = compare_oso
            df.loc["oseries: series_validated", f"model {i}"] = compare_osv
            df.loc["oseries: series_series", f"model {i}"] = compare_oss

        for sm_name, sm in ml.stressmodels.items():

            df.loc[f"stressmodel: '{sm_name}'"] = sm_name
            df.loc["- rfunc"] = (sm.rfunc._name if sm.rfunc is not None
                                 else "NA")

            if sm._name == "RechargeModel":
                stresses = [sm.prec, sm.evap]
            else:
                stresses = sm.stress

            for ts in stresses:
                df.loc[f"- timeseries: '{ts.name}'"] = ts.name
                for tsk in ts.settings.keys():
                    df.loc[f"  - {ts.name} settings: {tsk}", f"model {i}"] = \
                        ts.settings[tsk]

                if i == 0:
                    so1.append(ts.series_original.copy())
                    sv1.append(ts.series_validated.copy())
                    ss1.append(ts.series.copy())
                    df.loc[f"  - {ts.name}: series_original"] = True
                    df.loc[f"  - {ts.name}: series_validated"] = True
                    df.loc[f"  - {ts.name}: series"] = True

                elif i == 1:
                    # ValueError if series cannot be compared,
                    # set result to False
                    try:
                        compare_so1 = so1[counter].equals(ts.series_original)
                    except ValueError:
                        compare_so1 = False
                    try:
                        compare_sv1 = sv1[counter].equals(ts.series_validated)
                    except ValueError:
                        compare_sv1 = False
                    try:
                        compare_ss1 = ss1[counter].equals(ts.series)
                    except ValueError:
                        compare_ss1 = False
                    df.loc[f"  - {ts.name}: series_original"] = compare_so1
                    df.loc[f"  - {ts.name}: series_validated"] = compare_sv1
                    df.loc[f"  - {ts.name}: series"] = compare_ss1

                counter += 1

        for p in ml.parameters.index:
            df.loc[f"param: {p} (init)", f"model {i}"] = \
                ml.parameters.loc[p, "initial"]
            df.loc[f"param: {p} (opt)", f"model {i}"] = \
                ml.parameters.loc[p, "optimal"]

        if stats:
            stats_df = ml.stats.summary(stats=stats)
            for s in stats:
                df.loc[f"stats: {s}", f"model {i}"] = stats_df.loc[s, "Value"]

    # compare
    df["comparison"] = df.iloc[:, 0] == df.iloc[:, 1]

    # isclose for params
    param_mask = df.index.str.startswith("param: ")
    df.loc[param_mask, "comparison"] = np.isclose(
        df.loc[param_mask, "model 0"].astype(float).values,
        df.loc[param_mask, "model 1"].astype(float).values)

    # ensure NaN == NaN is not counted as a difference
    nanmask = df.iloc[:, 0].isna() & df.iloc[:, 1].isna()
    df.loc[nanmask, "comparison"] = True

    # for stats comparison must be almost_equal
    if stats:
        stats_idx = [f"stats: {s}" for s in stats]
        b = np.isclose(df.loc[stats_idx, "model 0"].astype(float).values,
                       df.loc[stats_idx, "model 1"].astype(float).values)
        df.loc[stats_idx, "comparison"] = b

    if detailed_comparison:
        return df
    else:
        return df["comparison"].iloc[1:].all()  # ignore name difference


def copy_database(conn1, conn2, libraries: Optional[List[str]] = None,
                  overwrite: bool = False, progressbar: bool = False) -> None:
    """Copy libraries from one database to another.

    Parameters
    ----------
    conn1 : pastastore.*Connector
        source Connector containing link to current database containing data
    conn2 : pastastore.*Connector
        destination Connector with link to database to which you want to copy
    libraries : Optional[List[str]], optional
        list of str containing names of libraries to copy, by default None,
        which copies all libraries: ['oseries', 'stresses', 'models']
    overwrite : bool, optional
        overwrite data in destination database, by default False
    progressbar : bool, optional
        show progressbars, by default False

    Raises
    ------
    ValueError
        if library name is not understood
    """
    if libraries is None:
        libraries = ["oseries", "stresses", "models"]

    for lib in libraries:
        if lib == "oseries":
            for name in (tqdm(conn1.oseries_names, desc="copying oseries") if
                         progressbar else conn1.oseries_names):
                o, meta = conn1.get_oseries(name, return_metadata=True)
                conn2.add_oseries(o, name, metadata=meta, overwrite=overwrite)
        elif lib == "stresses":
            for name in (tqdm(conn1.stresses_names, desc="copying stresses") if
                         progressbar else conn1.stresses_names):
                s, meta = conn1.get_stresses(name, return_metadata=True)
                conn2.add_stress(s, name, kind=meta["kind"], metadata=meta,
                                 overwrite=overwrite)
        elif lib == "models":
            for name in (tqdm(conn1.model_names, desc="copying models") if
                         progressbar else conn1.model_names):
                mldict = conn1.get_models(name, return_dict=True)
                conn2.add_model(mldict, overwrite=overwrite)
        else:
            raise ValueError(f"Library name '{lib}' not recognized!")
