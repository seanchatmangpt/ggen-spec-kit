# 40. Outcome Measurement

★★

*Features ship. Outcomes deliver. Outcome measurement tracks whether capabilities actually help customers make progress—not just whether they work.*

---

You defined **[Outcomes Desired](../context/outcome-desired.md)** when specifying the capability. Now it's in production. Are those outcomes being achieved?

Output metrics tell you what you shipped. Outcome metrics tell you if it mattered.

| Output Metric | Outcome Metric |
|---------------|----------------|
| Feature released | Customer progress made |
| Tests passing | Errors prevented |
| Commands available | Time saved |
| Documentation written | Questions answered |

Outcome measurement tracks the metrics that matter—the ones tied to customer progress.

**The problem: Shipping features feels like progress. But features without outcomes are waste. Outcome measurement reveals whether you're actually helping.**

---

**The forces at play:**

- *Measurement wants precision.* Exact numbers feel rigorous.

- *Outcomes want meaning.* Precise meaningless numbers aren't useful.

- *Attribution wants certainty.* Did our change cause the improvement?

- *Reality wants patience.* Outcomes take time to manifest.

The tension: measure meaningfully without false precision.

---

**Therefore:**

Implement outcome measurement that tracks the metrics defined in your outcome specifications.

**Outcome specification:**

```turtle
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    rdfs:label "Minimize validation time" ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:object "discovering syntax errors" ;
    jtbd:baseline "PT5M"^^xsd:duration ;  # 5 minutes
    jtbd:target "PT5S"^^xsd:duration ;    # 5 seconds
    jtbd:importance "high" ;
    jtbd:measurementMethod "otel:validate.duration histogram" .
```

**Measurement implementation:**

```python
# Outcome: Minimize validation time
# Measurement: validate.duration histogram

from opentelemetry import metrics

meter = metrics.get_meter(__name__)

validate_duration = meter.create_histogram(
    name="validate.duration",
    description="Time to complete validation",
    unit="ms",
)

def validate(file: Path) -> Result:
    start = time.perf_counter()
    result = do_validation(file)
    duration_ms = (time.perf_counter() - start) * 1000

    # Record outcome metric
    validate_duration.record(
        duration_ms,
        attributes={
            "file_size_bucket": categorize_size(file),
            "result": "success" if result.valid else "failure",
        }
    )
    return result
```

**Outcome tracking dashboard:**

```
Outcome: Minimize Validation Time
═══════════════════════════════════════════════════════════

Target: < 5 seconds (5000 ms)
Baseline: 5 minutes (300000 ms)

Current Performance:
  P50:  1,200 ms  ████████████░░░░░░░░ (76% to target)
  P90:  3,500 ms  ██████████████████░░ (30% to target)
  P99: 12,000 ms  ████████████████████ EXCEEDS TARGET

Trend (30 days):
  P50: ↓ 15% improvement
  P90: ↓ 8% improvement
  P99: ↑ 5% regression (investigate large files)

Segment Analysis:
  Small files (<100KB):   P50 = 200ms   ✓ Target met
  Medium files (100KB-1MB): P50 = 1,500ms  ✓ Target met
  Large files (>1MB):     P50 = 8,000ms  ✗ Exceeds target

Recommendation:
  Large file validation exceeds target. Consider streaming
  validation or async processing for files > 1MB.
```

**Outcome measurement categories:**

| Category | Example Outcomes | Measurement |
|----------|------------------|-------------|
| Time | Minimize time to X | Duration histograms |
| Errors | Minimize errors in Y | Error counters |
| Effort | Minimize steps to Z | Step counters |
| Confidence | Maximize confidence | Surveys |
| Success | Maximize completion rate | Success/failure ratio |

**Importance-Satisfaction tracking:**

```turtle
# Track satisfaction over time
jtbd:MinimizeValidationTime
    jtbd:satisfactionHistory [
        jtbd:date "2025-01-01"^^xsd:date ;
        jtbd:score 3 ;  # Scale 1-5
    ] ;
    jtbd:satisfactionHistory [
        jtbd:date "2025-02-01"^^xsd:date ;
        jtbd:score 4 ;  # Improved!
    ] .
```

---

**Resulting context:**

After applying this pattern, you have:

- Tracking of outcome metrics, not just output metrics
- Visibility into whether capabilities deliver value
- Data for prioritization decisions
- Foundation for continuous improvement

This feeds **[41. Gap Analysis](./gap-analysis.md)** and informs **[42. Specification Refinement](./specification-refinement.md)**.

---

**Related patterns:**

- *Measures:* **[5. Outcome Desired](../context/outcome-desired.md)** — Outcomes defined
- *Uses:* **[38. Observable Execution](../verification/observable-execution.md)** — Telemetry
- *Feeds:* **[41. Gap Analysis](./gap-analysis.md)** — Find gaps
- *Informs:* **[42. Specification Refinement](./specification-refinement.md)** — Improve specs

---

> *"You can't manage what you can't measure. But you can certainly measure the wrong things."*

Outcome measurement measures the right things—customer progress, not feature counts.
