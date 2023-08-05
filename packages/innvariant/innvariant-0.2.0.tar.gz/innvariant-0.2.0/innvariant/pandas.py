import glob
import hashlib
import json
import marshal
import os
import pickle
import shutil
import time
import uuid
import warnings

import pandas as pd


PICKLE_BYTES_MAX = 2**31 - 1
PICKLE_PROTOCOL = 5


def pickle_write(data, path_file, pickle_bytes_max: int = PICKLE_BYTES_MAX):
    bytes_data = pickle.dumps(data, protocol=PICKLE_PROTOCOL)
    with open(path_file, "wb") as handle_file:
        for idx in range(0, len(bytes_data), pickle_bytes_max):
            handle_file.write(bytes_data[idx : idx + pickle_bytes_max])


def pickle_load(path_file, pickle_bytes_max: int = PICKLE_BYTES_MAX):
    try:
        with open(path_file, "rb") as h:
            return pickle.load(h)
    except Exception:  # noqa, pylint: disable=broad-except
        bytes_in = bytearray(0)
        input_size = os.path.getsize(path_file)
        with open(path_file, "rb") as handle:
            for _ in range(0, input_size, pickle_bytes_max):
                bytes_in += handle.read(pickle_bytes_max)
        return pickle.loads(bytes_in)


class CacheNotFound(Exception):
    pass


class CodeChanged(Exception):
    pass


class ParametersChanged(Exception):
    pass


class CacheManager(object):
    def __init__(self, path_base):
        self._path_base = os.path.expanduser(path_base)
        self._name_cache_meta = "cachemeta-0.1.0.hd5"
        self._key_cachemanager = "cachemanager"

    def _ensure_base_path(self):
        if not os.path.exists(self._path_base):
            try:
                os.makedirs(self._path_base)
            except Exception:
                warnings.warn(
                    f"Could not create base path '{self._path_base}' for cache manager."
                )

    def _load_meta(self) -> pd.DataFrame:
        self._ensure_base_path()
        path_meta = os.path.join(self._path_base, self._name_cache_meta)
        if not os.path.exists(path_meta):
            self.clear_meta()
        return pd.read_hdf(path_meta, key=self._key_cachemanager)

    def clear(self, key: str):
        self._ensure_base_path()

        cache_meta = self._load_meta()
        path_meta = os.path.join(self._path_base, self._name_cache_meta)
        ixs_hit = cache_meta["key"] == key
        cache_meta.drop(cache_meta[ixs_hit].index)
        cache_meta.to_hdf(path_meta, key=self._key_cachemanager)

        files = glob.glob(self._path_base + os.path.sep + f"cache-{key}-*.pickle")
        for path_file in files:
            try:
                os.remove(path_file)
            except FileNotFoundError:
                print(f"Error while deleting cache file <{path_file}>")

    def clear_meta(self):
        self._ensure_base_path()
        path_meta = os.path.join(self._path_base, self._name_cache_meta)
        meta = pd.DataFrame.from_dict(
            {
                "key": [],
                "time_create_cache": [],
                "used_hash": [],
                "hash_code": [],
                "hash_args": [],
                "hash_kwargs": [],
                "file_cache": [],
            }
        )
        meta.to_hdf(path_meta, key=self._key_cachemanager)

    def clear_all(self):
        self._ensure_base_path()
        files = glob.glob(self._path_base + os.path.sep + "cache*")
        for path_file in files:
            try:
                os.remove(path_file)
            except FileNotFoundError:
                print(f"Error while deleting cache file <{path_file}>")

        if len(os.listdir(self._path_base)) == 0:
            os.removedirs(self._path_base)

    def _add_meta(self, key, hash_code, hash_args, hash_kwargs, name_cache):
        meta = pd.DataFrame.from_dict(
            {
                "key": [key],
                "time_create_cache": [time.time()],
                "used_hash": ["sha256"],
                "hash_code": [hash_code],
                "hash_args": [hash_args],
                "hash_kwargs": [hash_kwargs],
                "file_cache": [name_cache],
            }
        )
        all_meta = self._load_meta()
        new_meta = pd.concat([all_meta, meta], ignore_index=True)
        path_meta = os.path.join(self._path_base, self._name_cache_meta)
        new_meta.to_hdf(path_meta, key=self._key_cachemanager)

    def contains(self, key: str):
        cache_meta = self._load_meta()
        return any(cache_meta["key"] == key)

    def hit(self, key: str, func: callable, args: list = None, kwargs: dict = None):
        cache_meta = self._load_meta()

        if not any(cache_meta["key"] == key):
            raise CacheNotFound(f"No cache exists for key <{key}>.")

        hash_code_req = hashlib.sha256(marshal.dumps(func.__code__)).hexdigest()
        if not any(
            (cache_meta["key"] == key) & (cache_meta["hash_code"] == hash_code_req)
        ):
            raise CodeChanged(
                f"Code signature for function <{func.__name__}> and key <{key}> changed."
            )

        hash_args_req = hashlib.sha256(marshal.dumps(args)).hexdigest()
        hash_kwargs_req = hashlib.sha256(marshal.dumps(kwargs)).hexdigest()
        ixs_hit = (
            (cache_meta["key"] == key)
            & (cache_meta["hash_code"] == hash_code_req)
            & (cache_meta["hash_args"] == hash_args_req)
            & (cache_meta["hash_kwargs"] == hash_kwargs_req)
        )
        if not any(ixs_hit):
            raise ParametersChanged(
                f"Parameters for calling <{func.__name__}> with key <{key}> changed."
            )

        file_cache = (
            cache_meta[ixs_hit]
            .sort_values("time_create_cache", ascending=False)["file_cache"]
            .values[0]
        )
        path_cache = os.path.join(self._path_base, file_cache)
        return pickle_load(path_cache)

    def store(
        self, result, key: str, func: callable, args: list = None, kwargs: dict = None
    ):
        name_cache = f"cache-{key}-{str(uuid.uuid4())}.pickle"
        hash_code = hashlib.sha256(marshal.dumps(func.__code__)).hexdigest()
        hash_args = hashlib.sha256(marshal.dumps(args)).hexdigest()
        hash_kwargs = hashlib.sha256(marshal.dumps(kwargs)).hexdigest()

        path_cache = os.path.join(self._path_base, name_cache)
        assert not os.path.exists(
            path_cache
        ), "Cache file to store result in already exists"
        pickle_write(result, path_cache)
        assert os.path.exists(path_cache), "Could not write cache file"

        self._add_meta(key, hash_code, hash_args, hash_kwargs, name_cache)


def cache(key: str, *args, **kwargs):
    path_base_cache = str(kwargs["base"]) if "base" in kwargs else ".cache/"

    def cache_decorator(func):
        cm = CacheManager(path_base=path_base_cache)

        def wrapper(*args, **kwargs):
            force_calc = bool(kwargs["force_calc"]) if "force_calc" in kwargs else False
            clear_cache = (
                bool(kwargs["clear_cache"]) if "clear_cache" in kwargs else False
            )

            if force_calc:
                res = func(*args, **kwargs)
                cm.store(res, key, func, args, kwargs)
            else:
                try:
                    res = cm.hit(key, func, args, kwargs)
                except (CacheNotFound, CodeChanged, ParametersChanged):
                    res = func(*args, **kwargs)
                    cm.store(res, key, func, args, kwargs)

            if clear_cache:
                cm.clear(key)
            return res

        wrapper._cachemanager = cm
        return wrapper

    return cache_decorator


def get_cachemanager_for(func) -> CacheManager:
    if not hasattr(func, "_cachemanager"):
        raise ValueError(
            f"Function {func} was not decorated by cache() to obtain its cachemanager."
        )
    return func._cachemanager


def calculate_or_cache(
    fn_calculate,
    force_calc=False,
    clear_cache=False,
    path_base_cache="~/.cache/analysisnotebook/",
):
    assert callable(fn_calculate)
    name_calculation = fn_calculate.__name__
    name_cache_meta = "cache-meta.json"
    bytes_calculation = marshal.dumps(fn_calculate.__code__)
    m = hashlib.sha256()
    m.update(bytes_calculation)
    code_calculation = m.hexdigest()

    res = None

    path_base_cache = os.path.join(
        os.path.expanduser(path_base_cache), name_calculation
    )
    path_meta = os.path.join(path_base_cache, name_cache_meta)
    if not os.path.exists(path_base_cache):
        os.makedirs(path_base_cache)
    elif not force_calc and os.path.exists(path_meta):
        meta_full = None
        with open(path_meta) as handle_meta:
            meta_full = json.load(handle_meta)

        meta = None
        if "caches" in meta_full:
            for cache in meta_full["caches"]:
                if cache["code_calculation"] == code_calculation:
                    meta = cache

        if meta is not None and "format" in meta and "keys" in meta:
            print(f"Cache hit for {name_calculation}")
            path_hd5 = os.path.join(path_base_cache, meta["path"])
            if meta["format"] == "single":
                res = pd.read_hdf(path_hd5, key=meta["keys"])
            elif meta["format"] == "list":
                res = [pd.read_hdf(path_hd5, key=k) for k in meta["keys"]]
            elif meta["format"] == "dict":
                res = {
                    meta["keys"][k_hash]: pd.read_hdf(path_hd5, key=k_hash)
                    for k_hash in meta["keys"]
                }

    if clear_cache:
        shutil.rmtree(path_base_cache)

    if res is None:
        # (Re-)calculate result
        time_calc_start = time.time()
        res = fn_calculate()
        time_calc_end = time.time()

        if clear_cache:
            return res

        format_res = (
            "single"
            if isinstance(res, pd.DataFrame)
            else "list"
            if type(res) == list
            else "dict"
            if type(res) == dict
            else "unknown"
        )

        # "main" if format_res == "single" else [i for i in enumerate(res)] if format_res == "list" else [k for k in res.keys()] if format_res == "dict" else None
        name_hd5 = "result_cache.hd5"
        path_hd5 = os.path.join(path_base_cache, name_hd5)
        res_keys = None
        if format_res == "single":
            res_keys = "main"
            res.to_hdf(path_hd5, key=res_keys)
        elif format_res == "list":
            res_keys = [i for i in enumerate(res)]
            for k, df in zip(res_keys, res):
                df.to_hdf(path_hd5, key=k)
        elif format_res == "dict":
            res_keys = {
                "key" + hashlib.sha256(str.encode(k)).hexdigest(): k for k in res.keys()
            }
            for k_hash in res_keys:
                k = res_keys[k_hash]
                res[k].to_hdf(path_hd5, key=k_hash)

        # Store cache
        meta_info = {
            "version": 1.0,
            "code_calculation": code_calculation,
            "timings": {
                "cache_creation": time.time(),
                "calc_start": time_calc_start,
                "calc_end": time_calc_end,
            },
            "format": format_res,
            "path": name_hd5,
            "keys": res_keys,
        }

        meta = {}
        if os.path.exists(path_meta):
            with open(path_meta) as handle_meta:
                meta = json.load(handle_meta)
        if "caches" not in meta:
            meta["caches"] = []
        meta["caches"].append(meta_info)
        with open(path_meta, "w+") as handle_write_meta:
            json.dump(meta, handle_write_meta)

    return res
