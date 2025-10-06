// Bible books registry
const bibleBooks = [
    {
        id: "mark",
        name: "Gospel of Mark",
        shortName: "Mark",
        chapters: 16,
        dataFile: "data-mark.js"
    },
    {
        id: "luke",
        name: "Gospel of Luke",
        shortName: "Luke",
        chapters: 24,
        dataFile: "data-luke.js"
    }
    // Future books can be added here:
    // { id: "matthew", name: "Gospel of Matthew", shortName: "Matthew", chapters: 28, dataFile: "data-matthew.js" },
    // { id: "john", name: "Gospel of John", shortName: "John", chapters: 21, dataFile: "data-john.js" }
];

// Helper function to get book by ID
function getBook(bookId) {
    return bibleBooks.find(book => book.id === bookId);
}
