# GenAI Red Teaming Training

A comprehensive, self-paced training curriculum for security researchers focused on red teaming GenAI and AI/ML systems. This repository contains hands-on labs, theoretical content, and practical demonstrations of adversarial techniques.

## 🔴 What is GenAI Red Teaming?

**Red teaming for AI/ML goes far beyond traditional RAI (Responsible AI) testing.** While RAI focuses on fairness, bias, and ethical considerations, red teaming encompasses:

- **Adversarial Attacks**: Crafting inputs to fool models or extract sensitive information
- **Security Vulnerabilities**: Identifying exploitable weaknesses in AI systems
- **Privacy Breaches**: Testing for data leakage and membership inference
- **Model Manipulation**: Poisoning, backdoors, and supply chain attacks
- **Evasion Techniques**: Bypassing safety guardrails and content filters
- **System-Level Exploits**: Prompt injection, jailbreaking, and serialization attacks

This training teaches **offensive security techniques** for AI systems, the same methods attackers use, so you can better defend against them.

**New to AI Security?** Start with our companion resource: [GenAI Essentials - LLM Security Notebook](https://github.com/schwartz1375/genai-essentials/blob/main/llm_security.ipynb) for foundational concepts before diving into this advanced curriculum.

## 🎯 Target Audience

Security researchers with:
- Intermediate to advanced technical background
- Understanding of machine learning fundamentals
- Interest in AI/ML security and adversarial techniques

## 📚 Course Structure

The training is organized into sequential modules, each building upon previous concepts:

### Module 1: Introduction & Foundations
- Overview of AI/ML security landscape
- Understanding LLM architecture and vulnerabilities
- Setting up your red teaming environment
- Introduction to adversarial thinking

### Module 2: Prompt Injection & Jailbreaking
- Understanding prompt injection attacks
- Jailbreaking techniques and methodologies
- Defense mechanisms and their limitations
- Hands-on labs with real-world scenarios

### Module 3: Model Evasion Attacks
- White-box evasion techniques
- Black-box evasion strategies
- Adversarial example generation
- Practical exercises with various models

### Module 4: Data Extraction & Privacy
- Training data inference attacks
- Model inversion techniques
- Membership inference attacks
- Privacy-preserving defenses

### Module 5: Model Poisoning
- Training data poisoning
- Backdoor attacks
- Supply chain vulnerabilities
- Detection and mitigation strategies

### Module 6: Advanced LLM Attacks
- Model weight extraction
- Model distillation attacks
- Self-instruct data generation
- Serialization vulnerabilities

### Module 7: Assessment & Testing
- Comprehensive security assessment methodologies
- Automated testing frameworks
- Red team exercise scenarios
- Reporting and remediation

### Module 8: Final Assessment
- Capstone project
- Real-world scenario testing
- Comprehensive evaluation

### Module 9: Agent Security & Sub-Agent Operations
- Planner/executor/reviewer threat modeling
- Sub-agent attack simulation
- Tool policy enforcement
- Security regression testing for agent workflows

## 🛠️ Prerequisites

- Python 3.12+
- Basic understanding of machine learning
- Familiarity with Jupyter notebooks
- Access to GPU (recommended for some exercises)

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd genai-security-training

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation (Optional and note all packages)
python -c "import torch, transformers, numpy, pandas; print('✅ Ready!')"
```

**Note**: Installation takes 10-15 minutes. Labs that need additional packages (like `textattack`, `adversarial-robustness-toolbox`, etc.) will automatically install them when you run the notebook.

## 🚀 Getting Started

1. Start with Module 1 to understand the foundations
2. Progress sequentially through each module
3. Complete hands-on labs before moving to the next module
4. Reference materials are provided throughout
5. Final assessment tests comprehensive understanding

## 📖 Learning Path

Each module contains:
- **Theory**: Markdown documents explaining concepts
- **Labs**: Jupyter notebooks with hands-on exercises
- **References**: Links to papers, tools, and additional resources
- **Assessments**: Knowledge checks and practical exercises

## 🔗 Key Tools & Frameworks

This course uses industry-standard security testing tools:

### Adversarial Testing Frameworks
- **[Adversarial Robustness Toolbox (ART)](https://adversarial-robustness-toolbox.readthedocs.io/)** - IBM's comprehensive library for adversarial ML (Module 7)
- **[TextAttack](https://textattack.readthedocs.io/)** - NLP-focused adversarial attack framework (Modules 3, 7)
- **[SHAP](https://shap.readthedocs.io/)** - Model explainability and robustness testing (Module 7)

### Standards & Guidelines
- **[OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)** - Top vulnerabilities in LLM applications
- **[NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)** - AI risk assessment guidelines
- **[MITRE ATLAS](https://atlas.mitre.org/)** - Adversarial threat landscape for AI systems

### Companion Resources
- **[GenAI Essentials](https://github.com/schwartz1375/genai-essentials)** - Foundational GenAI concepts and security basics
- **[LLM Security Notebook](https://github.com/schwartz1375/genai-essentials/blob/main/llm_security.ipynb)** - Essential primer on LLM security concepts (recommended prerequisite)
- **[Artificial Diaries](https://github.com/schwartz1375/ArtificialDiaries)** - Research publications and case studies
- **GitHub**: [@schwartz1375](https://github.com/schwartz1375)

## ⚠️ Ethical Guidelines

This training is designed for:
- Security research and testing
- Defensive security improvements
- Educational purposes

**NOT for:**
- Malicious attacks on production systems
- Unauthorized testing
- Illegal activities

Always obtain proper authorization before testing any system.

## 📊 What's Included

- **8 Complete Modules** - Introduction through Capstone
- **40 Jupyter Notebooks** - Hands-on labs, interactive theory, and solutions
- **29 Theory & Documentation Files** - Comprehensive markdown guides and module overviews
- **Industry-Standard Tools** - Integrated ART, TextAttack, and SHAP frameworks in notebooks
- **Device Detection Code** - Built-in CUDA/Apple Silicon MPS/CPU detection in labs

**Note**: Labs include device detection code to automatically use your GPU (NVIDIA CUDA or Apple Silicon MPS) when available.

## 📖 Documentation & Resources

- **[QUICK_START.md](QUICK_START.md)** - Get started in 15 minutes
- **[INSTRUCTOR_GUIDE.md](INSTRUCTOR_GUIDE.md)** - Complete teaching guide with answer key locations and grading rubrics
- **Module ANSWERS.ipynb** - Runnable Jupyter notebooks with complete solutions (20+ exercises) in modules 1-5 and 7 labs folders
