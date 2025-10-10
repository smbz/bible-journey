#!/usr/bin/env python3
"""
Parse BSB (Berean Standard Bible) text and generate JavaScript data files
with manually defined paragraph structures.
"""

import urllib.request
import json
import re
import sys

global in_dialogue
in_dialogue = False

# Book configurations
BOOK_CONFIGS = {
    'mark': {
        'full_name': 'Gospel of Mark',
        'short_name': 'Mark',
        'start_pattern': r'^Mark 1:1',
        'end_pattern': r'^(Luke|Acts) 1:1',
        'chapters': 16,
        'paragraph_structure': {
            # Each list contains ONLY the first verse of each paragraph
            # Consecutive verses are automatically filled in up to the next paragraph start
            1: [1, 4, 7, 9, 12, 14, 16, 19, 21, 29, 32, 35, 40],
            2: [1, 6, 13, 15, 18, 21, 23],
            3: [1, 7, 13, 20, 22, 28, 31],
            4: [1, 3, 10, 13, 21, 26, 30, 33, 35],
            5: [1, 6, 11, 14, 18, 21, 25, 30, 35],
            6: [1, 7, 14, 17, 21, 30, 33, 35, 45, 53],
            7: [1, 6, 14, 17, 24, 27, 31],
            8: [1, 11, 14, 22, 27, 31, 34],
            9: [1, 2, 9, 11, 14, 30, 33, 38, 41, 43],
            10: [1, 13, 17, 23, 28, 32, 35, 41, 46],
            11: [1, 8, 12, 15, 20, 27],
            12: [1, 13, 18, 28, 35, 38, 41],
            13: [1, 3, 9, 14, 21, 24, 28, 32],
            14: [1, 3, 10, 12, 17, 22, 27, 32, 43, 53, 66],
            15: [1, 6, 16, 21, 28, 33, 40, 42],
            16: [1, 9, 12, 14, 19]
        }
    },
    'luke': {
        'full_name': 'Gospel of Luke',
        'short_name': 'Luke',
        'start_pattern': r'^Luke 1:1',
        'end_pattern': r'^John 1:1',
        'chapters': 24,
        'paragraph_structure': {
            # Each list contains ONLY the first verse of each paragraph
            # Consecutive verses are automatically filled in up to the next paragraph start
            1: [1, 5, 8, 11, 14, 18, 21, 24, 26, 29, 34, 39, 42, 46, 56, 57, 59, 65, 67, 80],
            2: [1, 4, 6, 8, 10, 13, 15, 17, 21, 22, 25, 28, 33, 36, 39, 41, 44, 46, 49, 51],
            3: [1, 3, 7, 10, 12, 14, 15, 18, 19, 21, 23],
            4: [1, 3, 5, 9, 14, 16, 22, 25, 28, 31, 33, 38, 40, 42],
            5: [1, 4, 8, 12, 17, 21, 27, 29, 33, 36],
            6: [1, 6, 12, 17, 20, 24, 27, 31, 37, 39, 41, 43, 46],
            7: [1, 6, 11, 16, 18, 21, 24, 29, 31, 36, 39, 44, 48],
            8: [1, 4, 9, 11, 16, 19, 22, 26, 30, 34, 38, 40, 43, 49, 51],
            9: [1, 7, 10, 12, 18, 23, 28, 37, 43, 46, 49, 51, 54, 57, 59, 61],
            10: [1, 8, 13, 17, 21, 23, 25, 29, 38],
            11: [1, 5, 9, 14, 17, 24, 27, 29, 33, 37, 42, 45, 47, 52],
            12: [1, 4, 6, 8, 11, 13, 16, 22, 27, 32, 35, 39, 41, 47, 49, 54, 58],
            13: [1, 6, 10, 14, 18, 20, 22, 25, 28, 31, 34],
            14: [1, 7, 12, 15, 25, 28, 31, 34],
            15: [1, 3, 8, 11, 17, 21, 25, 29],
            16: [1, 9, 14, 16, 19, 22, 27],
            17: [1, 3, 5, 7, 11, 15, 20, 22, 26, 31, 34],
            18: [1, 9, 15, 18, 24, 28, 31, 35, 40],
            19: [1, 5, 8, 11, 16, 20, 27, 28, 36, 39, 41, 45, 47],
            20: [1, 9, 17, 20, 27, 34, 39, 41, 45],
            21: [1, 5, 7, 12, 20, 25, 29, 32, 34, 37],
            22: [1, 3, 7, 14, 17, 19, 21, 24, 28, 31, 35, 39, 41, 47, 49, 52, 54, 59, 63, 66],
            23: [1, 6, 8, 13, 17, 26, 27, 32, 34, 35, 38, 39, 44, 46, 47, 50, 54],
            24: [1, 4, 8, 13, 18, 22, 25, 28, 30, 33, 36, 44, 50, 52]
        }
    },
    'romans': {
        'full_name': 'Romans',
        'short_name': 'Romans',
        'start_pattern': r'^Romans 1:1',
        'end_pattern': r'^1 Corinthians 1:1',
        'chapters': 16,
        'paragraph_structure': {
            # Structured based on Paul's theological arguments
            1: [1, 8, 13, 16, 18, 24, 28],  # Greeting, thanksgiving, gospel power, God's wrath, judgment
            2: [1, 6, 12, 17, 25],  # Judgment without partiality, law and circumcision
            3: [1, 5, 9, 19, 21, 27],  # God's faithfulness, universal sin, justification by faith
            4: [1, 4, 9, 13, 16, 23],  # Abraham justified by faith, promise to all
            5: [1, 6, 12],  # Peace with God, reconciliation, Adam and Christ
            6: [1, 6, 12, 15, 20],  # Dead to sin, alive to God, slaves to righteousness
            7: [1, 4, 7, 13, 21],  # Released from the law, struggle with sin
            8: [1, 5, 12, 18, 28, 31],  # Life in the Spirit, future glory, more than conquerors
            9: [1, 6, 14, 19, 25, 30],  # Israel's rejection, God's sovereignty, stumbling stone
            10: [1, 5, 11, 14],  # Israel's zeal, righteousness from faith, proclamation
            11: [1, 7, 13, 17, 25, 33],  # Remnant, Israel's stumbling, restoration, mystery
            12: [1, 3, 9, 14],  # Living sacrifice, spiritual gifts, love in action, practical duties
            13: [1, 8, 11],  # Submit to authorities, love fulfills law, salvation near
            14: [1, 5, 10, 13, 19],  # Accept the weak, don't judge, don't cause stumbling
            15: [1, 5, 14, 22, 30],  # Bear with weak, Paul's ministry, travel plans, prayer request
            16: [1, 3, 8, 17, 21, 25]  # Commend Phoebe, greetings, warnings, final greetings, doxology
        }
    }
}

def download_bsb():
    """Download the BSB text."""
    url = 'https://bereanbible.com/bsb.txt'
    print('Downloading BSB...')
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')

def extract_book(bsb_text, book_config):
    """Extract a specific book from BSB text."""
    lines = bsb_text.split('\n')
    book_lines = []
    in_book = False

    for line in lines:
        # Check for start of book
        if re.match(book_config['start_pattern'], line):
            in_book = True
        # Check for end of book
        elif re.match(book_config['end_pattern'], line):
            in_book = False

        if in_book and line.strip():
            book_lines.append(line)

    return book_lines

def parse_verses(book_lines):
    """Parse verse text into structured data."""
    chapters = {}

    for line in book_lines:
        # Match pattern like "Mark 1:1 text here"
        match = re.match(r'^[A-Za-z\s]+(\d+):(\d+)\s+(.+)$', line)
        if match:
            chapter_num = int(match.group(1))
            verse_num = int(match.group(2))
            text = match.group(3)

            if chapter_num not in chapters:
                chapters[chapter_num] = {}

            chapters[chapter_num][verse_num] = text

    return chapters

def is_in_open_dialogue(text):
    """Check if text ends with an open quotation (odd number of quotes)."""
    # Count quotation marks in the text (both straight and curly quotes)
    straight_quotes = text.count('"')
    curly_open = text.count('“')
    curly_close = text.count('”')

    # For curly quotes, check if there are more opening than closing
    if curly_open > 0 or curly_close > 0:
        return curly_open > curly_close

    # For straight quotes, check if odd number
    return straight_quotes % 2 == 1

def add_continuation_quotes(paragraphs):
    """Add opening quotes to paragraphs that continue dialogue."""
    global in_dialogue

    for para_idx, paragraph in enumerate(paragraphs):
        if not paragraph:
            continue

        # If we're in ongoing dialogue and this paragraph doesn't start with a quote,
        # add one to indicate continuation
        first_verse_text = paragraph[0]['text']
        if in_dialogue and not first_verse_text.startswith(('"', '“')):
            paragraph[0]['text'] = '“' + first_verse_text

        # Check the last verse of this paragraph to see if dialogue is still open
        last_verse_text = paragraph[-1]['text']
        in_dialogue = is_in_open_dialogue(last_verse_text)

    return paragraphs

def expand_paragraph_structure(paragraph_starts, max_verse):
    """
    Expand paragraph structure from start verses to full verse lists.

    Args:
        paragraph_starts: List of starting verse numbers for each paragraph
        max_verse: The maximum verse number in the chapter

    Returns:
        List of lists, where each inner list contains consecutive verse numbers

    Example:
        expand_paragraph_structure([1, 4, 7], 10)
        Returns: [[1, 2, 3], [4, 5, 6], [7, 8, 9, 10]]
    """
    if not paragraph_starts:
        return []

    result = []
    for i, start in enumerate(paragraph_starts):
        # Determine end verse (exclusive)
        if i + 1 < len(paragraph_starts):
            end = paragraph_starts[i + 1]
        else:
            end = max_verse + 1

        # Create list of verses from start to end (exclusive)
        result.append(list(range(start, end)))

    return result

def create_paragraph_structure(chapters, paragraph_structure):
    """Create paragraph structure from verse data."""
    result = []

    for chapter_num in sorted(chapters.keys()):
        chapter_verses = chapters[chapter_num]

        if paragraph_structure and chapter_num in paragraph_structure:
            # Expand paragraph starts to full verse lists
            paragraph_starts = paragraph_structure[chapter_num]
            max_verse = max(chapter_verses.keys())
            verse_groups = expand_paragraph_structure(paragraph_starts, max_verse)

            # Use expanded paragraph structure
            paragraphs = []
            for verse_group in verse_groups:
                paragraph = []
                for verse_num in verse_group:
                    if verse_num in chapter_verses:
                        paragraph.append({
                            'number': verse_num,
                            'text': chapter_verses[verse_num]
                        })
                if paragraph:
                    paragraphs.append(paragraph)

            # Add continuation quotes for dialogue
            paragraphs = add_continuation_quotes(paragraphs)
        else:
            # Default: each verse is its own paragraph
            paragraphs = [[{'number': v, 'text': chapter_verses[v]}]
                         for v in sorted(chapter_verses.keys())]

        result.append({
            'chapter': chapter_num,
            'paragraphs': paragraphs
        })

    return result

def generate_js_file(book_data, output_file):
    """Generate JavaScript data file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'// Berean Standard Bible\n')
        f.write('const bookData = ')
        json.dump(book_data, f, indent=2, ensure_ascii=False)
        f.write(';\n')

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_bsb_book.py <book_id>")
        print(f"Available books: {', '.join(BOOK_CONFIGS.keys())}")
        sys.exit(1)

    book_id = sys.argv[1].lower()

    if book_id not in BOOK_CONFIGS:
        print(f"Unknown book: {book_id}")
        print(f"Available books: {', '.join(BOOK_CONFIGS.keys())}")
        sys.exit(1)

    config = BOOK_CONFIGS[book_id]

    # Warn if paragraph structure is not defined
    if config['paragraph_structure'] is None:
        print(f"Warning: No paragraph structure defined for {config['full_name']}")
        print("Using default structure (one paragraph per verse)")
        print()

    # Download and parse
    bsb_text = download_bsb()
    book_lines = extract_book(bsb_text, config)
    print(f"Extracted {len(book_lines)} lines from {config['full_name']}")

    chapters = parse_verses(book_lines)
    print(f"Parsed {len(chapters)} chapters")

    book_data = create_paragraph_structure(chapters, config['paragraph_structure'])

    # Generate output file
    output_file = f'data-{book_id}.js'
    generate_js_file(book_data, output_file)
    print(f"Generated {output_file}")

    # Print summary
    total_verses = sum(len(ch['paragraphs']) if config['paragraph_structure'] is None
                      else sum(len(p) for p in ch['paragraphs'])
                      for ch in book_data)
    total_paragraphs = sum(len(ch['paragraphs']) for ch in book_data)
    print(f"Total verses: {total_verses}")
    print(f"Total paragraphs: {total_paragraphs}")

if __name__ == '__main__':
    main()
