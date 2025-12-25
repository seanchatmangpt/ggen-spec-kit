#!/bin/bash
# Comprehensive type error fixer

cd /home/user/ggen-spec-kit

# Fix prioritization.py - no-any-return errors
sed -i 's/return sum(factors) \/ len(factors)/return float(sum(factors) \/ len(factors))/g' \
    src/specify_cli/hyperdimensional/prioritization.py

sed -i 's/return min(entropy_reduction, 1\.0)/return float(min(entropy_reduction, 1.0))/g' \
    src/specify_cli/hyperdimensional/prioritization.py

sed -i 's/return entropy_reduction \/ effort/return float(entropy_reduction \/ effort)/g' \
    src/specify_cli/hyperdimensional/prioritization.py

sed -i 's/return min(value, 100\.0)/return float(min(value, 100.0))/g' \
    src/specify_cli/hyperdimensional/prioritization.py

sed -i 's/return importance \* satisfaction_gap \* (market_size \/ 100)/return float(importance * satisfaction_gap * (market_size \/ 100))/g' \
    src/specify_cli/hyperdimensional/prioritization.py

sed -i 's/return total_market \* addressable_percentage/return float(total_market * addressable_percentage)/g' \
    src/specify_cli/hyperdimensional/prioritization.py

sed -i 's/return min(advantage, 1\.0)/return float(min(advantage, 1.0))/g' \
    src/specify_cli/hyperdimensional/prioritization.py

sed -i 's/return min(timing_score, 1\.0)/return float(min(timing_score, 1.0))/g' \
    src/specify_cli/hyperdimensional/prioritization.py

# Fix ast_nodes.py - no-any-return errors
sed -i 's/return self\.parameters\.get("distance", self\.parameters\.get("within_distance", 0\.3))/return float(self.parameters.get("distance", self.parameters.get("within_distance", 0.3)))/g' \
    src/specify_cli/hyperdimensional/ast_nodes.py

sed -i 's/return self\.parameters\.get("metric", "cosine")/return str(self.parameters.get("metric", "cosine"))/g' \
    src/specify_cli/hyperdimensional/ast_nodes.py

# Fix process_mining.py - type mismatches
sed -i 's/2 \* fitness_val \* precision \/ (fitness_val + precision)/2 * float(fitness_val) * precision \/ (float(fitness_val) + precision)/g' \
    src/specify_cli/ops/process_mining.py

echo "Type fixes applied"
