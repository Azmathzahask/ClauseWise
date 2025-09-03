import unittest
from clausewise.analyzer import analyze_document, simplify_clause, extract_clauses

class TestAnalyzer(unittest.TestCase):

    def test_analyze_document(self):
        # Test the analyze_document function with a sample document
        document = "Sample legal document text."
        result = analyze_document(document)
        self.assertIsInstance(result, dict)  # Assuming the result is a dictionary

    def test_simplify_clause(self):
        # Test the simplify_clause function with a sample clause
        clause = "This is a complex legal clause."
        simplified = simplify_clause(clause)
        self.assertIsInstance(simplified, str)  # Assuming the result is a string

    def test_extract_clauses(self):
        # Test the extract_clauses function with a sample document
        document = "This is a legal document. Clause 1: ... Clause 2: ..."
        clauses = extract_clauses(document)
        self.assertIsInstance(clauses, list)  # Assuming the result is a list
        self.assertGreater(len(clauses), 0)  # Ensure at least one clause is extracted

if __name__ == '__main__':
    unittest.main()