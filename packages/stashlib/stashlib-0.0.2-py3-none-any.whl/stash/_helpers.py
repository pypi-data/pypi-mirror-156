from stash.codecs.passthru import PassthruCodec
from stash.manager import StashManager
from stash.options import StashOptions


def _init_cache(storage, codec, options: StashOptions) -> StashManager:
    cache_man = StashManager(storage=storage, codec=codec, options=options)
    return cache_man


def _init_fs_cache(codec, options: StashOptions) -> StashManager:
    from .storages.filesystem import FilesystemStorage

    return _init_cache(
        storage=FilesystemStorage(options=options), codec=codec, options=options
    )


def get_fs_zl_stash(options: StashOptions) -> StashManager:
    from .codecs.zlib import ZlibCodec

    return _init_fs_cache(ZlibCodec(), options=options)


def get_fs_br_stash(options: StashOptions) -> StashManager:
    from .codecs.brotli import BrotliCodec

    return _init_fs_cache(BrotliCodec(), options=options)


def get_fs_zs_stash(options: StashOptions) -> StashManager:
    from .codecs.zstd import ZstdCodec

    return _init_fs_cache(ZstdCodec(), options=options)


def get_mongo_zl_stash(options: StashOptions) -> StashManager:
    from .codecs.zlib import ZlibCodec
    from .storages.mongodb import MongoDbStorage

    storage = MongoDbStorage(options=options)
    return _init_cache(storage, ZlibCodec(), options=options)


def get_lmdb_zl_stash(options: StashOptions) -> StashManager:
    from .codecs.zlib import ZlibCodec
    from .storages.lm_db import LmdbStorage

    storage = LmdbStorage(options=options)
    return _init_cache(storage, ZlibCodec(), options=options)


def get_lmdb_zs_stash(options: StashOptions) -> StashManager:
    from .codecs.zstd import ZstdCodec
    from .storages.lm_db import LmdbStorage

    storage = LmdbStorage(options=options)
    return _init_cache(storage, ZstdCodec(), options=options)


def get_fs_stash(options: StashOptions) -> StashManager:
    return _init_fs_cache(codec=None, options=options)


def get_null_stash() -> StashManager:
    from .storages.null import NullStorage

    options = StashOptions()
    return _init_cache(
        storage=NullStorage(options=options), codec=PassthruCodec(), options=options
    )
