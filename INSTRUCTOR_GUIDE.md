# Instructor Guide - Lab Answer Keys

## Overview

This guide provides locations and summaries of all lab exercise answer keys in the GenAI Red Teaming Training curriculum.

## Answer Guide Locations

**Format**: Each module has runnable Jupyter notebooks (`.ipynb`) with complete solutions.

**Benefits of Notebook Format**:
- Students can run code directly and see outputs
- Easy to experiment with parameters
- Better learning experience
- Can be used in Jupyter Lab, VS Code, or any notebook environment
- Includes explanations, code, and expected results in one place

### Module 1: Introduction & Foundations
**File**: `modules/01_introduction/labs/ANSWERS.ipynb`

**Exercises Covered**:
1. **Tokenization Exploration** - Compare 5 different tokenizers
2. **Temperature Analysis** - Measure output diversity at different temperatures
3. **Context Overflow** - Demonstrate context window limitations
4. **Instruction Injection** - Implement 3 prompt injection techniques

**Key Learning**: Students understand tokenization, model parameters, and basic injection attacks.

---

### Module 2: Prompt Injection & Jailbreaking
**File**: `modules/02_prompt_injection/labs/ANSWERS.ipynb`

**Exercises Covered**:
1. **Create Your Own Jailbreak** (Lab 2) - Design 4 jailbreak techniques
2. **Design Robust Guardrail** (Lab 3) - Multi-layer defense implementation
3. **Conversation-Level Defense** (Lab 4) - Detect multi-turn attacks

**Key Learning**: Students learn attack techniques and defense mechanisms for prompt injection.

---

### Module 3: Model Evasion
**File**: `modules/03_evasion/labs/ANSWERS.ipynb`

**Exercises Covered**:
1. **C&W Attack Implementation** (Lab 1) - Optimization-based evasion
2. **Targeted SimBA Attack** (Lab 2) - Black-box targeted attack
3. **Keyboard Typo Attack** (Lab 3) - Realistic text perturbations
4. **Semantic Similarity Optimization** (Lab 3) - Maintain meaning while attacking

**Key Learning**: Students implement both white-box and black-box evasion attacks.

---

### Module 4: Data Extraction & Privacy
**File**: `modules/04_data_extraction/labs/ANSWERS.ipynb`

**Exercises Covered**:
1. **Shadow Model Attack** (Lab 2) - Advanced membership inference
2. **Regularized Model Inversion** (Lab 3) - Realistic reconstruction

**Key Learning**: Students understand privacy attacks and their sophistication.

---

### Module 5: Model Poisoning
**File**: `modules/05_poisoning/labs/ANSWERS.ipynb`

**Exercises Covered**:
1. **Clean-Label Poisoning** (Lab 1) - Stealthy data poisoning
2. **Stealthy Backdoor** (Lab 2) - Hard-to-detect triggers
3. **Detect Poisoning** (Lab 3) - Detection methods
4. **Improve Detection** (Lab 4) - Combine multiple detectors

**Key Learning**: Students learn both attack and defense for poisoning.

---

### Module 7: Assessment & Testing
**File**: `modules/07_assessment/labs/ANSWERS.ipynb`

**Exercises Covered**:
1. **Compare Attack Recipes** (Lab 2) - TextAttack evaluation
2. **Explanation Robustness** (Lab 3) - Test Alibi on adversarial examples
3. **Extend Assessment Framework** (Lab 4) - Add privacy and fairness tests

**Key Learning**: Students build comprehensive security assessment pipelines.

---

### Module 9: Agent Security & Sub-Agent Operations
**File**: `modules/09_agent_security/labs/ANSWERS.ipynb`

**Exercises Covered**:
1. **Agent Orchestration Basics** (Lab 1) - LLM-driven planner/executor/reviewer workflow tracing
2. **Sub-Agent Attack Simulation** (Lab 2) - Indirect prompt injection and trust-boundary abuse
3. **Tool Argument Injection Defense** (Lab 3) - Path traversal and SQLi-style payload hardening
4. **Security Regression Suite** (Lab 4) - Memory poisoning persistence and threshold-based gating
5. **Advanced Delegation Attacks (Optional)** (Lab 5) - Supervisor/worker handoff trust and provenance validation

**Key Learning**: Students operationalize realistic agent security controls, attack simulation, and regression testing.

---

## Using the Answer Guides

### For Instructors

**Before Class**:
- Review answer guides for the module
- Identify common pitfalls
- Prepare additional examples if needed
- Set up demo environment

**During Class**:
- Let students attempt exercises first
- Provide hints without giving away solutions
- Use answer guides for live coding demonstrations
- Discuss alternative approaches

**After Class**:
- Share answer guides with students
- Encourage students to compare their solutions
- Discuss trade-offs and improvements
- Assign follow-up challenges

### For Students

**Recommended Approach**:
1. Attempt exercise independently first
2. If stuck, review relevant theory documents
3. Check answer guide for hints (not full solution)
4. Compare your solution with provided answer
5. Understand why the answer works
6. Try to improve or modify the solution

**Learning Tips**:
- Don't just copy the answers
- Understand each line of code
- Experiment with parameters
- Try on different models/data
- Document your findings

---

## Answer Guide Structure

Each answer includes:

1. **Task Description**: Clear statement of the exercise
2. **Complete Code**: Fully working implementation
3. **Explanation**: Key concepts and techniques
4. **Expected Results**: What output to expect
5. **Key Insights**: Learning takeaways
6. **Extensions**: Ideas for further exploration

---

## Grading Rubric (Suggested)

### Code Quality (40%)
- Correctness: Does it work?
- Completeness: All requirements met?
- Style: Clean, readable code?
- Documentation: Comments and explanations?

### Understanding (30%)
- Can explain how it works
- Understands trade-offs
- Identifies limitations
- Suggests improvements

### Experimentation (20%)
- Tried different parameters
- Tested on multiple cases
- Documented results
- Drew conclusions

### Creativity (10%)
- Novel approaches
- Interesting extensions
- Thoughtful analysis
- Original insights

---

## Common Student Questions

### "Can I use a different approach?"
**Answer**: Yes! The answer guides show one solution, but multiple approaches exist. As long as your solution meets the requirements and demonstrates understanding, it's valid.

### "My results don't match exactly"
**Answer**: That's normal! Random initialization, different hardware, and model versions can cause variations. Focus on whether the general pattern matches.

### "The attack didn't work"
**Answer**: Attacks don't always succeed. Document why it failed, what you tried, and what you learned. Failure analysis is valuable!

### "Can I use external libraries?"
**Answer**: Check with your instructor. Generally, using well-known libraries (scikit-learn, numpy) is fine, but the goal is to understand the concepts, not just call APIs.

---

## Additional Resources

### For Deeper Understanding
- Original research papers (linked in theory documents)
- OWASP LLM Top 10
- NIST AI Risk Management Framework
- Academic conferences (NeurIPS, ICML, ICLR)

### For Practical Skills
- Kaggle competitions
- CTF challenges
- Bug bounty programs
- Open source contributions

### For Staying Current
- ArXiv (cs.CR, cs.LG)
- Security conferences (DEF CON, Black Hat)
- AI safety forums
- Research blogs

---

## Instructor Notes

### Time Estimates
- Module 1 exercises: 2-3 hours
- Module 2 exercises: 3-4 hours
- Module 3 exercises: 4-5 hours
- Module 4 exercises: 3-4 hours
- Module 5 exercises: 4-5 hours
- Module 7 exercises: 3-4 hours

### Difficulty Levels
- Module 1: Beginner
- Module 2: Intermediate
- Module 3: Intermediate to Advanced
- Module 4: Advanced
- Module 5: Advanced
- Module 7: Advanced

### Prerequisites
Students should complete modules sequentially. Each module builds on previous concepts.

---

## Feedback and Improvements

### Collecting Feedback
- Student surveys after each module
- Code review sessions
- Office hours discussions
- Anonymous feedback forms

### Continuous Improvement
- Update answers based on common issues
- Add clarifications where students struggle
- Include more examples if needed
- Adjust difficulty based on cohort

---

## Contact

For questions about answer guides or teaching materials:
- Review module README files
- Check theory documents
- Consult with other instructors
- Contribute improvements via pull requests

---

**Last Updated**: December 2025
**Version**: 1.0
**Status**: Complete for Modules 1-5, 7, 9
