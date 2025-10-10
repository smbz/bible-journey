// Progress page - Journey map functionality

// Current book being displayed on progress page
let progressBookId = 'mark';
let progressBook = null;

// Calculate positions along the SVG path for each chapter
function getChapterPositions(numChapters) {
    const positions = [];
    const path = document.getElementById('main-path');
    const pathLength = path.getTotalLength();

    // Distribute chapters from start to end of path
    for (let i = 0; i < numChapters; i++) {
        const ratio = numChapters === 1 ? 0.5 : i / (numChapters - 1);
        const point = path.getPointAtLength(pathLength * ratio);
        positions.push({ x: point.x, y: point.y, chapter: i + 1 });
    }

    return positions;
}

// Create chapter markers on the map
function createChapterMarkers() {
    const positions = getChapterPositions(progressBook.chapters);
    const container = document.getElementById('chapter-markers');
    const readChapters = getReadChapters(progressBookId);

    positions.forEach(pos => {
        const isRead = readChapters.includes(pos.chapter);

        // Create marker group
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        marker.classList.add('chapter-marker');
        marker.classList.add(isRead ? 'read' : 'unread');
        marker.dataset.chapter = pos.chapter;
        marker.style.cursor = 'pointer';

        // Circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.classList.add('chapter-circle');
        circle.setAttribute('cx', pos.x);
        circle.setAttribute('cy', pos.y);
        circle.setAttribute('r', '33');
        marker.appendChild(circle);

        // Chapter number or checkmark
        if (isRead) {
            // Add checkmark
            const checkmark = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            checkmark.classList.add('chapter-checkmark');
            checkmark.setAttribute('d', `M ${pos.x - 8} ${pos.y} L ${pos.x - 3} ${pos.y + 6} L ${pos.x + 8} ${pos.y - 6}`);
            marker.appendChild(checkmark);

            // Small chapter number
            const smallNum = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            smallNum.classList.add('chapter-number');
            smallNum.setAttribute('x', pos.x);
            smallNum.setAttribute('y', pos.y + 18);
            smallNum.setAttribute('font-size', '12');
            smallNum.textContent = pos.chapter;
            marker.appendChild(smallNum);
        } else {
            // Chapter number
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.classList.add('chapter-number');
            text.setAttribute('x', pos.x);
            text.setAttribute('y', pos.y);
            text.textContent = pos.chapter;
            marker.appendChild(text);
        }

        // Click handler
        marker.addEventListener('click', () => {
            navigateToChapter(pos.chapter);
        });

        container.appendChild(marker);
    });
}

// Navigate to a specific chapter on the reading page
function navigateToChapter(chapterNum) {
    window.location.href = `book.html?book=${progressBookId}#chapter-${chapterNum}`;
}

// Update progress summary in header
function updateProgressSummary() {
    const readChapters = getReadChapters(progressBookId);
    const total = progressBook.chapters;
    const completed = readChapters.length;
    const percentage = Math.round((completed / total) * 100);

    // Update subtitle text
    const subtitle = document.getElementById('progress-subtitle');
    if (subtitle) {
        subtitle.textContent = `${completed} of ${total} chapters read`;
    }

    // Update progress bar
    const progressFill = document.getElementById('header-progress-fill');
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
}

// Populate book modal
function populateBookModal() {
    const bookList = document.getElementById('book-list');
    const modal = document.getElementById('book-modal');
    const bookshelfButton = document.getElementById('bookshelf-button');
    const closeButton = document.getElementById('close-modal');

    if (!bookList || !modal || !bookshelfButton) return;

    // Populate book list
    bibleBooks.forEach(book => {
        const item = document.createElement('a');
        item.href = `progress.html?book=${book.id}`;
        item.className = 'book-list-item';
        if (book.id === progressBookId) {
            item.classList.add('current');
        }

        item.innerHTML = `
            <div class="book-list-item-name">${book.name}</div>
            <div class="book-list-item-chapters">${book.chapters} chapters</div>
        `;

        bookList.appendChild(item);
    });

    // Open modal
    bookshelfButton.addEventListener('click', () => {
        modal.classList.add('visible');
    });

    // Close modal
    const closeModal = () => {
        modal.classList.remove('visible');
    };

    closeButton.addEventListener('click', closeModal);

    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('visible')) {
            closeModal();
        }
    });
}

// Initialize the journey map
function initializeJourneyMap() {
    // Get book ID from URL parameter, default to 'mark'
    const urlParams = new URLSearchParams(window.location.search);
    progressBookId = urlParams.get('book') || 'mark';
    progressBook = getBook(progressBookId);

    if (!progressBook) {
        console.error('Book not found:', progressBookId);
        return;
    }

    populateBookModal();
    createChapterMarkers();
    updateProgressSummary();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeJourneyMap);
