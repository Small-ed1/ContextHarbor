import unittest
from agent.citation import CitationEngine
from agent.models import Source, SourceType
from datetime import datetime


class TestCitation(unittest.TestCase):
    """Test citation management and formatting"""

    def setUp(self):
        self.engine = CitationEngine()

    def test_add_source(self):
        """Test adding sources to citation engine"""
        source = Source(
            source_id="test_source",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test Title",
            locator="http://example.com",
            snippet="Test snippet",
            confidence=0.9
        )

        citation_id = self.engine.add_source(source)

        self.assertEqual(citation_id, 1)
        self.assertEqual(len(self.engine.sources), 1)

    def test_add_duplicate_source(self):
        """Test that duplicate sources get same citation ID"""
        source = Source(
            source_id="duplicate_id",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test",
            locator="http://example.com",
            snippet="snippet",
            confidence=0.9
        )

        id1 = self.engine.add_source(source)
        id2 = self.engine.add_source(source)

        self.assertEqual(id1, id2)
        self.assertEqual(len(self.engine.sources), 1)

    def test_add_multiple_sources(self):
        """Test adding multiple sources"""
        sources = [
            Source(
                source_id=f"src_{i}",
                tool="web_search",
                source_type=SourceType.WEB,
                title=f"Title {i}",
                locator=f"http://example.com/{i}",
                snippet=f"Snippet {i}",
                confidence=0.9
            )
            for i in range(5)
        ]

        for source in sources:
            self.engine.add_source(source)

        self.assertEqual(len(self.engine.sources), 5)
        self.assertEqual(self.engine.next_citation_index, 6)

    def test_format_citations_inline(self):
        """Test inline citation formatting"""
        source = Source(
            source_id="test_id",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test",
            locator="http://example.com",
            snippet="content",
            confidence=0.9
        )
        self.engine.add_source(source)

        text = "This is content with a citation"
        formatted = self.engine.format_citations(text, "inline")

        self.assertIn("[1]", formatted)

    def test_format_citations_footnotes(self):
        """Test footnote citation formatting"""
        source = Source(
            source_id="test_id",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test Title",
            locator="http://example.com",
            snippet="content",
            confidence=0.9
        )
        self.engine.add_source(source)

        text = "Content to cite"
        formatted = self.engine.format_citations(text, "footnotes")

        self.assertIn("[1]", formatted)

    def test_format_citations_links(self):
        """Test link citation formatting"""
        source = Source(
            source_id="test_id",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test Title",
            locator="http://example.com",
            snippet="content",
            confidence=0.9
        )
        self.engine.add_source(source)

        text = "Content"
        formatted = self.engine.format_citations(text, "links")

        self.assertIn("http://example.com", formatted)

    def test_get_source_by_citation(self):
        """Test retrieving source by citation ID"""
        source = Source(
            source_id="test_id",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test Title",
            locator="http://example.com",
            snippet="content",
            confidence=0.9
        )
        self.engine.add_source(source)

        retrieved = self.engine.get_source_by_citation(1)

        self.assertEqual(retrieved.source_id, "test_id")
        self.assertEqual(retrieved.title, "Test Title")

    def test_get_source_by_invalid_citation(self):
        """Test retrieving source with invalid citation ID"""
        retrieved = self.engine.get_source_by_citation(999)

        self.assertIsNone(retrieved)

    def test_clear_sources(self):
        """Test clearing all sources"""
        source = Source(
            source_id="test_id",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test",
            locator="http://example.com",
            snippet="content",
            confidence=0.9
        )
        self.engine.add_source(source)
        self.assertEqual(len(self.engine.sources), 1)

        self.engine.clear()

        self.assertEqual(len(self.engine.sources), 0)
        self.assertEqual(self.engine.next_citation_index, 1)

    def test_url_coverage_check(self):
        """Test URL coverage checking"""
        source1 = Source(
            source_id="src1",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test",
            locator="http://example.com/page",
            snippet="content",
            confidence=0.9
        )
        source2 = Source(
            source_id="src2",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test",
            locator="http://example.com/other",
            snippet="content",
            confidence=0.9
        )

        self.engine.add_source(source1)
        self.engine.add_source(source2)

        coverage = self.engine.check_url_coverage("http://example.com/page")
        self.assertTrue(coverage)

    def test_source_metadata_tracking(self):
        """Test that source metadata is tracked"""
        source = Source(
            source_id="test_id",
            tool="web_search",
            source_type=SourceType.WEB,
            title="Test Title",
            locator="http://example.com",
            snippet="content",
            confidence=0.8,
            retrieved_at=datetime.now()
        )
        self.engine.add_source(source)

        tracked = self.engine.sources[0]
        self.assertEqual(tracked.tool, "web_search")
        self.assertEqual(tracked.confidence, 0.8)
        self.assertIsNotNone(tracked.retrieved_at)


if __name__ == "__main__":
    unittest.main()
