function deleteNote(noteId) {
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token
        }
    }).then((_res) => {
        window.location.href = "/";
    });
}
