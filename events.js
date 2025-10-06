// Events page - Significant moments discovered

// Check if an event has been unlocked
function isEventUnlocked(event) {
    const allRead = getAllReadChapters();
    return event.locations.some(loc => {
        const bookChapters = allRead[loc.book] || [];
        return bookChapters.includes(loc.chapter);
    });
}

// Get which locations have been read for an event
function getReadLocations(event) {
    const allRead = getAllReadChapters();
    return event.locations.filter(loc => {
        const bookChapters = allRead[loc.book] || [];
        return bookChapters.includes(loc.chapter);
    });
}

// Render events grid
function renderEvents() {
    const grid = document.getElementById('events-grid');
    const discoveredCountEl = document.getElementById('discovered-count');

    let discoveredCount = 0;

    // Only show events that have been unlocked (read in at least one book)
    significantMoments.forEach(event => {
        if (isEventUnlocked(event)) {
            discoveredCount++;

            const card = document.createElement('div');
            card.className = 'event-card';

            const readLocs = getReadLocations(event);

            // Build list of all locations with links
            const locationLinks = event.locations.map(loc => {
                const book = getBook(loc.book);
                const bookName = book ? book.shortName : loc.book;
                const isRead = readLocs.some(r => r.book === loc.book && r.chapter === loc.chapter);

                if (isRead) {
                    return `<a href="book.html?book=${loc.book}#chapter-${loc.chapter}" class="event-reference">${bookName} ${loc.chapter}</a>`;
                } else {
                    return `<span class="event-reference-unread">${bookName} ${loc.chapter}</span>`;
                }
            }).join(' ');

            card.innerHTML = `
                <div class="achievement-badge">✓</div>
                <div class="event-icon">${event.icon}</div>
                <h3 class="event-title">${event.title}</h3>
                <div class="event-locations">${locationLinks}</div>
            `;

            grid.appendChild(card);
        }
    });

    // Update discovery count
    discoveredCountEl.textContent = discoveredCount;
    document.getElementById('total-count').textContent = significantMoments.length;

    // Show message if no events discovered yet
    if (discoveredCount === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.style.gridColumn = '1 / -1';
        emptyMessage.style.textAlign = 'center';
        emptyMessage.style.padding = '3rem 1rem';
        emptyMessage.style.color = '#6b6355';
        emptyMessage.innerHTML = `
            <p style="font-size: 1.2rem; margin-bottom: 1rem;">No moments discovered yet</p>
            <p>Start reading to unlock significant events and teachings!</p>
            <a href="index.html" style="display: inline-block; margin-top: 1.5rem; color: #6b5335; text-decoration: none; border: 1px solid #d4cfc0; padding: 0.7rem 1.5rem; border-radius: 4px;">
                Begin Reading →
            </a>
        `;
        grid.appendChild(emptyMessage);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', renderEvents);
