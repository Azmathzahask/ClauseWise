# ClauseWise: AI-Powered Legal Document Analyzer

ClauseWise is an AI-powered legal document analyzer designed to simplify the process of analyzing legal texts. This project leverages advanced natural language processing techniques to provide functionalities such as clause simplification, named entity recognition, clause extraction, and document classification.

## Features

- **Clause Simplification**: Automatically simplifies complex legal clauses for better understanding.
- **Named Entity Recognition**: Identifies and categorizes key entities within legal documents.
- **Clause Extraction**: Extracts relevant clauses from lengthy documents for quick reference.
- **Document Classification**: Classifies documents based on their content and structure.

## Installation

To install the necessary dependencies, run the following command:

```
pip install -r requirements.txt
```

## Usage

After installing the dependencies, you can start using the analyzer by importing the `analyzer` module in your Python scripts. Here’s a simple example:

```python
from clausewise.analyzer import analyze_document

result = analyze_document("path/to/legal/document.pdf")
print(result)
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.