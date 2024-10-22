export const applyColorCoding = (htmlString, setSelectedNote) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    const rows = doc.querySelectorAll('tr');
  
    rows.forEach((row, index) => {
      if (index > 0) {
        const growthFallCol = row.cells[5];
        const colC = row.cells[6];
        const notesCol = row.cells[2];
  
        if (notesCol && notesCol.innerText.trim()) {
          const noteContent = notesCol.innerText.trim();
          const anchor = document.createElement('a');
          anchor.href = '#';
          anchor.innerText = noteContent;
          // anchor.addEventListener('click', () => handleNoteClick(noteContent, setSelectedNote));
          notesCol.innerHTML = '';  // Clear the cell content
          notesCol.appendChild(anchor);  // Append the clickable link
        }
  
        const growthFallValue = parseFloat(growthFallCol.innerText.replace('%', '').trim());
        colC.style.backgroundColor = growthFallValue > 10 ? 'red' : '';
      }
    });
  
    return doc.body.innerHTML;
  };
  
  export const handleNoteClick = (noteContent, setSelectedNote) => {
    setSelectedNote(noteContent);
  };
  