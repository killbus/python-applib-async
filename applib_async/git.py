from typing import Set
from .subprocess import read_and_display

async def get_first_commit_hash(cwd: str) -> str:
    """..."""

    cmd = ['git', 'rev-list', '--max-parents=0', 'HEAD']
    _, stdout, _ = await read_and_display(cmd, cwd=cwd)
    hash: str = stdout.decode().strip()

    return hash

async def get_changed_files_between_commits(cwd: str, before_commit: str, after_comit='HEAD', location: str = None) -> Set[str]:
    """Get changed files between commits without duplicates
    
    example: 
        >>> git log --format=''  --name-only 526b944024cd363a0748f2df33702dde748d8fae..HEAD pages/miui/updates/ | sort -u
    """
    cmd = ['git', 'log', '--format=', '--name-only', f'{before_commit}..{after_comit}']
    if location:
        cmd.append(location)

    _, stdout, _ = await read_and_display(cmd, cwd=cwd)
    if stdout:
        files = stdout.decode().strip().split('\n')
        return set(files)

    return set([])
