# Prefix-Aware LLM Inference Scheduler

## Overview

This project implements a lightweight LLM serving system on top of vLLM to study how **request scheduling, batching, and prefix alignment** impact inference performance and KV cache effectiveness.

Instead of focusing only on model optimization, this system explores **system-level optimizations**—how incoming requests are shaped before reaching the model.

---

## Problem Statement

Modern LLM systems serve multiple concurrent requests. However:

* Similar requests are not guaranteed to be processed together
* KV cache reuse depends on prefix alignment
* Default batching does not consider semantic or structural similarity

This leads to inefficient utilization of compute.

This project explores:

> How request scheduling and prefix-aware grouping influence batching efficiency and KV cache reuse in real inference systems.

---

## Architecture

```
Client Requests
      ↓
API (FastAPI)
      ↓
Request Queue (async futures)
      ↓
Scheduler Loop (time-window batching ~50ms)
      ↓
[Naive OR Prefix-aware grouping]
      ↓
vLLM (KV cache ON/OFF)
      ↓
Response + Metrics (CSV + Logs)
```

---

## Key Components

### 1. Request Queue

* Fully decouples API from inference
* Requests are enqueued and return async futures
* Enables buffering for batching

### 2. Scheduler Loop

* Runs every ~50ms
* Pulls requests from queue
* Forms batches dynamically
* Core system control point

### 3. Naive Batching

* Groups requests purely by arrival
* No awareness of prompt similarity
* Baseline for comparison

### 4. Prefix-Aware Grouping

* Groups requests by prefix (first K tokens/characters)
* Ensures similar prompts are co-located
* Approximates real-world prefix reuse systems

### 5. KV Cache (vLLM)

* Enabled via:

  ```python
  LLM(..., enable_prefix_caching=True)
  ```
* Reuses previously computed key-value states
* Eliminates redundant prefill computation for identical prefixes

---

## Experiment Setup

Two independent toggles:

```
USE_GROUPING = True / False
ENABLE_PREFIX_CACHE = True / False
```

Metrics collected per request:

* latency (end - arrival)
* batch size
* group size

Example log:

```
[Metrics] {"id": "...", "latency": 0.706, "batch_size": 4, "group_size": 4}
```

---

## Experiments Performed

### 1. Baseline (No grouping, No cache)

* Random prompts
* Observed:

  * batch_size grows (2 → 8)
  * latency range ≈ 0.55s → 0.77s

### 2. Same Prefix (Naive batching)

* Identical prompts
* Observed:

  * batching works
  * no explicit grouping
  * no structural improvement

### 3. Prefix Grouping Only

* Same prefix, grouping ON
* Observed:

  * group_size == batch_size
  * structured batches
  * no major latency gain (no cache)

### 4. Mixed Prompts (Negative control)

* Different prefixes
* Observed:

  * multiple groups formed
  * scheduler splits workload

### 5. Cache Only

* Same prompt, cache ON
* Observed:

  * minimal improvement on CPU
  * cache benefit limited for first batch

### 6. Full System (Grouping + Cache)

* Same prompt, both ON

#### Observed Data (Batch size = 8)

**Case 1 (No grouping, No cache)**

Latencies:

```
0.858, 0.84, 0.825, 0.809, 0.785, 0.758, 0.743, 0.725
```

* Avg ≈ **0.793s**
* Spread ≈ **0.133s**

**Case 2 (Grouping + Cache)**

Latencies:

```
0.923, 0.889, 0.862, 0.835, 0.792, 0.762, 0.738, 0.715
```

* Avg ≈ **0.815s**
* Spread ≈ **0.208s**

---

## Results Interpretation

### Key Observation

> The "optimized" system is not always faster.

### Why?

1. **Prefill dominates latency (CPU constraint)**

   * First batch must compute everything
   * Cache reuse helps only after initial computation

2. **KV Cache ≠ Immediate Speedup**

   * Helps repeated prefixes
   * Benefits appear in steady-state, not first burst

3. **Grouping improves structure, not raw latency**

   * Aligns requests correctly
   * Enables cache—but does not guarantee gains

---

## Key Insights

### 1. Batching vs Caching

* Batching → improves throughput
* KV cache → reduces redundant computation
* They are orthogonal optimizations

---

### 2. Scheduling is the real bottleneck

> KV cache is only useful if similar requests arrive together.

---

### 3. Prefix-aware grouping

* Converts random traffic → structured traffic
* Maximizes cache reuse probability

---

### 4. Latency behavior

* Early requests in batch → higher latency
* Later requests → benefit more
* This creates latency spread

---

### 5. Hardware dependency

* CPU → minimal visible gains
* GPU / large models → significant improvements

---

## What This Project Demonstrates

* Real-world LLM serving architecture
* Importance of request scheduling
* Tradeoffs between latency and throughput
* When KV cache works—and when it doesn’t
* How batching alone is insufficient

---

## Limitations

* Prefix matching is naive (string-based)
* No semantic grouping
* CPU environment hides real gains
* Single-node system (no distributed scaling)

---

## Conclusion

> Efficient LLM serving is not just about faster models—it is about shaping requests correctly.

This project shows that:

* Batching improves throughput
* KV cache reduces redundant work
* Scheduling determines whether cache can be used at all

---

## Future Work

* Token-level prefix matching
* Adaptive batching window
* GPU benchmarking
* Integration with SGLang / RadixAttention-style execution
* Multi-node scheduling

---

## Resume Bullet

Built a prefix-aware LLM inference scheduler on top of vLLM, demonstrating how request grouping affects batching efficiency and KV cache utilization, with controlled experiments analyzing latency behavior under different scheduling strategies.
