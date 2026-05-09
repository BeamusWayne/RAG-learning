#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Milvus MVP-05: 企业级特性
==========================
目标：添加企业级系统必备的可靠性特性
在MVP-04批量处理基础上新增：

新增内容：
- 重试机制（Retry with Exponential Backoff）
- 熔断器（Circuit Breaker）
- 结果缓存（Result Cache）
- 限流器（Rate Limiter）
- 健康检查（Health Check）
- 优雅关闭（Graceful Shutdown）

为什么需要这些特性：
- 重试机制：网络瞬时故障时自动恢复
- 熔断器：防止级联故障，快速失败
- 缓存：减少重复查询，提升响应速度
- 限流：保护系统不被过载

知识点：
- 指数退避重试：每次重试等待时间翻倍
- 熔断器三状态：CLOSED（正常）、OPEN（熔断）、HALF_OPEN（试探）
- LRU缓存：最近最少使用淘汰策略
"""

import asyncio
import numpy as np
import time
import hashlib
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType

# ============================================================
# 第一步：熔断器实现
# ============================================================
class CircuitState(Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"      # 关闭状态：正常请求
    OPEN = "open"          # 打开状态：快速失败
    HALF_OPEN = "half_open" # 半开状态：试探恢复

class CircuitBreaker:
    """
    熔断器实现
    原理：当失败率超过阈值时，打开熔断器，快速返回错误；
          一段时间后，尝试放行一个请求进行试探（半开状态）；
          如果成功则关闭熔断器，失败则继续打开
    """

    def __init__(
        self,
        failure_threshold: int = 5,      # 触发熔断的连续失败次数
        recovery_timeout: float = 30.0,   # 熔断后等待多少秒开始试探
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._success_count = 0
        self._half_open_max_success = 3  # 半开状态下连续成功次数达到这个值则关闭

    @property
    def state(self) -> CircuitState:
        """获取当前熔断器状态"""
        if self._state == CircuitState.OPEN:
            # 检查是否应该进入半开状态
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
        return self._state

    async def call(self, func, *args, **kwargs):
        """
        通过熔断器执行函数
        如果熔断器打开，直接抛出异常
        """
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("熔断器已打开，拒绝请求")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """记录成功"""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._half_open_max_success:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                print("[OK] 熔断器已关闭，系统恢复正常")
        else:
            self._failure_count = 0

    def _on_failure(self):
        """记录失败"""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            print("[警告] 熔断器重新打开")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            print(f"[警告] 熔断器已打开 (连续失败 {self._failure_count} 次)")

class CircuitBreakerOpenError(Exception):
    """熔断器打开时抛出的异常"""
    pass

# ============================================================
# 第二步：LRU缓存实现
# ============================================================
class LRUCache:
    """
    LRU（最近最少使用）缓存
    当缓存满时，自动淘汰最久未使用的条目
    """

    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        """
        参数:
            max_size: 缓存最大条目数
            ttl: 缓存条目存活时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}

    def _make_key(self, query_vector: List[float], top_k: int) -> str:
        """生成缓存键"""
        # 将向量转换为字符串并取哈希
        vec_str = ",".join([f"{v:.6f}" for v in query_vector[:10]])  # 只用前10维
        return f"{vec_str}:{top_k}"

    def get(self, query_vector: List[float], top_k: int) -> Optional[List[Dict]]:
        """获取缓存结果"""
        key = self._make_key(query_vector, top_k)

        if key not in self._cache:
            return None

        # 检查是否过期
        if time.time() - self._timestamps[key] > self.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None

        # 移到末尾（表示最近使用）
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, query_vector: List[float], top_k: int, results: List[Dict]):
        """存入缓存"""
        key = self._make_key(query_vector, top_k)

        # 如果已存在，先删除
        if key in self._cache:
            del self._cache[key]

        # 添加到末尾
        self._cache[key] = results
        self._timestamps[key] = time.time()

        # 如果超过最大容量，淘汰最久未使用的
        if len(self._cache) > self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]

    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._timestamps.clear()

    def stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size
        }

# ============================================================
# 第三步：限流器实现
# ============================================================
class RateLimiter:
    """
    令牌桶限流器
    原理：系统以固定速率往桶里放令牌，请求需要获取令牌才能执行
    """

    def __init__(self, rate: float = 100, capacity: int = 200):
        """
        参数:
            rate: 每秒产生的令牌数
            capacity: 桶的容量
        """
        self.rate = rate
        self.capacity = capacity
        self._tokens = float(capacity)
        self._last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """获取令牌，如果不够则等待"""
        async with self._lock:
            while True:
                now = time.time()
                # 补充令牌
                elapsed = now - self._last_update
                self._tokens = min(
                    self.capacity,
                    self._tokens + elapsed * self.rate
                )
                self._last_update = now

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return

                # 等待下一批令牌
                wait_time = (tokens - self._tokens) / self.rate
                await asyncio.sleep(wait_time)

# ============================================================
# 第四步：带重试的Milvus客户端
# ============================================================
class RetryMilvusClient:
    """
    带重试机制的Milvus客户端
    使用指数退避策略：每次重试的等待时间翻倍
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0
    ):
        """
        参数:
            max_retries: 最大重试次数
            base_delay: 基础延迟（秒）
            max_delay: 最大延迟（秒）
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute_with_retry(self, func, *args, **kwargs):
        """
        执行函数，失败时自动重试
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    # 计算退避时间
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    print(f"    请求失败，{delay:.1f}秒后重试 ({attempt + 1}/{self.max_retries})")
                    await asyncio.sleep(delay)
                else:
                    print(f"    重试次数用尽，最后一次错误: {e}")

        raise last_exception

# ============================================================
# 第五步：企业级RAG系统
# ============================================================
class EnterpriseRAG:
    """
    企业级RAG系统，整合所有可靠性特性
    """

    def __init__(
        self,
        collection_name: str = "enterprise_rag",
        dim: int = 768
    ):
        self.collection_name = collection_name
        self.dim = dim
        self.collection = None

        # 初始化各组件
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30.0
        )
        self.cache = LRUCache(max_size=1000, ttl=300.0)
        self.rate_limiter = RateLimiter(rate=50, capacity=100)
        self.retry_client = RetryMilvusClient(
            max_retries=3,
            base_delay=1.0
        )

    async def connect(self):
        """连接到Milvus"""
        await self.retry_client.execute_with_retry(
            lambda: connections.connect(
                alias="default",
                host="localhost",
                port="19530"
            )
        )
        print("[OK] 已连接到 Milvus")

    async def search_with_all_features(
        self,
        query_vector: List[float],
        top_k: int = 5
    ) -> List[Dict]:
        """
        完整的搜索流程，包含所有企业级特性：
        1. 限流
        2. 缓存
        3. 熔断
        4. 重试
        """
        # 1. 限流
        await self.rate_limiter.acquire()

        # 2. 检查缓存
        cached_result = self.cache.get(query_vector, top_k)
        if cached_result is not None:
            print("[OK] 从缓存返回结果")
            return cached_result

        # 3. 通过熔断器和重试执行搜索
        async def _search():
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.collection.load)

            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }

            def _do_search():
                return self.collection.search(
                    data=[query_vector],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    output_fields=["chunk_id", "content"]
                )

            return await loop.run_in_executor(None, _do_search)

        try:
            results = await self.circuit_breaker.call(_search)

            # 4. 格式化结果
            hits = []
            for hit in results[0]:
                hits.append({
                    "id": hit.id,
                    "chunk_id": hit.entity.get("chunk_id"),
                    "content": hit.entity.get("content"),
                    "score": hit.distance
                })

            # 5. 存入缓存
            self.cache.put(query_vector, top_k, hits)

            return hits

        except CircuitBreakerOpenError:
            print("[警告] 服务熔断中，返回空结果")
            return []

    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        返回系统各组件的健康状态
        """
        health = {
            "milvus": "unknown",
            "circuit_breaker": self.circuit_breaker.state.value,
            "cache": self.cache.stats(),
            "timestamp": time.time()
        }

        try:
            # 检查Milvus连接
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: connections.connect(alias="health_check", host="localhost", port="19530")
            )
            connections.disconnect(alias="health_check")
            health["milvus"] = "healthy"
        except Exception as e:
            health["milvus"] = f"unhealthy: {str(e)}"

        return health

    async def graceful_shutdown(self):
        """
        优雅关闭
        确保所有操作完成后关闭连接
        """
        print("[OK] 开始优雅关闭...")

        # 清空缓存
        self.cache.clear()
        print("[OK] 缓存已清空")

        # 关闭Milvus连接
        connections.disconnect(alias="default")
        print("[OK] Milvus连接已关闭")

# ============================================================
# 第六步：演示企业级特性
# ============================================================
async def demo_enterprise_features():
    """演示企业级RAG系统的各项特性"""
    rag = EnterpriseRAG()

    # 1. 连接
    await rag.connect()

    # 2. 模拟创建collection和插入数据（省略详细代码）
    print("\n" + "="*60)
    print("企业级特性演示")
    print("="*60)

    # 3. 演示缓存效果
    print("\n[演示] 缓存效果:")
    query_vector = np.random.rand(768).astype(np.float32).tolist()

    print("  第一次搜索（无缓存）...")
    start = time.time()
    await rag.search_with_all_features(query_vector, top_k=3)
    print(f"    耗时: {time.time() - start:.4f}秒")

    print("  第二次搜索（应有缓存）...")
    start = time.time()
    await rag.search_with_all_features(query_vector, top_k=3)
    print(f"    耗时: {time.time() - start:.4f}秒")

    # 4. 演示限流
    print("\n[演示] 限流效果:")
    print("  连续发送5个请求...")
    start = time.time()
    for i in range(5):
        await rag.search_with_all_features(query_vector, top_k=3)
        print(f"    请求 {i+1} 完成")
    print(f"  总耗时: {time.time() - start:.2f}秒")

    # 5. 健康检查
    print("\n[演示] 健康检查:")
    health = await rag.health_check()
    for key, value in health.items():
        print(f"  {key}: {value}")

    # 6. 优雅关闭
    await rag.graceful_shutdown()

# ============================================================
# 主函数
# ============================================================
async def main():
    """主函数"""
    try:
        await demo_enterprise_features()

        print("\n[MVP-05 完成] 你已学会企业级RAG特性！")
        print("下一步建议：学习生产级高性能架构 (milvus_mvp_06_production.py)")

    except Exception as e:
        print(f"[错误] {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())