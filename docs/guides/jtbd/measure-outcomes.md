# Measure Jobs-to-be-Done Outcomes

Learn how to define, track, and measure job outcome satisfaction throughout the product lifecycle.

## Defining Measurable Outcomes

### Outcome Structure

Every job outcome needs:

```
1. Clear statement of desired result
2. Measurable success criteria
3. Baseline (current state)
4. Target (desired state)
5. Timeline (when to achieve)
6. Owner (who's responsible)
```

## Example: Process Data Job

### Define the Job

```
Job: Process data files from raw format into analysis-ready format

Actor: Data analyst
Context: Daily data ingestion workflow
Frequency: Every morning before analysis
Pain: Takes 15+ minutes manually
```

### Define Outcomes

**Outcome 1:** Validate data quickly

```
Statement: Files validated in minimal time

Measurable: Validation completes in < 1 minute per 100MB

Baseline:
  - Current: 2 minutes per 100MB (manual spot-checking)
  - Measured: Tracked last 5 data loads
  - Average: 1:58

Target:
  - Goal: < 1 minute per 100MB
  - Stretch: < 30 seconds per 100MB

Timeline:
  - MVP: Achieve target by Q1 2026
  - Stretch: Achieve stretch by Q2 2026

Owner: Data engineering team

Success metrics:
  [ ] Validation completes in < 60 seconds
  [ ] Error detection accuracy > 99%
  [ ] Catches schema mismatches before processing
```

**Outcome 2:** Detect and prevent errors

```
Statement: Data quality issues caught before downstream systems

Measurable: Error detection rate > 99%

Baseline:
  - Current: 70% of errors caught (rest discovered downstream)
  - Measured: Reviewed last 30 days of incidents
  - Breakdown:
    - Schema mismatches: 45% missed
    - Missing values: 30% missed
    - Out-of-range values: 20% missed
    - Type mismatches: 5% missed

Target:
  - Goal: 99% error detection

Implementation:
  - Add schema validation: +20% coverage
  - Add range checks: +15% coverage
  - Add type checking: +5% coverage
  - Add custom rules: +15% coverage
  Total improvement: 55% → 99%

Timeline:
  - MVP: Achieve > 95% by Q1 2026
  - Final: Achieve 99% by Q2 2026

Owner: Data engineering + Analytics team
```

**Outcome 3:** Reduce manual work

```
Statement: Analyst doesn't need to manually fix data issues

Measurable: Manual rework time < 5% of total processing time

Baseline:
  - Current: 30% of processing time spent on manual fixes
  - Measured:
    - Load raw data: 3 min (20%)
    - Validate & fix manually: 9 min (60%)
    - Export processed: 3 min (20%)
    - Total: 15 minutes

  - Breakdown of manual time:
    - Schema issues: 4 min
    - Missing values: 3 min
    - Formatting: 2 min

Target:
  - Goal: Manual work < 5% (< 45 seconds of 15 min total)

How to achieve:
  - Automated schema mapping: -4 min
  - Automated missing value handling: -3 min
  - Automated formatting: -2 min
  - Expected manual time: 0 min (better than target!)

Timeline:
  - MVP: < 10% manual time by Q1 2026
  - Final: < 5% manual time by Q2 2026

Owner: Data engineering team
```

## Tracking Outcomes Over Time

### Measurement Dashboard

Create a dashboard to track outcomes:

```
Job: Process Data Files
Last updated: 2025-12-23

Outcome 1: Validation speed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current:    1:30/100MB
Target:     1:00/100MB
Status:     ✓ ON TRACK (1:30 < 2:00 baseline)
Trend:      ↓ Improving (was 1:45 last week)
Progress:   82% to target

Outcome 2: Error detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current:    94%
Target:     99%
Status:     ⚠ NEEDS WORK (94% < 99%)
Trend:      ↑ Improving (was 85% last month)
Progress:   47% to target

Outcome 3: Manual work reduction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current:    8%
Target:     5%
Status:     ⚠ CLOSE (8% vs 5% target)
Trend:      ↓ Improving (was 12% last month)
Progress:   95% to target

Overall job satisfaction: 75% (improving)
```

### Collect Data

**Method 1: Automated Metrics**

```python
# Track in instrumentation
from specify_cli.core.telemetry import meter

# Counter: processing events
process_counter = meter.create_counter("process.events")

# Gauge: processing duration
duration_gauge = meter.create_gauge(
    "process.duration_seconds",
    unit="s"
)

# Histogram: error detection rates
error_rate_histogram = meter.create_histogram(
    "process.error_detection_rate",
    unit="1"  # percentage 0-100
)

def process_data_files(files):
    start = time.time()

    # ... processing code ...

    # Record metrics
    process_counter.add(len(files))
    duration = time.time() - start
    duration_gauge.record(duration)

    errors_detected = 94  # from validation
    total_errors = 100
    error_rate = (errors_detected / total_errors) * 100
    error_rate_histogram.record(error_rate)
```

**Method 2: Manual Tracking**

```bash
# Track in spreadsheet or database
date,validation_time_sec,error_detection_pct,manual_time_pct
2025-12-16,90,88,12
2025-12-17,88,90,10
2025-12-18,92,91,11
2025-12-19,87,92,9
2025-12-20,85,93,8
2025-12-21,90,94,8
2025-12-22,88,93,9
2025-12-23,86,94,8
```

**Method 3: User Feedback**

```
Survey questions (weekly):

1. How much time did you spend validating data today?
   [ ] < 1 min    [ ] 1-2 min    [ ] 2-5 min    [ ] > 5 min

2. How many errors slipped through to downstream systems?
   [ ] 0    [ ] 1-5    [ ] 6-10    [ ] > 10

3. How much time on manual fixes?
   [ ] < 5%    [ ] 5-10%    [ ] 10-20%    [ ] > 20%

4. Overall satisfaction with data processing?
   1 = Very dissatisfied
   5 = Very satisfied
   [ ] 1    [ ] 2    [ ] 3    [ ] 4    [ ] 5
```

## Analyze Results

### Trend Analysis

```bash
# Plot outcomes over time
python scripts/plot-outcomes.py \
  --job "Process Data Files" \
  --metric "validation_time" \
  --output validation-trend.png

# Output shows:
#   Week 1: 120 sec/100MB
#   Week 2: 105 sec/100MB (↓ 12%)
#   Week 3: 90 sec/100MB (↓ 14%)
#   Week 4: 86 sec/100MB (↓ 4%)
#   Trend: Improving, on track for target
```

### Gap Analysis

```
Outcome satisfaction gaps:

HIGH IMPACT, QUICK WIN:
  - Error detection (94% → 99%)
    Gap: 5 percentage points
    Effort: Medium (add range checks)
    Impact: High (prevents downstream issues)
    Priority: 1

  - Manual work reduction (8% → 5%)
    Gap: 3 percentage points
    Effort: Low (automate existing validation)
    Impact: High (saves time daily)
    Priority: 2

MEDIUM IMPACT:
  - Validation speed (1:30 → 1:00)
    Gap: 30 seconds
    Effort: High (optimize parsing)
    Impact: Medium (saves time)
    Priority: 3

LOW IMPACT:
  - None identified
```

## Satisfaction Score

Calculate overall job satisfaction:

```
Outcome 1: Validation speed
  Current: 1:30
  Target: 1:00
  Progress: (2:00 - 1:30) / (2:00 - 1:00) = 60% to target
  Satisfaction: 60%

Outcome 2: Error detection
  Current: 94%
  Target: 99%
  Progress: (94 - 70) / (99 - 70) = 82% to target
  Satisfaction: 82%

Outcome 3: Manual work
  Current: 8%
  Target: 5%
  Progress: (12 - 8) / (12 - 5) = 57% to target
  Satisfaction: 57%

OVERALL JOB SATISFACTION:
  Average: (60 + 82 + 57) / 3 = 66%
  Trend: ↑ Improving
```

## Setting New Targets

Based on outcomes and satisfaction:

```
Current outcome satisfaction: 75%

Review results:
  ✓ Validation speed: On track
  ✓ Manual work: Nearly done
  ⚠ Error detection: Needs focus

NEW TARGETS:

Q1 2026 Priorities:
  1. Improve error detection to 99% (highest gap)
  2. Reduce manual work below 5% (nearly there)
  3. Maintain validation speed at < 1 min

Q2 2026 Stretch Goals:
  1. Validation speed < 30 seconds (2x improvement)
  2. Error detection 99.5% (perfection)
  3. Zero manual work (fully automated)

New metrics to add:
  - Data accuracy after processing
  - User satisfaction survey
  - Processing cost per file
```

## Communicate Results

### Stakeholder Update

```markdown
# Job Outcome Report: Process Data Files

## Summary
Overall job satisfaction improving: 66% → 75% (↑9 points)

## Outcomes Status

| Outcome | Current | Target | Status | Trend |
|---------|---------|--------|--------|-------|
| Validation speed | 1:30/100MB | 1:00/100MB | 🟢 ON TRACK | ↓ Good |
| Error detection | 94% | 99% | 🟡 NEEDS WORK | ↑ Good |
| Manual work | 8% | 5% | 🟡 CLOSE | ↓ Improving |

## Next Steps (Priority Order)

1. **Improve error detection** (High Impact, Medium Effort)
   - Add range validation: +5% coverage
   - Add custom rules: +3% coverage
   - Timeline: 2 weeks

2. **Reduce manual work** (High Impact, Low Effort)
   - Automate missing value handling
   - Timeline: 1 week

3. **Optimize validation speed** (Medium Impact, High Effort)
   - Profile current bottleneck
   - Parallelize validation
   - Timeline: 4 weeks

## Recommendation
Start with error detection improvement - highest impact relative to effort.
```

## See Also

- `apply-framework.md` - Full JTBD framework guide
- `/docs/commands/jtbd.md` - JTBD command reference
- `/docs/reference/jtbd-framework.md` - JTBD terminology
- `/docs/guides/testing/run-tests.md` - Testing outcomes
- `/docs/reference/quality-metrics.md` - Metric definitions
