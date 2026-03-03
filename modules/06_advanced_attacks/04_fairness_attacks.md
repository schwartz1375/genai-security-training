# Fairness Attacks in Machine Learning

## Introduction

Fairness in machine learning is not just an ethical concern—it's a security issue. Adversaries can exploit fairness mechanisms, manipulate fairness metrics, or weaponize bias to achieve malicious goals. This document covers advanced fairness attacks from a red team perspective.

## Why Fairness Matters for Security

### Security Implications

1. **Regulatory Compliance**: GDPR, EU AI Act, sector-specific regulations
2. **Legal Liability**: Discriminatory decisions can lead to lawsuits
3. **Reputational Risk**: Bias scandals damage trust
4. **Attack Surface**: Fairness constraints can be exploited
5. **Adversarial Manipulation**: Bias can be weaponized

### The Fairness-Security Nexus

```
Traditional View: Fairness ≠ Security
Red Team View: Fairness IS Security

Why?
- Fairness mechanisms can be attacked
- Bias can be a backdoor
- Fairness metrics can be gamed
- Debiasing can introduce vulnerabilities
```

## Fairness Definitions

### Mathematical Fairness Metrics

#### 1. Demographic Parity (Statistical Parity)
```
P(Ŷ = 1 | A = 0) = P(Ŷ = 1 | A = 1)

Where:
- Ŷ: Predicted outcome
- A: Protected attribute (e.g., race, gender)
```

**Meaning**: Positive prediction rate should be equal across groups

**Attack Vector**: Satisfy metric while maintaining hidden bias

#### 2. Equalized Odds
```
P(Ŷ = 1 | Y = y, A = 0) = P(Ŷ = 1 | Y = y, A = 1)  for y ∈ {0,1}

Where:
- Y: True outcome
```

**Meaning**: True positive and false positive rates equal across groups

**Attack Vector**: Manipulate one metric while violating fairness in practice

#### 3. Calibration
```
P(Y = 1 | Ŷ = p, A = a) = p  for all a, p

Where:
- p: Predicted probability
```

**Meaning**: Predictions should be well-calibrated across groups

**Attack Vector**: Achieve calibration through biased probability estimates

#### 4. Individual Fairness
```
d(x₁, x₂) ≈ 0 ⟹ d(f(x₁), f(x₂)) ≈ 0

Where:
- d: Distance metric
- f: Model function
```

**Meaning**: Similar individuals should receive similar predictions

**Attack Vector**: Define similarity metric that encodes bias

### Impossibility Results

**Key Insight**: Multiple fairness definitions cannot be satisfied simultaneously

```
Theorem (Chouldechova, 2017):
If prevalence differs across groups, cannot simultaneously achieve:
- Calibration
- Equal false positive rates
- Equal false negative rates
```

**Attack Implication**: Adversary can force trade-offs, exploit conflicts

## Fairness Attack Taxonomy

### 1. Fairness Poisoning

**Objective**: Manipulate training data to introduce bias while appearing fair

#### Attack Method
```python
# Poisoning strategy
def fairness_poisoning(X_train, y_train, protected_attr):
    # Step 1: Identify samples near decision boundary
    boundary_samples = find_boundary_samples(X_train, y_train)
    
    # Step 2: Flip labels strategically
    # Maintain overall fairness metrics
    # But introduce bias in specific regions
    for sample in boundary_samples:
        if should_flip(sample, protected_attr):
            y_train[sample] = 1 - y_train[sample]
    
    return X_train, y_train
```

#### Real-World Example
```
Scenario: Loan approval system
Attack: Poison training data
Method: Flip labels for qualified minority applicants
Result: Model learns to reject minorities
Metric: Demographic parity still satisfied (overall rates equal)
Impact: Systematic discrimination hidden by fairness metrics
```

### 2. Bias Injection

**Objective**: Introduce targeted bias that evades detection

#### Techniques

**A. Feature Manipulation**
```python
# Inject bias through correlated features
def inject_bias(X, protected_attr, proxy_feature):
    # Create correlation between proxy and protected attribute
    # Model learns bias through proxy
    X[proxy_feature] = encode_bias(X[protected_attr])
    return X
```

**B. Label Correlation**
```python
# Correlate labels with protected attribute
def correlate_labels(y, protected_attr, correlation_strength):
    # Subtle correlation that evades fairness checks
    noise = generate_correlated_noise(protected_attr, correlation_strength)
    y_biased = y + noise
    return y_biased
```

### 3. Fairness Washing

**Objective**: Appear fair while maintaining discrimination

#### Strategy
```python
# Satisfy fairness metrics superficially
def fairness_washing(model, X_test, protected_attr):
    # Step 1: Measure fairness metrics
    metrics = compute_fairness_metrics(model, X_test, protected_attr)
    
    # Step 2: Adjust predictions to satisfy metrics
    # While maintaining bias in practice
    adjusted_predictions = adjust_for_metrics(
        model.predict(X_test),
        metrics,
        protected_attr
    )
    
    return adjusted_predictions
```

#### Example
```
Hiring System:
- Metric: Equal interview rates across genders
- Reality: Different evaluation criteria during interviews
- Result: Appears fair, but discriminates in practice
```

### 4. Metric Manipulation

**Objective**: Game specific fairness metrics

#### Attack: Satisfying Demographic Parity While Discriminating

```python
def game_demographic_parity(model, X, y, protected_attr):
    """
    Achieve demographic parity while maintaining bias
    """
    # Get predictions
    predictions = model.predict(X)
    
    # Calculate current rates
    rate_group_0 = predictions[protected_attr == 0].mean()
    rate_group_1 = predictions[protected_attr == 1].mean()
    
    # Adjust to equalize rates
    if rate_group_0 > rate_group_1:
        # Randomly promote some from group 1
        # But use biased selection within group
        promote_biased_subset(predictions, protected_attr, 1)
    
    # Now demographic parity is satisfied
    # But discrimination persists within groups
    return predictions
```

### 5. Adversarial Fairness

**Objective**: Exploit fairness constraints for adversarial advantage

#### Attack Scenario: Adversarial Examples with Fairness
```python
def fairness_constrained_adversarial(model, x, y, protected_attr):
    """
    Generate adversarial example that:
    1. Causes misclassification
    2. Maintains fairness metrics
    """
    # Standard adversarial perturbation
    perturbation = generate_adversarial_perturbation(model, x, y)
    
    # Add fairness constraint
    # Ensure attack doesn't violate fairness metrics
    fairness_constraint = compute_fairness_constraint(
        model, x + perturbation, protected_attr
    )
    
    # Optimize with constraint
    final_perturbation = optimize_with_fairness(
        perturbation, fairness_constraint
    )
    
    return x + final_perturbation
```

## Advanced Attack Techniques

### 1. Proxy Feature Exploitation

**Concept**: Use non-protected features correlated with protected attributes

```python
# Example: ZIP code as proxy for race
def exploit_proxy_features(X, protected_attr):
    # Find features correlated with protected attribute
    proxy_features = find_correlated_features(X, protected_attr)
    
    # Model learns bias through proxies
    # Fairness checks on protected attribute pass
    # But discrimination persists through proxies
    return proxy_features
```

**Real-World Examples**:
- ZIP code → Race
- First name → Gender/ethnicity
- School name → Socioeconomic status
- Purchase history → Age/income

### 2. Intersectional Bias

**Concept**: Exploit bias at intersections of multiple attributes

```python
def intersectional_attack(model, X, protected_attrs):
    """
    Attack specific intersectional groups
    Example: Black women, elderly Hispanics, etc.
    """
    # Identify intersectional groups
    groups = identify_intersections(protected_attrs)
    
    # Target specific intersections
    for group in groups:
        if is_vulnerable(group):
            inject_bias_for_group(model, X, group)
    
    # Overall fairness metrics may still pass
    # But specific intersections are discriminated against
    return model
```

### 3. Temporal Bias Injection

**Concept**: Introduce bias that emerges over time

```python
def temporal_bias_attack(model, X_stream, protected_attr):
    """
    Gradually introduce bias in online learning
    """
    for t, (X_t, y_t) in enumerate(X_stream):
        # Slowly increase bias over time
        bias_strength = compute_temporal_bias(t)
        
        # Inject biased samples
        X_biased, y_biased = inject_temporal_bias(
            X_t, y_t, protected_attr, bias_strength
        )
        
        # Update model
        model.partial_fit(X_biased, y_biased)
    
    # Bias accumulates gradually
    # Harder to detect than sudden changes
    return model
```

### 4. Fairness-Accuracy Trade-off Exploitation

**Concept**: Force defenders to choose between fairness and accuracy

```python
def exploit_fairness_accuracy_tradeoff(model, X, y, protected_attr):
    """
    Create scenarios where fairness and accuracy conflict
    """
    # Poison data to create conflict
    X_poison, y_poison = create_fairness_accuracy_conflict(
        X, y, protected_attr
    )
    
    # Defender must choose:
    # Option 1: High accuracy, low fairness
    # Option 2: High fairness, low accuracy
    # Option 3: Medium both (vulnerable to attacks)
    
    return X_poison, y_poison
```

## Detection and Defense

### Detection Techniques

#### 1. Comprehensive Fairness Auditing
```python
def comprehensive_fairness_audit(model, X, y, protected_attrs):
    """
    Test multiple fairness metrics
    Check intersectional fairness
    Analyze subgroup performance
    """
    results = {}
    
    # Test multiple metrics
    results['demographic_parity'] = test_demographic_parity(model, X, protected_attrs)
    results['equalized_odds'] = test_equalized_odds(model, X, y, protected_attrs)
    results['calibration'] = test_calibration(model, X, y, protected_attrs)
    
    # Check intersections
    results['intersectional'] = test_intersectional_fairness(
        model, X, y, protected_attrs
    )
    
    # Analyze subgroups
    results['subgroup_analysis'] = analyze_subgroups(model, X, y)
    
    return results
```

#### 2. Proxy Feature Detection
```python
def detect_proxy_features(X, protected_attr, threshold=0.7):
    """
    Identify features correlated with protected attributes
    """
    correlations = {}
    for feature in X.columns:
        corr = compute_correlation(X[feature], protected_attr)
        if abs(corr) > threshold:
            correlations[feature] = corr
    
    return correlations
```

#### 3. Bias Drift Monitoring
```python
def monitor_bias_drift(model, X_stream, protected_attr, window_size=1000):
    """
    Detect gradual bias introduction
    """
    fairness_history = []
    
    for window in sliding_window(X_stream, window_size):
        fairness_score = compute_fairness(model, window, protected_attr)
        fairness_history.append(fairness_score)
        
        # Detect drift
        if detect_drift(fairness_history):
            alert("Bias drift detected!")
    
    return fairness_history
```

### Defense Strategies

#### 1. Adversarial Debiasing
```python
def adversarial_debiasing(model, X, y, protected_attr):
    """
    Train model to be fair against adversarial attacks
    """
    # Adversarial training for fairness
    for epoch in range(num_epochs):
        # Generate fairness attacks
        X_adv, y_adv = generate_fairness_attack(X, y, protected_attr)
        
        # Train on both clean and adversarial
        model.train(X, y)
        model.train(X_adv, y_adv)
    
    return model
```

#### 2. Robust Fairness Metrics
```python
def robust_fairness_evaluation(model, X, y, protected_attr):
    """
    Evaluate fairness under adversarial conditions
    """
    # Test multiple metrics
    metrics = compute_all_fairness_metrics(model, X, y, protected_attr)
    
    # Test under perturbations
    for perturbation in generate_perturbations():
        X_pert = X + perturbation
        metrics_pert = compute_all_fairness_metrics(
            model, X_pert, y, protected_attr
        )
        
        # Check robustness
        if not is_robust(metrics, metrics_pert):
            return False, metrics_pert
    
    return True, metrics
```

#### 3. Fairness Certification
```python
def certify_fairness(model, X, protected_attr, epsilon):
    """
    Provide provable fairness guarantees
    """
    # Use randomized smoothing or other certification methods
    certified_radius = compute_certified_fairness_radius(
        model, X, protected_attr, epsilon
    )
    
    if certified_radius >= epsilon:
        return True, "Model is certifiably fair"
    else:
        return False, f"Only certified up to {certified_radius}"
```

## Case Studies

### Case 1: COMPAS Recidivism Prediction

**System**: Criminal risk assessment
**Bias**: Racial disparities in predictions
**Attack Vector**: Training data reflects historical bias
**Fairness Metric**: Calibration (satisfied)
**Reality**: Different false positive rates across races
**Lesson**: Single metric insufficient

### Case 2: Amazon Hiring AI

**System**: Resume screening
**Bias**: Gender discrimination
**Attack Vector**: Historical hiring data biased
**Proxy Features**: Words like "women's" in resume
**Result**: System scrapped
**Lesson**: Proxy features enable discrimination

### Case 3: Healthcare Risk Prediction

**System**: Patient risk scoring
**Bias**: Racial bias in cost-based labels
**Attack Vector**: Using healthcare cost as proxy for health
**Impact**: Underestimated risk for Black patients
**Lesson**: Label choice matters

## Practical Recommendations

### For Red Teams

1. **Test Multiple Metrics**: Don't rely on single fairness definition
2. **Check Intersections**: Test intersectional fairness
3. **Find Proxies**: Identify correlated features
4. **Temporal Testing**: Monitor bias over time
5. **Adversarial Fairness**: Test robustness of fairness

### For Defenders

1. **Comprehensive Auditing**: Use multiple fairness metrics
2. **Proxy Detection**: Monitor correlated features
3. **Continuous Monitoring**: Track fairness over time
4. **Adversarial Training**: Train against fairness attacks
5. **Certification**: Seek provable fairness guarantees

## Tools and Resources

### Fairness Libraries
- **AIF360** (IBM): Comprehensive fairness toolkit
- **Fairlearn** (Microsoft): Fairness assessment and mitigation
- **What-If Tool** (Google): Interactive fairness exploration
- **Fairness Indicators** (TensorFlow): Fairness metrics

### Research Papers
- "Fairness and Machine Learning" (Barocas et al., 2019)
- "Adversarial Attacks on Fairness" (Mehrabi et al., 2021)
- "Fairness Through Awareness" (Dwork et al., 2012)
- "On Fairness and Calibration" (Pleiss et al., 2017)

## Conclusion

Fairness in ML is not just an ethical imperative—it's a security concern. Adversaries can exploit fairness mechanisms, manipulate metrics, and weaponize bias. Red teams must understand these attacks to help build truly fair and secure systems.

### Key Takeaways

1. **Fairness ≠ Security**: But they're deeply connected
2. **Metrics Can Be Gamed**: Single metrics are insufficient
3. **Proxies Enable Bias**: Correlated features are dangerous
4. **Intersectionality Matters**: Check all subgroups
5. **Continuous Monitoring**: Bias can drift over time

## Next Steps

- Complete [Lab 5: Fairness Attacks](labs/lab2_fairness_attacks.ipynb)
- Read [Interpretability Security](05_interpretability_security.md)
- Practice comprehensive fairness auditing
- Develop robust fairness defenses
