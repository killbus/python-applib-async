import asyncio
from dataclasses import dataclass
from typing import Dict, Union
from concurrent.futures import ThreadPoolExecutor
import json
import leancloud

from .policy_async import policy_async as _policy_async
from .requests_adapters import TimeoutHTTPAdapter
from .tools import pcformat
from .logu import logger
info, debug, warn, error = logger.info, logger.debug, logger.warning, logger.error

@dataclass
class LeancloudConfig:
    """..."""
    app_id: str
    app_key: str
    app_objectid: str

class LeancloudConfigStorage(object):

    def __init__(self, conf: LeancloudConfig):
        self.loop = asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.conf = conf

        leancloud.client.session.mount('http://', TimeoutHTTPAdapter(timeout=30)) # 10 seconds
        leancloud.client.session.mount('https://', TimeoutHTTPAdapter(timeout=30))

        leancloud.init(self.conf.app_id, self.conf.app_key)
        self.object = leancloud.Object.extend('Config')
        self.query = self.object.query
        self.object_config = self.query.get(self.conf.app_objectid)


    async def get_config(self) -> Union[Dict, None]:
        config = await self.policy_async(self.object_config.get, 'config')
        if config:
            try:
                config = json.loads(config)
                return config
            except Exception:
                logger.opt(exception=True).error('[Leancloud] Failed to load config.')

        return None

    async def fetch(self) -> None:
        await self.policy_async(self.object_config.fetch)
    

    async def policy_async(self, *args, **kwargs) -> None:
        return await _policy_async(self.loop, *args, executor=self.executor, **kwargs)


    async def show_config(self) -> None:
        info(pcformat(await self.get_config()))

if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    try:
        lcs = LeancloudConfigStorage()
        loop.run_until_complete(lcs.show_config())
    except KeyboardInterrupt:
        info('cancel on KeyboardInterrupt..')
#-#        task.cancel()
        loop.run_forever()
#-#        task.exception()
    finally:
        loop.stop()