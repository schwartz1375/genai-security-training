# Federated Learning Security

## Overview

Federated Learning (FL) enables collaborative model training across distributed devices without centralizing data. While this preserves privacy, it introduces unique security vulnerabilities. This document explores attacks and defenses in federated learning systems.

## Learning Objectives

- Understand federated learning architecture
- Execute Byzantine attacks on FL systems
- Perform gradient inversion attacks
- Implement Sybil attacks
- Design Byzantine-robust aggregation
- Apply differential privacy in FL

## Federated Learning Fundamentals

### Architecture

```
┌─────────────────────────────────────────┐
│         Central Server                   │
│  - Maintains global model                │
│  - Aggregates client updates             │
│  - Distributes model to clients          │
└─────────────────────────────────────────┘
         ↓                    ↑
    Broadcast            Aggregate
    Global Model         Local Updates
         ↓                    ↑
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Client 1 │  │ Client 2 │  │ Client N │
│ Local    │  │ Local    │  │ Local    │
│ Data     │  │ Data     │  │ Data     │
└──────────┘  └──────────┘  └──────────┘
```

### Standard FL Algorithm (FedAvg)

```python
# Server-side
def federated_averaging(client_models, client_weights):
    """
    Standard FedAvg algorithm
    """
    global_model = initialize_model()
    
    for round in range(num_rounds):
        # 1. Broadcast global model to clients
        for client in selected_clients:
            client.receive_model(global_model)
        
        # 2. Clients train locally
        client_updates = []
        for client in selected_clients:
            local_update = client.train_local()
            client_updates.append(local_update)
        
        # 3. Aggregate updates
        global_model = aggregate_updates(client_updates, client_weights)
    
    return global_model

def aggregate_updates(updates, weights):
    """
    Weighted average of client updates
    """
    aggregated = {}
    for key in updates[0].keys():
        aggregated[key] = sum(w * u[key] for w, u in zip(weights, updates))
    return aggregated
```

### FL Variants

**Horizontal FL**: Clients have same features, different samples
**Vertical FL**: Clients have different features, same samples
**Federated Transfer Learning**: Different features and samples



## Threat Model

### Adversary Capabilities

**Malicious Clients**:
- Control one or more clients
- Access to local data
- Can modify local updates
- Cannot access other clients' data

**Malicious Server**:
- Controls aggregation
- Sees all client updates
- Can modify global model
- Cannot access raw client data

**Honest-but-Curious**:
- Follows protocol
- Tries to infer information
- Passive attacks

### Attack Goals

1. **Model Poisoning**: Degrade global model performance
2. **Backdoor Injection**: Insert backdoor into global model
3. **Privacy Breach**: Extract client data from updates
4. **Targeted Attack**: Misclassify specific inputs
5. **Denial of Service**: Prevent convergence

## Byzantine Attacks

### Attack 1: Model Poisoning

**Concept**: Malicious clients send corrupted updates to degrade model

```python
class MaliciousClient:
    """
    Client that sends poisoned updates
    """
    def __init__(self, attack_type='random'):
        self.attack_type = attack_type
    
    def train_local(self, global_model, local_data):
        """
        Train locally but return poisoned update
        """
        # Normal training
        local_model = global_model.copy()
        local_model.train(local_data)
        
        # Poison the update
        if self.attack_type == 'random':
            # Random noise
            poisoned_update = self.add_random_noise(local_model)
        elif self.attack_type == 'sign_flip':
            # Flip gradient signs
            poisoned_update = self.flip_signs(local_model)
        elif self.attack_type == 'scaled':
            # Scale up malicious update
            poisoned_update = self.scale_update(local_model, scale=10)
        
        return poisoned_update
    
    def add_random_noise(self, model):
        """Add random noise to model parameters"""
        poisoned = {}
        for key, param in model.items():
            poisoned[key] = param + np.random.normal(0, 1, param.shape)
        return poisoned
    
    def flip_signs(self, model):
        """Flip signs of all parameters"""
        poisoned = {}
        for key, param in model.items():
            poisoned[key] = -param
        return poisoned
    
    def scale_update(self, model, scale=10):
        """Scale update to dominate aggregation"""
        poisoned = {}
        for key, param in model.items():
            poisoned[key] = param * scale
        return poisoned
```

**Impact**:
- Degraded model accuracy
- Slower convergence
- Potential model failure

### Attack 2: Targeted Backdoor Injection

**Concept**: Insert backdoor that activates on specific trigger

```python
def backdoor_federated_learning(global_model, local_data, 
                                  trigger, target_class):
    """
    Train model with backdoor
    """
    # Add backdoor samples to local data
    backdoor_data = []
    for x, y in local_data:
        # Add trigger to input
        x_backdoor = add_trigger(x, trigger)
        # Change label to target
        backdoor_data.append((x_backdoor, target_class))
    
    # Combine clean and backdoor data
    poisoned_data = local_data + backdoor_data
    
    # Train on poisoned data
    local_model = global_model.copy()
    local_model.train(poisoned_data)
    
    return local_model

def add_trigger(x, trigger):
    """
    Add backdoor trigger to input
    """
    x_triggered = x.copy()
    # Example: Add pattern to corner
    x_triggered[0:5, 0:5] = trigger
    return x_triggered
```

**Stealthy Backdoor**:
```python
def semantic_backdoor_fl(global_model, local_data):
    """
    Use semantic trigger (e.g., wearing glasses)
    """
    # Find samples with semantic feature
    triggered_samples = find_samples_with_feature(local_data, 'glasses')
    
    # Relabel to target class
    poisoned_data = []
    for x, y in triggered_samples:
        poisoned_data.append((x, target_class))
    
    # Train with poisoned data
    local_model = global_model.copy()
    local_model.train(local_data + poisoned_data)
    
    return local_model
```

### Attack 3: Sybil Attack

**Concept**: Attacker controls multiple fake clients

```python
class SybilAttacker:
    """
    Attacker controlling multiple clients
    """
    def __init__(self, num_sybils=10):
        self.num_sybils = num_sybils
        self.sybil_clients = [MaliciousClient() for _ in range(num_sybils)]
    
    def coordinate_attack(self, global_model):
        """
        Coordinate attack across Sybil clients
        """
        # All Sybils send same malicious update
        malicious_update = self.craft_malicious_update(global_model)
        
        updates = []
        for _ in range(self.num_sybils):
            # Add small noise to avoid detection
            noisy_update = add_noise(malicious_update, noise_level=0.01)
            updates.append(noisy_update)
        
        return updates
    
    def craft_malicious_update(self, global_model):
        """
        Craft update to maximize damage
        """
        # Optimize to maximize loss on validation set
        malicious_update = optimize_for_max_loss(global_model)
        return malicious_update
```

**Impact**:
- Amplified attack effect
- Harder to detect (distributed)
- Can overwhelm honest clients

### Attack 4: Model Replacement

**Concept**: Replace global model entirely

```python
def model_replacement_attack(global_model, attacker_model, 
                              num_malicious, num_total):
    """
    Replace global model with attacker's model
    """
    # Scale attacker model to dominate aggregation
    # If aggregation is average: scale by (num_total / num_malicious)
    scale_factor = num_total / num_malicious
    
    scaled_update = {}
    for key in attacker_model.keys():
        # Compute update from global to attacker model
        update = attacker_model[key] - global_model[key]
        # Scale to dominate
        scaled_update[key] = global_model[key] + scale_factor * update
    
    return scaled_update
```

## Privacy Attacks

### Attack 5: Gradient Inversion

**Concept**: Reconstruct training data from gradients

```python
def gradient_inversion_attack(gradients, model, num_iterations=1000):
    """
    Reconstruct training data from gradients
    
    Reference: "Deep Leakage from Gradients" (Zhu et al., 2019)
    """
    # Initialize dummy data and label
    dummy_data = torch.randn(batch_size, *input_shape, requires_grad=True)
    dummy_label = torch.randn(batch_size, num_classes, requires_grad=True)
    
    optimizer = torch.optim.LBFGS([dummy_data, dummy_label])
    
    for iteration in range(num_iterations):
        def closure():
            optimizer.zero_grad()
            
            # Compute gradients on dummy data
            dummy_pred = model(dummy_data)
            dummy_loss = criterion(dummy_pred, dummy_label)
            dummy_gradients = torch.autograd.grad(
                dummy_loss, model.parameters(), create_graph=True
            )
            
            # Match gradients
            grad_diff = 0
            for dummy_grad, real_grad in zip(dummy_gradients, gradients):
                grad_diff += ((dummy_grad - real_grad) ** 2).sum()
            
            grad_diff.backward()
            return grad_diff
        
        optimizer.step(closure)
    
    return dummy_data.detach(), dummy_label.detach()
```

**Improved Attack (iDLG)**:
```python
def improved_gradient_inversion(gradients, model):
    """
    Improved Deep Leakage from Gradients
    
    Reference: "iDLG: Improved Deep Leakage from Gradients" (Zhao et al., 2020)
    """
    # Extract label from gradient of last layer
    last_layer_gradient = gradients[-1]  # Gradient of output layer
    
    # Label is argmin of gradient (for cross-entropy loss)
    reconstructed_label = torch.argmin(last_layer_gradient, dim=-1)
    
    # Now reconstruct data with known label
    dummy_data = torch.randn(batch_size, *input_shape, requires_grad=True)
    optimizer = torch.optim.LBFGS([dummy_data])
    
    for iteration in range(num_iterations):
        def closure():
            optimizer.zero_grad()
            dummy_pred = model(dummy_data)
            dummy_loss = criterion(dummy_pred, reconstructed_label)
            dummy_gradients = torch.autograd.grad(
                dummy_loss, model.parameters(), create_graph=True
            )
            
            grad_diff = sum(
                ((dg - rg) ** 2).sum() 
                for dg, rg in zip(dummy_gradients, gradients)
            )
            grad_diff.backward()
            return grad_diff
        
        optimizer.step(closure)
    
    return dummy_data.detach(), reconstructed_label
```

### Attack 6: Membership Inference in FL

**Concept**: Determine if specific sample was in client's training data

```python
def membership_inference_fl(target_sample, client_updates, global_model):
    """
    Infer if target sample was in client's training data
    """
    # Compute loss on target sample
    loss_on_target = compute_loss(global_model, target_sample)
    
    # Analyze client updates
    membership_scores = []
    for client_update in client_updates:
        # Check if update reduces loss on target
        updated_model = apply_update(global_model, client_update)
        new_loss = compute_loss(updated_model, target_sample)
        
        # Large loss reduction indicates membership
        loss_reduction = loss_on_target - new_loss
        membership_scores.append(loss_reduction)
    
    # Client with highest loss reduction likely has target
    suspected_client = np.argmax(membership_scores)
    confidence = membership_scores[suspected_client]
    
    return suspected_client, confidence
```

### Attack 7: Property Inference

**Concept**: Infer properties of client's data distribution

```python
def property_inference_fl(client_updates, property_classifier):
    """
    Infer properties of client data from updates
    
    Example: Infer if client data contains specific demographic
    """
    # Extract features from client update
    update_features = extract_features(client_updates)
    
    # Use meta-classifier to infer property
    # Trained on: (update features) -> (data property)
    inferred_property = property_classifier.predict(update_features)
    
    return inferred_property

def train_property_classifier():
    """
    Train classifier to infer data properties from updates
    """
    # Collect training data
    training_data = []
    for data_property in properties:
        # Generate synthetic data with property
        synthetic_data = generate_data_with_property(data_property)
        
        # Train model and get update
        update = train_and_get_update(synthetic_data)
        
        # Extract features
        features = extract_features(update)
        training_data.append((features, data_property))
    
    # Train classifier
    classifier = train_classifier(training_data)
    return classifier
```

## Defenses

### Defense 1: Byzantine-Robust Aggregation

**Krum Algorithm**:
```python
def krum_aggregation(client_updates, num_malicious):
    """
    Krum: Select update closest to others
    
    Reference: "Machine Learning with Adversaries: Byzantine Tolerant 
                Gradient Descent" (Blanchard et al., 2017)
    """
    n = len(client_updates)
    m = num_malicious
    
    # Compute pairwise distances
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            dist = compute_distance(client_updates[i], client_updates[j])
            distances[i, j] = dist
            distances[j, i] = dist
    
    # For each update, sum distances to n-m-2 closest updates
    scores = []
    for i in range(n):
        sorted_distances = np.sort(distances[i])
        score = np.sum(sorted_distances[:n-m-2])
        scores.append(score)
    
    # Select update with minimum score
    selected_idx = np.argmin(scores)
    return client_updates[selected_idx]
```

**Trimmed Mean**:
```python
def trimmed_mean_aggregation(client_updates, trim_ratio=0.1):
    """
    Remove extreme values before averaging
    """
    aggregated = {}
    
    for key in client_updates[0].keys():
        # Stack all client values for this parameter
        values = np.array([update[key] for update in client_updates])
        
        # Trim extreme values
        num_trim = int(len(values) * trim_ratio)
        trimmed_values = []
        
        # Trim for each parameter element
        for i in range(values.shape[1]):
            param_values = values[:, i]
            sorted_values = np.sort(param_values)
            # Remove top and bottom trim_ratio
            trimmed = sorted_values[num_trim:-num_trim]
            trimmed_values.append(np.mean(trimmed))
        
        aggregated[key] = np.array(trimmed_values)
    
    return aggregated
```

**Median Aggregation**:
```python
def median_aggregation(client_updates):
    """
    Use coordinate-wise median
    """
    aggregated = {}
    
    for key in client_updates[0].keys():
        values = np.array([update[key] for update in client_updates])
        # Coordinate-wise median
        aggregated[key] = np.median(values, axis=0)
    
    return aggregated
```

### Defense 2: Secure Aggregation

**Concept**: Aggregate without server seeing individual updates

```python
def secure_aggregation_protocol(client_updates):
    """
    Secure aggregation using secret sharing
    
    Reference: "Practical Secure Aggregation for Privacy-Preserving 
                Machine Learning" (Bonawitz et al., 2017)
    """
    num_clients = len(client_updates)
    
    # Phase 1: Clients generate pairwise shared secrets
    shared_secrets = generate_pairwise_secrets(num_clients)
    
    # Phase 2: Clients mask their updates
    masked_updates = []
    for i, update in enumerate(client_updates):
        mask = compute_mask(shared_secrets[i])
        masked_update = update + mask
        masked_updates.append(masked_update)
    
    # Phase 3: Server aggregates masked updates
    aggregated_masked = sum(masked_updates)
    
    # Phase 4: Masks cancel out (sum of pairwise secrets = 0)
    # Result: sum of original updates without server seeing individuals
    return aggregated_masked

def generate_pairwise_secrets(num_clients):
    """
    Generate shared secrets between client pairs
    """
    secrets = {}
    for i in range(num_clients):
        secrets[i] = {}
        for j in range(num_clients):
            if i < j:
                # Generate shared secret
                secret = generate_random_secret()
                secrets[i][j] = secret
                secrets[j][i] = -secret  # Negative for cancellation
    return secrets
```

### Defense 3: Differential Privacy in FL

**Client-Level DP**:
```python
def dp_federated_learning(client_updates, epsilon, delta):
    """
    Add differential privacy to federated learning
    """
    # Clip client updates
    clipped_updates = []
    clip_norm = compute_clip_norm(epsilon, delta)
    
    for update in client_updates:
        # Clip update to bound sensitivity
        norm = compute_norm(update)
        if norm > clip_norm:
            clipped = {k: v * clip_norm / norm for k, v in update.items()}
        else:
            clipped = update
        clipped_updates.append(clipped)
    
    # Aggregate clipped updates
    aggregated = aggregate_updates(clipped_updates)
    
    # Add Gaussian noise
    noise_scale = compute_noise_scale(clip_norm, epsilon, delta)
    noisy_aggregated = {}
    for key, value in aggregated.items():
        noise = np.random.normal(0, noise_scale, value.shape)
        noisy_aggregated[key] = value + noise
    
    return noisy_aggregated
```

**Local DP**:
```python
def local_dp_client_update(local_model, epsilon):
    """
    Client adds noise before sending update
    """
    # Clip local update
    clipped_model = clip_model(local_model, clip_norm)
    
    # Add local noise
    noise_scale = clip_norm / epsilon
    noisy_model = {}
    for key, value in clipped_model.items():
        noise = np.random.laplace(0, noise_scale, value.shape)
        noisy_model[key] = value + noise
    
    return noisy_model
```

### Defense 4: Anomaly Detection

**Statistical Detection**:
```python
def detect_malicious_updates(client_updates, threshold=3.0):
    """
    Detect outlier updates using statistical methods
    """
    # Compute pairwise similarities
    similarities = compute_pairwise_similarities(client_updates)
    
    # Compute average similarity for each client
    avg_similarities = np.mean(similarities, axis=1)
    
    # Detect outliers (low similarity)
    mean_sim = np.mean(avg_similarities)
    std_sim = np.std(avg_similarities)
    
    malicious_clients = []
    for i, sim in enumerate(avg_similarities):
        if sim < mean_sim - threshold * std_sim:
            malicious_clients.append(i)
    
    return malicious_clients

def compute_pairwise_similarities(updates):
    """
    Compute cosine similarity between updates
    """
    n = len(updates)
    similarities = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i+1, n):
            sim = cosine_similarity(
                flatten_model(updates[i]),
                flatten_model(updates[j])
            )
            similarities[i, j] = sim
            similarities[j, i] = sim
    
    return similarities
```

**Learning-Based Detection**:
```python
def train_malicious_update_detector():
    """
    Train ML model to detect malicious updates
    """
    # Collect training data
    benign_updates = collect_benign_updates()
    malicious_updates = generate_malicious_updates()
    
    # Extract features
    benign_features = [extract_features(u) for u in benign_updates]
    malicious_features = [extract_features(u) for u in malicious_updates]
    
    # Train classifier
    X = benign_features + malicious_features
    y = [0] * len(benign_features) + [1] * len(malicious_features)
    
    detector = train_classifier(X, y)
    return detector

def extract_features(update):
    """
    Extract features from client update
    """
    features = {
        'norm': compute_norm(update),
        'sparsity': compute_sparsity(update),
        'mean': compute_mean(update),
        'std': compute_std(update),
        'max': compute_max(update),
        'min': compute_min(update),
    }
    return features
```

### Defense 5: Reputation Systems

```python
class ReputationSystem:
    """
    Track client reputation over time
    """
    def __init__(self, num_clients):
        self.reputations = np.ones(num_clients)  # Start with neutral reputation
        self.history = [[] for _ in range(num_clients)]
    
    def update_reputation(self, client_id, update, global_model, validation_data):
        """
        Update client reputation based on update quality
        """
        # Test update on validation data
        test_model = apply_update(global_model, update)
        accuracy = evaluate_model(test_model, validation_data)
        
        # Update reputation
        if accuracy > baseline_accuracy:
            self.reputations[client_id] *= 1.1  # Increase reputation
        else:
            self.reputations[client_id] *= 0.9  # Decrease reputation
        
        # Clip reputation
        self.reputations[client_id] = np.clip(
            self.reputations[client_id], 0.1, 2.0
        )
        
        self.history[client_id].append(accuracy)
    
    def get_client_weights(self):
        """
        Get aggregation weights based on reputation
        """
        # Normalize reputations to sum to 1
        weights = self.reputations / np.sum(self.reputations)
        return weights
    
    def select_clients(self, num_select):
        """
        Select clients with highest reputation
        """
        top_clients = np.argsort(self.reputations)[-num_select:]
        return top_clients
```

## Advanced Topics

### Cross-Silo vs Cross-Device FL

**Cross-Silo** (Few reliable clients):
```python
# Example: Hospitals collaborating
# - Few clients (10-100)
# - Reliable connections
# - Larger datasets per client
# - Can use complex aggregation
```

**Cross-Device** (Many unreliable clients):
```python
# Example: Mobile phones
# - Many clients (millions)
# - Unreliable connections
# - Small datasets per client
# - Need simple, robust aggregation
```

### Personalized FL

```python
def personalized_federated_learning(global_model, local_data):
    """
    Combine global and local models
    """
    # Train local model
    local_model = global_model.copy()
    local_model.train(local_data)
    
    # Combine global and local
    personalized_model = {}
    for key in global_model.keys():
        # Weighted combination
        personalized_model[key] = (
            alpha * global_model[key] + 
            (1 - alpha) * local_model[key]
        )
    
    return personalized_model
```

### Asynchronous FL

```python
def asynchronous_federated_learning():
    """
    Don't wait for all clients
    """
    global_model = initialize_model()
    
    while not converged:
        # Accept updates as they arrive
        if update_available():
            client_update = receive_update()
            
            # Apply update immediately
            global_model = apply_update(global_model, client_update)
            
            # Send updated model back
            broadcast_model(global_model)
```

## Practical Considerations

### Communication Efficiency

```python
def compressed_federated_learning(client_update, compression_ratio=0.1):
    """
    Compress updates to reduce communication
    """
    # Sparsification: Send only top-k gradients
    flattened = flatten_model(client_update)
    k = int(len(flattened) * compression_ratio)
    top_k_indices = np.argsort(np.abs(flattened))[-k:]
    
    sparse_update = {
        'indices': top_k_indices,
        'values': flattened[top_k_indices]
    }
    
    return sparse_update

def quantized_federated_learning(client_update, num_bits=8):
    """
    Quantize updates to reduce communication
    """
    quantized = {}
    for key, value in client_update.items():
        # Quantize to num_bits
        min_val, max_val = value.min(), value.max()
        scale = (max_val - min_val) / (2**num_bits - 1)
        quantized_value = np.round((value - min_val) / scale).astype(int)
        
        quantized[key] = {
            'values': quantized_value,
            'scale': scale,
            'min': min_val
        }
    
    return quantized
```

### Client Selection

```python
def smart_client_selection(clients, num_select):
    """
    Select diverse, high-quality clients
    """
    # Consider multiple factors
    scores = []
    for client in clients:
        score = (
            0.4 * client.data_quality +
            0.3 * client.data_diversity +
            0.2 * client.reputation +
            0.1 * client.computational_power
        )
        scores.append(score)
    
    # Select top clients
    selected_indices = np.argsort(scores)[-num_select:]
    return [clients[i] for i in selected_indices]
```

## Case Studies

### Case 1: Google Gboard (2017)

**Application**: Next-word prediction on mobile keyboards

**Approach**:
- Cross-device FL with millions of phones
- Secure aggregation for privacy
- Differential privacy
- Communication-efficient updates

**Security Measures**:
- Client-level DP
- Secure aggregation
- Anomaly detection
- Rate limiting

### Case 2: Healthcare FL (2020)

**Application**: Disease prediction across hospitals

**Challenges**:
- Highly sensitive data
- Regulatory compliance (HIPAA)
- Malicious hospitals possible
- Data heterogeneity

**Security Measures**:
- Byzantine-robust aggregation (Krum)
- Differential privacy
- Secure multi-party computation
- Audit logs

### Case 3: Financial Fraud Detection (2021)

**Application**: Fraud detection across banks

**Attack**: Malicious bank injects backdoor

**Defense**:
- Reputation system
- Validation on holdout data
- Multi-round anomaly detection
- Backdoor detection via interpretability

## Tools and Frameworks

### FL Frameworks

```python
# PySyft
import syft as sy
hook = sy.TorchHook(torch)
bob = sy.VirtualWorker(hook, id="bob")
alice = sy.VirtualWorker(hook, id="alice")

# TensorFlow Federated
import tensorflow_federated as tff
federated_data = [data1, data2, data3]
federated_averaging = tff.learning.build_federated_averaging_process(model_fn)

# Flower
import flwr as fl
fl.client.start_numpy_client(server_address="localhost:8080", client=MyClient())

# FedML
from FedML import FedMLRunner
runner = FedMLRunner(args)
runner.run()
```

## Summary

### Key Takeaways

1. **Unique Threat Model**: FL has different security challenges than centralized ML
2. **Byzantine Attacks**: Malicious clients can poison global model
3. **Privacy Attacks**: Gradients leak information about training data
4. **Robust Aggregation**: Essential defense against Byzantine attacks
5. **Differential Privacy**: Protects against privacy attacks but reduces utility

### Best Practices

**For FL System Designers**:
- Use Byzantine-robust aggregation
- Implement secure aggregation
- Add differential privacy
- Monitor for anomalies
- Validate on holdout data

**For Red Teamers**:
- Test Byzantine attacks
- Attempt gradient inversion
- Try Sybil attacks
- Evaluate privacy leakage
- Assess defense robustness

## References

### Key Papers

1. "Communication-Efficient Learning of Deep Networks from Decentralized Data" (McMahan et al., 2017) - FedAvg
2. "Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent" (Blanchard et al., 2017) - Krum
3. "Practical Secure Aggregation for Privacy-Preserving Machine Learning" (Bonawitz et al., 2017)
4. "Deep Leakage from Gradients" (Zhu et al., 2019)
5. "Analyzing Federated Learning through an Adversarial Lens" (Bhagoji et al., 2019)

### Resources

- [TensorFlow Federated](https://www.tensorflow.org/federated)
- [PySyft](https://github.com/OpenMined/PySyft)
- [Flower](https://flower.dev/)
- [FedML](https://fedml.ai/)

## Next Steps

1. Complete [Lab 4: Federated Learning Attacks](labs/lab4_federated_attacks.ipynb)
2. Implement Byzantine attacks
3. Test robust aggregation methods
4. Experiment with secure aggregation
5. Study differential privacy in FL

---

**Difficulty**: ⭐⭐⭐⭐⭐ Expert Level
**Prerequisites**: Distributed systems, cryptography basics, optimization
**Estimated Time**: 4-5 hours
