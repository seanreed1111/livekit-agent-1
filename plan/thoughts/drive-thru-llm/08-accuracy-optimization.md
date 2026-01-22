# Plan 08: Accuracy Optimization (Advanced Strategies)

**Created**: 2026-01-21
**Status**: Optional/Future Work
**Dependencies**: Plans 01-07 (Complete working system with baseline accuracy)
**Estimated Complexity**: Medium-High

---

## Overview

This plan covers **advanced accuracy optimization strategies** to improve beyond the baseline 95% accuracy achieved in Plan 07. These are **optional enhancements** that can be implemented after the core system is working.

**Current State** (after Plan 07):
- ✅ Strategy 1: Function Calling
- ✅ Strategy 2: Menu Context Injection
- ✅ Strategy 4: Fuzzy String Matching
- ✅ Strategy 9: Post-Processing Validation

**This Plan Adds**:
- 🔄 Strategy 3: Explicit Confirmation Loop
- 🧠 Strategy 5: Semantic Search with Embeddings
- 📊 Strategy 6: Two-Stage Parsing (if needed)
- 💭 Strategy 7: Chain-of-Thought Prompting
- 🎯 Strategy 10: Context Window Optimization

---

## When to Implement This Plan

**Implement if**:
- Baseline accuracy < 95% on test suite
- Specific failure patterns identified (e.g., modifier confusion, similar item names)
- Need to push accuracy to 98%+
- Cost/latency optimization needed

**Skip if**:
- Baseline accuracy >= 95%
- System meets requirements
- Want to focus on other features first

---

## Strategy 3: Explicit Confirmation Loop

### Overview

Add explicit confirmation steps before committing items to order.

### Implementation

**Approach 1**: Modify agent instructions

```python
def _get_instructions(self) -> str:
    return """...existing instructions...

    Confirmation Protocol:
    - After understanding an item request, CONFIRM with the customer before adding
    - Example: "Got it, one Big Mac. Is that correct?"
    - Wait for customer to confirm ("yes", "correct", "that's right")
    - If customer corrects, update accordingly
    - Only call add_item_to_order AFTER confirmation
    """
```

**Approach 2**: Add confirmation state to OrderStateManager

```python
class OrderStateManager:
    def __init__(self, ...):
        self._pending_items = []  # Items awaiting confirmation

    def stage_item(self, ...) -> OrderItem:
        """Stage item for confirmation (doesn't add to order yet)."""
        item = OrderItem(...)
        self._pending_items.append(item)
        return item

    def confirm_staged_item(self, item_id: str) -> bool:
        """Confirm and add staged item to order."""
        # Move from pending to confirmed
        ...
```

### Testing

Add BDD scenarios:
```gherkin
Scenario: Customer confirms item
  When the customer says "I want a Big Mac"
  Then the agent asks "Did you say one Big Mac?"
  When the customer says "yes"
  Then the item is added to the order

Scenario: Customer corrects item
  When the customer says "I want a Big Mac"
  Then the agent asks "Did you say one Big Mac?"
  When the customer says "no, a McDouble"
  Then the agent updates to McDouble
  And asks for confirmation again
```

### Trade-offs

**Pros**:
- Catches errors before commitment
- Builds customer confidence
- Clear correction path

**Cons**:
- Slower ordering process
- May annoy customers with simple orders
- More conversation turns

**Recommendation**: Make configurable via `enable_confirmation_loop` flag

---

## Strategy 5: Semantic Search with Embeddings

### Overview

Use vector embeddings to find semantically similar menu items, handling synonyms and paraphrasing.

### Implementation

#### 1. Pre-compute Menu Embeddings

```python
from openai import OpenAI
import numpy as np

class MenuEmbeddingsProvider:
    """Precomputed embeddings for menu items."""

    def __init__(self, menu_provider: MenuProvider):
        self.menu_provider = menu_provider
        self.embeddings_cache = self._load_or_compute_embeddings()

    def _compute_embeddings(self) -> dict[str, np.ndarray]:
        """Compute embeddings for all menu items."""
        client = OpenAI()
        items = self._get_all_menu_items()

        embeddings = {}
        for item in items:
            # Create searchable text
            text = f"{item.item_name} {item.category}"

            # Get embedding
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            embeddings[item.item_name] = np.array(response.data[0].embedding)

        return embeddings

    def _save_embeddings(self, embeddings: dict) -> None:
        """Save to disk for fast loading."""
        import pickle
        with open("menu_embeddings.pkl", "wb") as f:
            pickle.dump(embeddings, f)

    def _load_embeddings(self) -> dict | None:
        """Load from disk if exists."""
        if not Path("menu_embeddings.pkl").exists():
            return None

        with open("menu_embeddings.pkl", "rb") as f:
            return pickle.load(f)

    def _load_or_compute_embeddings(self) -> dict:
        """Load from disk or compute if not cached."""
        embeddings = self._load_embeddings()
        if embeddings is None:
            embeddings = self._compute_embeddings()
            self._save_embeddings(embeddings)
        return embeddings

    def semantic_search(self, query: str, top_k: int = 5) -> list[tuple[Item, float]]:
        """
        Find most semantically similar items.

        Args:
            query: Customer's query (e.g., "cheeseburger")
            top_k: Number of results to return

        Returns:
            List of (Item, similarity_score) tuples
        """
        # Get query embedding
        client = OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = np.array(response.data[0].embedding)

        # Compute similarity to all items
        similarities = []
        for item_name, item_embedding in self.embeddings_cache.items():
            # Cosine similarity
            similarity = np.dot(query_embedding, item_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(item_embedding)
            )

            item = self.menu_provider.get_item_by_name(item_name)
            similarities.append((item, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]
```

#### 2. Integrate into MenuProvider

```python
class MenuProvider:
    def __init__(self, menu_file_path: str, use_embeddings: bool = False):
        # ... existing code ...

        if use_embeddings:
            self._embeddings = MenuEmbeddingsProvider(self)

    def semantic_search(self, query: str, top_k: int = 5) -> list[Item]:
        """Semantic search using embeddings."""
        if not hasattr(self, '_embeddings'):
            raise ValueError("Embeddings not enabled")

        results = self._embeddings.semantic_search(query, top_k)
        return [item for item, score in results]
```

#### 3. Use in DriveThruLLM

```python
class DriveThruLLM(LLM):
    def _find_relevant_items(self, keywords: list[str]) -> list[Item]:
        """Find relevant items using semantic search if enabled."""
        if self._use_semantic_search:
            # Use embeddings
            query = " ".join(keywords)
            return self._menu_provider.semantic_search(query, top_k=20)
        else:
            # Use keyword search (existing code)
            return self._keyword_search(keywords)
```

### Testing

```python
def test_semantic_search_synonyms():
    """Verify semantic search handles synonyms."""
    embeddings = MenuEmbeddingsProvider(menu_provider)

    # "cheeseburger" should find Quarter Pounder with Cheese, etc.
    results = embeddings.semantic_search("cheeseburger", top_k=5)

    assert any("cheese" in item.item_name.lower() for item, score in results)

def test_semantic_search_paraphrasing():
    """Verify semantic search handles paraphrasing."""
    # "chicken pieces" → Chicken McNuggets
    results = embeddings.semantic_search("chicken pieces", top_k=5)

    assert any("McNuggets" in item.item_name for item, score in results)
```

### Trade-offs

**Pros**:
- Handles synonyms ("cheeseburger" → Quarter Pounder with Cheese)
- Robust to paraphrasing
- Better understanding of customer intent

**Cons**:
- Additional complexity
- Requires OpenAI API calls (cost)
- Adds latency (~50-100ms per search)
- Requires pre-computation and caching

**Recommendation**: Implement if fuzzy matching alone isn't sufficient

---

## Strategy 7: Chain-of-Thought Prompting

### Implementation

Modify agent instructions to use chain-of-thought:

```python
def _get_instructions(self) -> str:
    return """...existing instructions...

    Decision Process:
    When a customer orders, think step-by-step:

    1. **Identify Item Type**: What category is this? (burger, breakfast, drink, etc.)
    2. **Match to Menu**: Which specific menu item matches best?
    3. **Extract Modifiers**: Did they mention customizations?
    4. **Determine Quantity**: How many?
    5. **Verify**: Does this make sense?

    Example:
    Customer: "I'd like a cheeseburger with no pickles"

    Thinking:
    1. Item type: burger
    2. Menu match: Could be Cheeseburger, Quarter Pounder with Cheese, or Double Cheeseburger
    3. Modifiers: "no pickles"
    4. Quantity: 1 (not specified, default to 1)
    5. Verification: Most likely "Cheeseburger" from menu

    Then call: add_item_to_order(category="Beef & Pork", item_name="Cheeseburger", modifiers=["No Pickles"], quantity=1)
    """
```

### Testing

Verify LLM follows chain-of-thought process (check logs or use judge to evaluate reasoning).

### Trade-offs

**Pros**:
- Improves LLM reasoning
- More interpretable
- Catches logic errors

**Cons**:
- Increases token usage (~100-200 tokens per request)
- Adds latency
- Reasoning not visible to customer (unless we expose it)

---

## Strategy 10: Context Window Optimization

### Implementation

**Dynamic Category Filtering**

```python
class DriveThruLLM(LLM):
    def _detect_category(self, message: str) -> str | None:
        """Detect which category customer is likely ordering from."""
        message_lower = message.lower()

        # Simple heuristics
        if any(word in message_lower for word in ["breakfast", "morning", "egg", "mcmuffin"]):
            return "Breakfast"
        elif any(word in message_lower for word in ["burger", "mac", "quarter"]):
            return "Beef & Pork"
        elif any(word in message_lower for word in ["chicken", "nugget", "fish"]):
            return "Chicken & Fish"
        elif any(word in message_lower for word in ["drink", "coke", "sprite", "beverage"]):
            return "Beverages"
        # ... more categories ...

        return None  # No clear category

    def _find_relevant_items(self, keywords: list[str], message: str) -> list[Item]:
        """Find relevant items, filtered by detected category."""
        # Detect category
        category = self._detect_category(message)

        if category:
            # Only search within that category
            return self._menu_provider.search_items(
                keyword=" ".join(keywords),
                category=category
            )
        else:
            # Search all categories
            return self._menu_provider.search_items(
                keyword=" ".join(keywords)
            )
```

### Trade-offs

**Pros**:
- Reduces token usage (inject fewer items)
- Reduces noise (more focused context)
- Faster inference

**Cons**:
- May miss cross-category orders
- Requires accurate category detection
- More complex logic

---

## Experimentation Framework

### A/B Testing Different Strategies

```python
class AccuracyExperiment:
    """Framework for A/B testing accuracy strategies."""

    def __init__(self, test_cases: list[TestCase]):
        self.test_cases = test_cases

    async def run_experiment(
        self,
        config: DriveThruConfig,
        strategy_name: str
    ) -> ExperimentResults:
        """Run all test cases with given config."""
        results = []

        for test_case in self.test_cases:
            # Create agent with config
            agent = self._create_agent(config)

            # Run test
            result = await self._run_test(agent, test_case)

            results.append({
                "test_case": test_case.name,
                "strategy": strategy_name,
                "passed": result.passed,
                "accuracy": result.accuracy,
                "latency": result.latency,
                "cost": result.cost
            })

        return ExperimentResults(results)

    def compare_strategies(
        self,
        baseline_config: DriveThruConfig,
        experiment_config: DriveThruConfig
    ) -> Comparison:
        """Compare two configurations."""
        baseline_results = await self.run_experiment(baseline_config, "baseline")
        experiment_results = await self.run_experiment(experiment_config, "experiment")

        return Comparison(
            baseline=baseline_results,
            experiment=experiment_results,
            metrics=["accuracy", "latency", "cost"]
        )
```

### Example Experiments

**Experiment 1**: Fuzzy matching threshold
- Baseline: threshold=85
- Variants: threshold=75, threshold=90, threshold=95
- Metric: Item accuracy

**Experiment 2**: Semantic search vs keyword search
- Baseline: keyword search only
- Variant: semantic search enabled
- Metrics: Accuracy, latency, cost

**Experiment 3**: Confirmation loop
- Baseline: no confirmation
- Variant: confirmation enabled
- Metrics: Accuracy, conversation length, user satisfaction

---

## Implementation Checklist

### Phase 1: Identify Optimization Needs
- [ ] Run full test suite, measure baseline accuracy
- [ ] Identify failure patterns (which scenarios fail?)
- [ ] Categorize failures (item confusion, modifier errors, quantity errors, etc.)
- [ ] Prioritize strategies to address failures

### Phase 2: Implement Selected Strategies
- [ ] Strategy 3: Confirmation loop (if needed)
- [ ] Strategy 5: Semantic search (if fuzzy matching insufficient)
- [ ] Strategy 7: Chain-of-thought (if reasoning errors observed)
- [ ] Strategy 10: Context optimization (if token usage/latency high)

### Phase 3: A/B Testing
- [ ] Create experiment framework
- [ ] Define test cases
- [ ] Run baseline experiment
- [ ] Run variant experiments
- [ ] Compare metrics: accuracy, latency, cost

### Phase 4: Analysis
- [ ] Analyze experiment results
- [ ] Identify best-performing strategy
- [ ] Verify accuracy improvement
- [ ] Check latency/cost impact

### Phase 5: Production Deployment
- [ ] Update default config with optimal strategy
- [ ] Re-run full test suite
- [ ] Verify 95%+ accuracy achieved
- [ ] Document accuracy improvements
- [ ] Update configuration docs

---

## Success Criteria

✅ **Accuracy >= 95%** on full BDD test suite
✅ **Optimal strategy identified** via A/B testing
✅ **Latency acceptable** (<2s per turn)
✅ **Cost reasonable** (<$0.05 per order)
✅ **All tests pass** with optimized configuration

---

## Design Notes

### When to Optimize

**Optimize Early If**:
- Critical accuracy requirements (e.g., production system)
- Known difficult edge cases
- Cost/latency constraints

**Optimize Later If**:
- Baseline accuracy sufficient
- MVP approach
- Learning/experimentation focus

### Measure, Don't Guess

Always measure impact:
- Accuracy change: +X% item accuracy
- Latency change: +Y ms per turn
- Cost change: +$Z per order

Make data-driven decisions.

### Diminishing Returns

- 90% → 95% accuracy: Moderate effort
- 95% → 98% accuracy: Significant effort
- 98% → 99.5% accuracy: Extreme effort

Choose target based on requirements and ROI.

---

## Future Enhancements

Beyond this plan:

1. **Active Learning**: Learn from corrections, improve over time
2. **Personalization**: Remember customer preferences
3. **Multi-turn Context**: Better understanding of conversation history
4. **Voice-specific Optimization**: Handle STT errors better
5. **Menu Evolution**: Adapt to menu changes automatically

---

**Key Principle**: Optimize based on measured needs, not speculation. Start with simple strategies, add complexity only when data shows it's needed. 95% accuracy with simple system beats 97% accuracy with complex, fragile system.
