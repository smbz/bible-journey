// Cookie management for storing read chapters
const COOKIE_NAME = 'bible_read_chapters';
const LAST_BOOK_COOKIE = 'bible_last_book';
const COOKIE_EXPIRY_DAYS = 365;

// Save/get last read book
function saveLastBook(bookId) {
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + COOKIE_EXPIRY_DAYS);
    document.cookie = `${LAST_BOOK_COOKIE}=${bookId}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Strict`;
}

function getLastBook() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === LAST_BOOK_COOKIE) {
            return value;
        }
    }
    return 'mark'; // Default to Mark
}

// Get first unread chapter for a book
function getFirstUnreadChapter(bookId) {
    const book = getBook(bookId);
    if (!book) return 1;

    const readChapters = getReadChapters(bookId);
    for (let i = 1; i <= book.chapters; i++) {
        if (!readChapters.includes(i)) {
            return i;
        }
    }
    return 1; // All read, go back to chapter 1
}

// Get smart reading URL (last book, first unread chapter)
function getSmartReadingURL() {
    const lastBook = getLastBook();
    const firstUnread = getFirstUnreadChapter(lastBook);
    return `book.html?book=${lastBook}#chapter-${firstUnread}`;
}

// Get smart journey URL (last book)
function getSmartJourneyURL() {
    const lastBook = getLastBook();
    return `progress.html?book=${lastBook}`;
}

// Get all read chapters (for all books)
function getAllReadChapters() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === COOKIE_NAME) {
            try {
                const data = JSON.parse(decodeURIComponent(value));

                // Migrate old format: [1, 2, 3] → {"mark": [1, 2, 3]}
                if (Array.isArray(data)) {
                    const migrated = { "mark": data };
                    saveAllReadChapters(migrated);
                    return migrated;
                }

                return data;
            } catch (e) {
                return {};
            }
        }
    }
    return {};
}

// Save all read chapters (for all books)
function saveAllReadChapters(allChapters) {
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + COOKIE_EXPIRY_DAYS);
    const cookieValue = encodeURIComponent(JSON.stringify(allChapters));
    document.cookie = `${COOKIE_NAME}=${cookieValue}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Strict`;
}

// Get read chapters for a specific book
function getReadChapters(bookId) {
    const allChapters = getAllReadChapters();
    return allChapters[bookId] || [];
}

// Check if a chapter is read
function isChapterRead(bookId, chapterNum) {
    const readChapters = getReadChapters(bookId);
    return readChapters.includes(chapterNum);
}

// Mark a chapter as read
function markChapterAsRead(bookId, chapterNum) {
    let allChapters = getAllReadChapters();
    if (!allChapters[bookId]) {
        allChapters[bookId] = [];
    }
    if (!allChapters[bookId].includes(chapterNum)) {
        allChapters[bookId].push(chapterNum);
        saveAllReadChapters(allChapters);
        return true;
    }
    return false;
}

// Unmark a chapter as read
function unmarkChapterAsRead(bookId, chapterNum) {
    let allChapters = getAllReadChapters();
    if (!allChapters[bookId]) {
        return false;
    }
    const index = allChapters[bookId].indexOf(chapterNum);
    if (index > -1) {
        allChapters[bookId].splice(index, 1);
        saveAllReadChapters(allChapters);
        return true;
    }
    return false;
}

// Dynamic book data loading
function loadBookData(bookId) {
    return new Promise((resolve, reject) => {
        const book = getBook(bookId);
        if (!book) {
            reject(`Book ${bookId} not found`);
            return;
        }

        // Check if already loaded
        if (typeof bookData !== 'undefined') {
            resolve(bookData);
            return;
        }

        const script = document.createElement('script');
        script.src = book.dataFile;
        script.onload = () => {
            if (typeof bookData !== 'undefined') {
                resolve(bookData);
            } else {
                reject(`Failed to load book data from ${book.dataFile}`);
            }
        };
        script.onerror = () => reject(`Failed to load ${book.dataFile}`);
        document.head.appendChild(script);
    });
}

// Current book ID (set by page initialization)
let currentBookId = 'mark';

// Render book content
function renderBook(bookId, chapters) {
    currentBookId = bookId;
    const contentDiv = document.getElementById('content');

    chapters.forEach(chapterData => {
        const chapterSection = document.createElement('section');
        chapterSection.className = 'chapter';
        chapterSection.dataset.chapter = chapterData.chapter;

        // Add chapter ID for anchor navigation
        chapterSection.id = `chapter-${chapterData.chapter}`;

        // Chapter header
        const header = document.createElement('div');
        header.className = 'chapter-header';
        header.innerHTML = `
            <span class="chapter-number">${chapterData.chapter}</span>
            <h2 class="chapter-title">Chapter ${chapterData.chapter}</h2>
        `;
        chapterSection.appendChild(header);

        // Paragraphs with continuous verses
        chapterData.paragraphs.forEach(paragraph => {
            const paragraphDiv = document.createElement('p');
            paragraphDiv.className = 'paragraph';

            paragraph.forEach((verse, index) => {
                // Add verse number as superscript
                const verseNum = document.createElement('sup');
                verseNum.className = 'verse-number';
                verseNum.textContent = verse.number;
                paragraphDiv.appendChild(verseNum);

                // Add verse text
                const verseText = document.createTextNode(verse.text);
                paragraphDiv.appendChild(verseText);

                // Add space between verses (except after last verse)
                if (index < paragraph.length - 1) {
                    paragraphDiv.appendChild(document.createTextNode(' '));
                }
            });

            chapterSection.appendChild(paragraphDiv);
        });

        // Chapter completion marker
        const marker = document.createElement('div');
        marker.className = 'chapter-marker';
        marker.dataset.chapterNum = chapterData.chapter;

        if (isChapterRead(bookId, chapterData.chapter)) {
            marker.classList.add('read');
            marker.innerHTML = `
                <div class="completion-message">Chapter completed</div>
                <button class="mark-complete-btn" onclick="handleUnmarkComplete(${chapterData.chapter})" style="margin-top: 0.5rem;">
                    Unmark as read
                </button>
            `;
        } else {
            marker.innerHTML = `
                <button class="mark-complete-btn" onclick="handleMarkComplete(${chapterData.chapter})">
                    Mark chapter as read
                </button>
            `;
        }

        chapterSection.appendChild(marker);
        contentDiv.appendChild(chapterSection);
    });

    // Initialize scroll detection
    initializeScrollDetection();
}

// Handle manual chapter completion
function handleMarkComplete(chapterNum) {
    if (markChapterAsRead(currentBookId, chapterNum)) {
        updateChapterMarker(chapterNum, true);
        showUnlockedEvents(currentBookId, chapterNum);
    }
}

// Handle unmarking chapter
function handleUnmarkComplete(chapterNum) {
    if (unmarkChapterAsRead(currentBookId, chapterNum)) {
        updateChapterMarker(chapterNum, false);
    }
}

// Update the visual state of a chapter marker
function updateChapterMarker(chapterNum, isRead) {
    const marker = document.querySelector(`.chapter-marker[data-chapter-num="${chapterNum}"]`);
    if (!marker) return;

    if (isRead) {
        marker.classList.add('read');
        marker.innerHTML = `
            <div class="completion-message">Chapter completed</div>
            <button class="mark-complete-btn" onclick="handleUnmarkComplete(${chapterNum})" style="margin-top: 0.5rem;">
                Unmark as read
            </button>
        `;
    } else {
        marker.classList.remove('read');
        marker.innerHTML = `
            <button class="mark-complete-btn" onclick="handleMarkComplete(${chapterNum})">
                Mark chapter as read
            </button>
        `;
    }
}

// Scroll detection for auto-marking chapters
const DWELL_TIME_MS = 2500; // 2.5 seconds
const SCROLL_SPEED_THRESHOLD = 100; // pixels per second

let scrollTimeout;
let lastScrollY = window.scrollY;
let lastScrollTime = Date.now();
let dwellTimers = new Map(); // Track dwell time per chapter

function initializeScrollDetection() {
    // Create Intersection Observers for each chapter marker
    const markers = document.querySelectorAll('.chapter-marker');

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: [0, 0.5, 1.0]
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const chapterNum = parseInt(entry.target.dataset.chapterNum);

            if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
                // Marker is visible - start dwell timer if not already read
                if (!isChapterRead(chapterNum)) {
                    startDwellTimer(chapterNum, entry.target);
                }
            } else {
                // Marker left view - cancel dwell timer
                cancelDwellTimer(chapterNum);
            }
        });
    }, observerOptions);

    markers.forEach(marker => {
        observer.observe(marker);
        // Make marker visible when it enters viewport
        const intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        intersectionObserver.observe(marker);
    });

    // Track scroll speed
    window.addEventListener('scroll', () => {
        const currentTime = Date.now();
        const currentScrollY = window.scrollY;
        const timeDelta = currentTime - lastScrollTime;
        const scrollDelta = Math.abs(currentScrollY - lastScrollY);

        if (timeDelta > 0) {
            const scrollSpeed = (scrollDelta / timeDelta) * 1000; // pixels per second

            // If scrolling fast, cancel all dwell timers
            if (scrollSpeed > SCROLL_SPEED_THRESHOLD) {
                cancelAllDwellTimers();
            }
        }

        lastScrollY = currentScrollY;
        lastScrollTime = currentTime;
    }, { passive: true });
}

function startDwellTimer(chapterNum, markerElement) {
    // Don't start if already has a timer or already read
    if (dwellTimers.has(chapterNum) || isChapterRead(currentBookId, chapterNum)) {
        return;
    }

    const timer = setTimeout(() => {
        // After dwelling for the required time, mark as read
        if (markChapterAsRead(currentBookId, chapterNum)) {
            updateChapterMarker(chapterNum, true);
            showUnlockedEvents(currentBookId, chapterNum);
            dwellTimers.delete(chapterNum);
        }
    }, DWELL_TIME_MS);

    dwellTimers.set(chapterNum, timer);
}

function cancelDwellTimer(chapterNum) {
    if (dwellTimers.has(chapterNum)) {
        clearTimeout(dwellTimers.get(chapterNum));
        dwellTimers.delete(chapterNum);
    }
}

function cancelAllDwellTimers() {
    dwellTimers.forEach((timer, chapterNum) => {
        clearTimeout(timer);
    });
    dwellTimers.clear();
}

// Handle navigation from hash (e.g., #chapter-3)
function handleHashNavigation() {
    const hash = window.location.hash;
    if (hash && hash.startsWith('#chapter-')) {
        const chapterElement = document.querySelector(hash);
        if (chapterElement) {
            // Delay scroll to ensure content is rendered
            setTimeout(() => {
                chapterElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }
}

// Show unlocked events overlay
function showUnlockedEvents(bookId, chapterNum) {
    // Find all events for this book and chapter
    const chapterEvents = significantMoments.filter(moment =>
        moment.locations.some(loc => loc.book === bookId && loc.chapter === chapterNum)
    );

    // Only show overlay if there are events for this chapter
    if (chapterEvents.length === 0) {
        return;
    }

    const overlay = document.getElementById('events-overlay');
    const titleEl = document.getElementById('overlay-chapter-title');
    const listEl = document.getElementById('unlocked-events-list');

    // Get book name
    const book = getBook(bookId);
    const bookName = book ? book.shortName : bookId;

    // Set chapter title
    titleEl.textContent = `${bookName} ${chapterNum} Complete`;

    // Clear previous events
    listEl.innerHTML = '';

    // Add each event with animation
    chapterEvents.forEach((event, index) => {
        const eventItem = document.createElement('div');
        eventItem.className = 'unlocked-event-item';

        // Build reference list showing all locations
        const references = event.locations.map(loc => {
            const locBook = getBook(loc.book);
            const locName = locBook ? locBook.shortName : loc.book;
            return `${locName} ${loc.chapter}`;
        }).join(', ');

        eventItem.innerHTML = `
            <div class="unlocked-event-icon">${event.icon}</div>
            <div class="unlocked-event-details">
                <div class="unlocked-event-title">${event.title}</div>
                <div class="unlocked-event-reference">${references}</div>
            </div>
        `;

        listEl.appendChild(eventItem);
    });

    // Show overlay with fade-in
    setTimeout(() => {
        overlay.classList.add('visible');
    }, 100);
}

// Close events overlay
function closeEventsOverlay() {
    const overlay = document.getElementById('events-overlay');
    overlay.classList.remove('visible');
}

// Initialize book page when DOM is loaded
async function initializeBookPage() {
    // Get book ID from URL parameter, default to 'mark'
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('book') || 'mark';

    // Save as last read book
    saveLastBook(bookId);

    try {
        // Load book data dynamically
        const chapters = await loadBookData(bookId);

        // Render the book
        renderBook(bookId, chapters);

        // Handle hash navigation (e.g., #chapter-3)
        handleHashNavigation();
    } catch (error) {
        console.error('Failed to load book:', error);
        document.getElementById('content').innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #6b6355;">
                <p>Unable to load book. Please try again.</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">${error}</p>
            </div>
        `;
    }
}

// Initialize when DOM is loaded (only for book.html)
if (document.getElementById('content')) {
    document.addEventListener('DOMContentLoaded', initializeBookPage);
}
