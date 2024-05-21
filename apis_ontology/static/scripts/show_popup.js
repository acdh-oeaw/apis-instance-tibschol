function showPopup(recordId, renderStyle) {
  renderStyle = "tei";
  fetch(`/apis/excerpts/${recordId}/${renderStyle}`)
    .then(response => response.text())
    .then(data => {
      // Display the data in the popup
      document.getElementById('popupContent').innerHTML = data;
      document.getElementById('popupModal').style.display = 'block';
    })
    .catch(error => {
      console.error('Error fetching dynamic content:', error);
    });
}

function closePopup() {
  document.getElementById('popupModal').style.display = 'none';
}
