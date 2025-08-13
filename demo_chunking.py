"""
Demo script to show how markdown chunking works
"""

from app.utils.preprocessing import split_markdown_into_chunks


def demo_chunking():
    """Demonstrate the markdown chunking functionality"""

    # Sample large markdown content
    large_markdown = """
    # Breaking News: Major Technology Breakthrough
    
    ## Technology News
    A revolutionary new development in artificial intelligence has been announced today. 
    Researchers have developed a more efficient algorithm for natural language processing.
    This development could fundamentally change how we interact with computers and AI systems.
    The breakthrough was achieved through innovative neural network architectures.
    
    ## Business Update
    The stock market showed positive trends this week, with technology stocks leading the gains.
    Major tech companies reported strong quarterly earnings, driving market optimism.
    Analysts predict continued growth in the technology sector throughout the year.
    Investment in AI and machine learning companies has increased significantly.
    
    ## Sports News
    The local football team won their match yesterday with a score of 3-1.
    The victory puts them in a strong position for the championship.
    Fans celebrated throughout the city after the win.
    The team's performance has been consistently improving this season.
    
    ## Health Update
    New health guidelines have been released by the health department.
    The guidelines focus on preventive care and early detection.
    Experts recommend regular check-ups and healthy lifestyle choices.
    These guidelines are based on the latest medical research findings.
    
    ## Entertainment
    A new movie has broken box office records this weekend.
    The film received critical acclaim and audience approval.
    Industry experts are calling it a game-changer for the genre.
    The success has led to discussions about sequels and spin-offs.
    
    ## Science News
    Scientists have discovered a new species of marine life in the Pacific Ocean.
    The discovery was made during a deep-sea exploration mission.
    Researchers believe this could lead to new insights into ocean ecosystems.
    The species shows unique adaptations to extreme pressure conditions.
    
    ## Education
    New educational programs have been launched to improve digital literacy.
    The programs target students from all age groups and backgrounds.
    Technology companies are partnering with schools to provide resources.
    Early results show significant improvement in digital skills.
    """

    print("Demo: Markdown Chunking with Mistral AI (3000 char chunks)")
    print("=" * 60)
    print(f"Original content length: {len(large_markdown)} characters")
    print()

    # Split into chunks
    chunks = split_markdown_into_chunks(large_markdown, chunk_size=3000)

    print(f"Content split into {len(chunks)} chunks (3000 char limit):")
    print(f"Will process first chunk with Mistral AI for reliable JSON output")
    print("-" * 50)

    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}: {len(chunk)} characters")
        print(f"Preview: {chunk[:100]}...")
        print()

    # Show what the first chunk looks like
    print("First chunk content (for processing):")
    print("=" * 50)
    print(chunks[0])
    print("=" * 50)


if __name__ == "__main__":
    demo_chunking()
