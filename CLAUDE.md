# Bible Reading Journey - Developer Documentation

## Project Overview

A gamified Bible reading web application that encourages users to read Scripture through progress tracking, visual journey maps, and unlockable achievement moments. Built as a static web application with client-side storage.

## Architecture

### Technology Stack
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Storage**: Browser cookies (client-side only, no backend)
- **Data Format**: JavaScript modules with JSON-like structures
- **Bible Translation**: Berean Standard Bible (BSB) - public domain

### File Structure

```
├── index.html              # Homepage with book selection
├── book.html              # Main reading page (dynamic, book-aware)
├── progress.html          # Journey visualization page
├── events.html            # Achievement/moments page
├── styles.css             # Main reading page styles
├── home.css               # Homepage styles
├── progress.css           # Journey page styles
├── events.css             # Events page styles
├── books-data.js          # Book registry and metadata
├── data-mark.js           # Gospel of Mark text (16 chapters)
├── data-luke.js           # Gospel of Luke text (24 chapters)
├── events-data.js         # Significant moments/events
├── script.js              # Core application logic
├── progress.js            # Journey map functionality
├── events.js              # Events page logic
└── parse_bsb_book.py      # Python script to generate book data files
```

## Core Concepts

### 1. Multi-Book Support

**URL Structure:**
- Homepage: `index.html`
- Reading: `book.html?book=<bookId>#chapter-<num>`
- Journey: `progress.html?book=<bookId>`
- Events: `events.html` (shows all books)

**Book Registry** (`books-data.js`):
```javascript
const bibleBooks = [
    {
        id: "mark",
        name: "Gospel of Mark",
        shortName: "Mark",
        chapters: 16,
        dataFile: "data-mark.js"
    },
    // ... more books
];
```

### 2. Dynamic Data Loading

Books are loaded on-demand to save bandwidth:

```javascript
async function loadBookData(bookId) {
    const book = getBook(bookId);
    const script = document.createElement('script');
    script.src = book.dataFile;
    // ... load dynamically
}
```

Each book data file exports a `bookData` constant:
```javascript
const bookData = [
    {
        chapter: 1,
        paragraphs: [
            [
                { number: 1, text: "..." },
                { number: 2, text: "..." }
            ],
            // ... more paragraphs
        ]
    },
    // ... more chapters
];
```

### 3. Progress Tracking

**Storage Format** (cookie):
```javascript
{
    "mark": [1, 2, 3, 16],      // Chapters read in Mark
    "luke": [1, 5, 10]          // Chapters read in Luke
}
```

**Key Functions:**
- `getAllReadChapters()` - Returns full object
- `getReadChapters(bookId)` - Returns array for specific book
- `isChapterRead(bookId, chapterNum)` - Boolean check
- `markChapterAsRead(bookId, chapterNum)` - Mark as complete
- `unmarkChapterAsRead(bookId, chapterNum)` - Unmark

**Auto-Migration**: Old format `[1,2,3]` automatically converts to `{"mark": [1,2,3]}`

### 4. Smart Chapter Completion

**Scroll Detection:**
- Uses Intersection Observer API
- Tracks when chapter end marker is visible
- Requires 2.5 second dwell time
- Cancels if scrolling too fast (>100px/s)

**Manual Marking:**
- Button at end of each chapter
- "Unmark as read" option for mistakes

### 5. Events System

**Event Structure** (`events-data.js`):
```javascript
{
    title: "Jesus's Baptism",
    icon: "💧",
    locations: [
        { book: "mark", chapter: 1 },
        { book: "matthew", chapter: 3 },
        { book: "luke", chapter: 3 }
    ]
}
```

**Unlocking Logic:**
- Event unlocks when read in ANY of its locations
- Shows all locations (read and unread)
- Read locations are clickable links
- Unread locations are grayed out

**Achievement Overlay:**
- Appears when chapter is marked complete
- Shows all events unlocked from that chapter
- Displays all parallel locations
- Staggered animation for multiple events

### 6. Journey Visualization

**SVG Path:**
- Winding path representing reading journey
- Chapters positioned along path using `getPointAtLength()`
- Path scales to any number of chapters
- Decorative elements (grass, stones)

**Dynamic Positioning:**
```javascript
for (let i = 0; i < numChapters; i++) {
    const ratio = numChapters === 1 ? 0.5 : i / (numChapters - 1);
    const point = path.getPointAtLength(pathLength * ratio);
    // Position chapter marker at point
}
```

## Data Generation

### parse_bsb_book.py

**Purpose**: Download BSB text and generate formatted JavaScript data files

**Usage:**
```bash
python3 parse_bsb_book.py <book_id>
```

**Features:**
1. Downloads BSB from bereanbible.com/bsb.txt
2. Extracts specific book based on patterns
3. Applies manual paragraph structure (if defined)
4. Adds continuation quotes for dialogue
5. Generates `data-<bookId>.js`

**Paragraph Structure:**
Manually defined in `BOOK_CONFIGS` for optimal reading flow:
```python
'paragraph_structure': {
    1: [
        [1, 2, 3],    # Verses 1-3 in first paragraph
        [4, 5],       # Verses 4-5 in second paragraph
        # ...
    ]
}
```

**Continuation Quotes:**
- Detects open dialogue (unclosed quotes)
- Adds opening quote to continuation paragraphs
- Handles both straight (") and curly (" ") quotes
- Follows standard literary convention

**Default Behavior:**
- If no paragraph structure defined, creates one paragraph per verse
- Warns but still generates usable file

## Adding New Books

1. **Add to book registry** (`books-data.js`):
```javascript
{
    id: "matthew",
    name: "Gospel of Matthew",
    shortName: "Matthew",
    chapters: 28,
    dataFile: "data-matthew.js"
}
```

2. **Add to parser** (`parse_bsb_book.py`):
```python
'matthew': {
    'full_name': 'Gospel of Matthew',
    'short_name': 'Matthew',
    'start_pattern': r'^Matthew 1:1',
    'end_pattern': r'^Mark 1:1',
    'chapters': 28,
    'paragraph_structure': None  # Or define structure
}
```

3. **Generate data file**:
```bash
python3 parse_bsb_book.py matthew
```

4. **(Optional) Define paragraph structure** for better readability

5. **Add events** to `events-data.js` with locations

## Adding Events

1. Choose significant moments (aim for ~1 per chapter)
2. Add to `events-data.js`:
```javascript
{
    title: "Event Name",
    icon: "📖",  // Emoji icon (will be replaced with graphics later)
    locations: [
        { book: "mark", chapter: 5 },
        { book: "matthew", chapter: 9 }
        // All places this event appears
    ]
}
```

3. Same event can appear in multiple books
4. Unlocks when read in ANY location

## Design Philosophy

### User Experience
- **Mobile-first**: Responsive design for phone reading
- **Minimal friction**: No accounts, no server, instant access
- **Encouraging**: Progress visualization, achievements
- **Traditional aesthetic**: Serif fonts, cream background, biblical map style

### Performance
- **Lazy loading**: Books loaded only when needed
- **Client-side only**: No server requests after initial load
- **Cookie storage**: Simple, no database needed
- **Static files**: Can host anywhere (GitHub Pages, etc.)

### Content
- **Public domain**: BSB is freely usable
- **Readable**: Manually curated paragraph breaks
- **Accurate**: Source text preserved exactly
- **Conventional**: Proper quotation continuation

## Browser Compatibility

**Required Features:**
- Intersection Observer API
- ES6+ JavaScript (async/await, arrow functions)
- CSS Grid and Flexbox
- SVG support
- Cookie storage

**Supported Browsers:**
- Chrome/Edge 58+
- Firefox 55+
- Safari 12.1+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

**Potential additions:**
- More books (complete Bible)
- Custom paragraph structures for all books
- Graphic icons instead of emoji
- Reading streaks/statistics
- Notes/highlighting (localStorage)
- Audio narration
- Multiple translations
- Social sharing of progress
- Print/PDF export

## Contributing

When adding books or events:
1. Follow existing naming conventions
2. Test on mobile devices
3. Verify paragraph flow is readable
4. Ensure continuation quotes are correct
5. Check that events unlock properly
6. Test with cookies disabled (graceful degradation)

## License

**Code**: MIT License (or your preferred license)
**Bible Text**: BSB is public domain (CC0)
**Attribution**: Link to berean.bible required in UI

## Contact

For questions or contributions, see repository issues.
