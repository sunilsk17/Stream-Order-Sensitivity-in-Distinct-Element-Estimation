# Contributing to Stream Order Sensitivity Research

Thank you for your interest in contributing! This project welcomes contributions from the research community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Create a branch** for your feature/fix

## Development Workflow

### Setting Up Your Environment

```bash
# Clone the repository
git clone https://github.com/sunilsk17/Stream-Order-Sensitivity-in-Distinct-Element-Estimation.git
cd distinct-order-study

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run the main experiments
python experiments/synthetic_correlation_analysis.py
python experiments/real_data_convergence_analysis.py
python experiments/zipfian_distribution_analysis.py
```

### Code Style

- Follow PEP 8 conventions
- Use meaningful variable and function names
- Include docstrings for all functions
- Add comments for complex logic

### Testing Your Changes

Before submitting a pull request:

1. Ensure all experiments run without errors
2. Verify output files are generated correctly
3. Check that results are reproducible

## Types of Contributions

### Bug Reports

Submit an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS)

### Feature Requests

Propose features with:
- Clear description of the feature
- Use case and motivation
- Potential implementation approach

### Code Contributions

For code changes:
1. Keep changes focused and minimal
2. Update relevant documentation
3. Add docstrings to new functions
4. Test thoroughly before submitting

### Documentation Improvements

Documentation contributions are always welcome:
- Clarify existing documentation
- Add examples or tutorials
- Fix typos or errors
- Improve code comments

## Pull Request Process

1. **Update documentation** if needed
2. **Test your changes** thoroughly
3. **Write a clear PR description** explaining what changed and why
4. **Reference any related issues** using `#issue-number`
5. **Ensure clean commit history** with descriptive messages

## Research Contribution Guidelines

If you're extending the research:

1. **Maintain reproducibility** - Document data sources and methodology
2. **Use the same datasets** - Ensure comparability with original findings
3. **Document new experiments** - Provide clear setup and interpretation instructions
4. **Cite sources** - Include proper attribution for any external work

## Code of Conduct

This project is committed to providing a welcoming and inspiring community. All contributors are expected to:

- Be respectful and constructive
- Welcome diverse perspectives
- Focus on what is best for the research community
- Show empathy towards others

Unacceptable behavior includes: harassment, discrimination, disrespectful comments, or any form of abuse.

## Questions?

- Open an issue for questions about the code
- Check existing issues and documentation first
- Reference relevant sections of the README or papers

## Recognition

Contributors will be recognized in:
- The repository's contributor list
- Project documentation if appropriate
- Publications based on contributed work (as agreed upon)

## License

By contributing, you agree that your contributions will be licensed under the same MIT License as the project.

Thank you for contributing to advancing research in cardinality estimation and stream processing!
