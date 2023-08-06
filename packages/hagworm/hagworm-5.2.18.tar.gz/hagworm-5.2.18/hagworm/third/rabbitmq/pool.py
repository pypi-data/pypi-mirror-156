# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import aio_pika

from ...extend.asyncio.task import IntervalTask


class RabbitMQPool:
    """RabbitMQPool连接池
    """

    def __init__(self, url, **kwargs):

        self._mq_url = url
        self._mq_setting = kwargs

        self._queue_name = None
        self._consume_func = None
        self._consume_qos = None

        self._connection_pool = None
        self._channel_pool = None

        self._task = IntervalTask.create(10, self._consume_message)

    async def open(self, queue_name, consume_func, consume_qos=10, pool_size=10):

        self._queue_name = queue_name
        self._consume_func = consume_func
        self._consume_qos = consume_qos

        self._connection_pool = aio_pika.pool.Pool(self._get_connection, max_size=pool_size)
        self._channel_pool = aio_pika.pool.Pool(self._get_channel, max_size=pool_size)

        self._task.start()

    async def close(self):

        self._task.stop()

        await self._channel_pool.close()
        await self._connection_pool.close()

    async def _get_connection(self):

        return await aio_pika.connect_robust(self._mq_url, **self._mq_setting)

    async def _get_channel(self):

        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    async def _consume_message(self):

        async with self._channel_pool.acquire() as channel:

            await channel.set_qos(self._consume_qos)

            queue = await channel.declare_queue(self._queue_name)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self._consume_func(message)
                    await message.ack()

    async def publish(self, message):

        async with self._channel_pool.acquire() as channel:
            await channel.default_exchange.publish(aio_pika.Message(message), self._queue_name)

    async def batch_publish(self, messages):

        async with self._channel_pool.acquire() as channel:
            for message in messages:
                await channel.default_exchange.publish(aio_pika.Message(message), self._queue_name)
