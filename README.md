# Bible Journey

A gamified Bible reading web application that encourages Scripture reading through progress tracking, visual journey maps, and unlockable achievement moments.

## Features

- 🗺️ **Visual journey map** - Track your progress along a winding path
- ✨ **Unlockable moments** - Discover significant events and teachings as you read
- 📱 **Mobile-first design** - Responsive interface optimized for reading on any device
- 💾 **Client-side storage** - Your progress is saved locally in browser cookies
- 🎨 **Beautiful typography** - Comfortable reading experience with Crimson Text serif font

## Live Demo

Visit the app at: [https://smbz.github.io/bible-journey/](https://smbz.github.io/bible-journey/)

## Technology

- Pure HTML/CSS/JavaScript (no frameworks)
- Browser cookies for progress tracking
- Berean Standard Bible (BSB) - public domain translation
- GitHub Pages hosting

## Usage

Simply open the app and:
1. Choose a book to read (Mark or Luke)
2. Read chapters at your own pace
3. Chapters automatically mark as complete when you reach the end
4. Unlock significant moments and events
5. View your progress on the journey map

## Development

### Adding New Books

1. Add book metadata to `books-data.js`
2. Update `parse_bsb_book.py` with book configuration
3. Run: `python3 parse_bsb_book.py <book_id>`
4. Add events to `events-data.js`

See `CLAUDE.md` for complete developer documentation.

## Attribution

Scripture quotations from the [Berean Standard Bible](https://berean.bible/), which has been dedicated to the public domain. The Bible text, including our paragraph formatting, is in the public domain.

## License

The application code is licensed under the MIT License (see LICENSE file).

The Bible text (Berean Standard Bible), including our paragraph breaks and formatting, is in the public domain.
