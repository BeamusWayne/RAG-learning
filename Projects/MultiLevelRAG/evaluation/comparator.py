# -*- coding: utf-8 -*-
"""
横向对比器 — 并发执行多个策略并汇总结果
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from concurrent.futures import ThreadPoolExecutor, as_completed
from router import STRATEGY_META


def compare_all(question: str, strategies: list[str] | None = None) -> list[dict]:
    """并发运行所有（或指定）策略，返回按耗时排序的结果列表"""
    from strategies import baseline_rag, hyde_rag, fusion_rag, crag, graph_rag

    runners = {
        "baseline": baseline_rag.run,
        "hyde":     hyde_rag.run,
        "fusion":   fusion_rag.run,
        "crag":     crag.run,
        "graph":    graph_rag.run,
    }
    targets = strategies or list(runners.keys())

    def _run(name: str):
        t0 = time.time()
        try:
            result = runners[name](question=question)
        except Exception as e:
            result = {"strategy": name, "answer": f"[错误] {e}", "error": str(e)}
        result["elapsed_ms"] = round((time.time() - t0) * 1000)
        result["strategy_name"] = STRATEGY_META.get(name, (name, ""))[0]
        result["strategy_desc"] = STRATEGY_META.get(name, ("", ""))[1]
        return result

    results = []
    with ThreadPoolExecutor(max_workers=len(targets)) as pool:
        futures = {pool.submit(_run, name): name for name in targets}
        for fut in as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda r: r.get("elapsed_ms", 0))
    return results
