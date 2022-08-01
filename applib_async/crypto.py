import sys
import asyncio
from asyncio import BaseEventLoop
from asyncio.subprocess import PIPE
import subprocess
from typing import List, Union, Tuple, IO
import re
from zlib import crc32
from hashlib import md5, sha1, sha256

from numpy import Infinity

from .platform import IS_LINUX, IS_MACOS
from .policy_async import policy_async

    
def _md5_cmd(localpath: str) -> List[str]:
    if IS_MACOS:
        cmd = ["md5", localpath]
    elif IS_LINUX:
        cmd = ["md5sum", localpath]
    else:  # windows
        cmd = ["CertUtil", "-hashfile", localpath, "MD5"]
    return cmd


async def calu_file_md5(localpath: str) -> str:
    cp = await asyncio.create_subprocess_exec(
        *_md5_cmd(localpath), universal_newlines=False, stdout=PIPE, stderr=PIPE
    )

    stdout, _ = await cp.communicate()

    output = stdout.decode().strip()
    if IS_MACOS:
        return re.split(r"\s+", output)[-1]
    elif IS_LINUX:
        return re.split(r"\s+", output)[0]
    else:  # windows
        cn = output.split("CertUtil")[0].strip()
        cn = cn.split(":")[-1].strip().replace(" ", "")
        return cn


def _calu_md5(buf: Union[str, bytes], encoding="utf-8") -> str:
    assert isinstance(buf, (str, bytes))

    if isinstance(buf, str):
        buf = buf.encode(encoding)
    return md5(buf).hexdigest()

async def calu_md5(buf: Union[str, bytes], encoding="utf-8", loop: BaseEventLoop = None) -> str:
    """..."""
    return await policy_async(_calu_md5, buf, encoding, loop=loop)

def calu_crc32_and_md5(stream: IO, chunk_size: int) -> Tuple[int, str]:
    md5_v = md5()
    crc32_v = 0
    while True:
        buf = stream.read(chunk_size)
        if buf:
            md5_v.update(buf)
            crc32_v = crc32(buf, crc32_v).conjugate()
        else:
            break
    return crc32_v.conjugate() & 0xFFFFFFFF, md5_v.hexdigest()

def _sha1_cmd(localpath: str) -> List[str]:
    if IS_MACOS:
        cmd = ["shasum", localpath]
    elif IS_LINUX:
        cmd = ["sha1sum", localpath]
    else:  # windows
        cmd = ["CertUtil", "-hashfile", localpath, "SHA1"]
    return cmd

def _sha256_cmd(localpath: str) -> List[str]:
    if IS_MACOS:
        cmd = ["sha256sum", localpath]
    elif IS_LINUX:
        cmd = ["sha256sum", localpath]
    else:  # windows
        cmd = ["CertUtil", "-hashfile", localpath, "SHA256"]
    return cmd

async def _calu_file_sha(localpath: str, sha_type: str = "sha1") -> str:
    """..."""
    _sha_cmd = _sha1_cmd if sha_type == "sha1" else _sha256_cmd
    cp = await asyncio.create_subprocess_exec(
            *_sha_cmd(localpath), universal_newlines=False, stdout=PIPE, stderr=PIPE
        )

    stdout, _ = await cp.communicate()
    output = stdout.decode().strip()
    if IS_MACOS:
        return re.split(r"\s+", output)[-1]
    elif IS_LINUX:
        return re.split(r"\s+", output)[0]
    else:  # windows
        cn = output.split("CertUtil")[0].strip()
        cn = cn.split(":")[-1].strip().replace(" ", "")
        return cn

def _calu_sha(buf: Union[str, bytes], encoding="utf-8", sha_type: str = "sha1") -> str:
    assert isinstance(buf, (str, bytes))

    if isinstance(buf, str):
        buf = buf.encode(encoding)

    if sha_type == "sha1":
        return sha1(buf).hexdigest()
    elif sha_type == "sha256":
        return sha256(buf).hexdigest()
    else:
        raise ValueError("sha_type must be sha1 or sha256")

async def calu_file_sha1(localpath: str) -> str:
    """..."""
    return await _calu_file_sha(localpath, sha_type="sha1")

def _calu_sha1(buf: Union[str, bytes], encoding="utf-8") -> str:
    return _calu_sha(buf, encoding, sha_type="sha1")

async def calu_sha1(buf: Union[str, bytes], encoding="utf-8", loop: BaseEventLoop = None) -> str:
    """..."""
    return await policy_async(_calu_sha1, buf, encoding, loop=loop)

async def calu_file_sha256(localpath: str) -> str:
    """..."""
    return await _calu_file_sha(localpath, sha_type="sha256")

def _calu_sha256(buf: Union[str, bytes], encoding="utf-8") -> str:
    return _calu_sha(buf, encoding, sha_type="sha256")

async def calu_sha256(buf: Union[str, bytes], encoding="utf-8", loop: BaseEventLoop = None) -> str:
    """..."""
    return await policy_async(_calu_sha256, buf, encoding, loop=loop)

async def test_infinity_loop():
    while True:
        print(1)
        await asyncio.sleep(0.5)

async def test_main():
    """..."""
    # dd if=/dev/zero of=/tmp/test.img bs=1024 count=0 seek=$[1024*1000]
    result = await calu_file_md5('/tmp/test.img')
    print(result)

if __name__ == '__main__':
    """..."""
    try:
        loop = asyncio.get_event_loop()
        # task = asyncio.ensure_future(calu_sha1(b'a'))
        task = asyncio.gather(
            test_infinity_loop(),
            test_main()
        )
        loop.run_until_complete(task)

    except KeyboardInterrupt:
        print('cancel on KeyboardInterrupt..')
        task.cancel()
        loop.run_forever()
        task.exception()
    finally:
        loop.stop()
