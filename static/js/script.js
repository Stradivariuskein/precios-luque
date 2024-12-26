
let originalTable;
var searchTimer;

document.addEventListener('DOMContentLoaded', function() {
    const auxTable = document.getElementById('table-body');
  
    if (auxTable) {
      originalTable = auxTable.cloneNode(true);
  
    }
})

function startSearchTimer(func) {
  // Cancela el temporizador existente si lo hay
  clearTimeout(searchTimer);

  // Inicia un nuevo temporizador después de 2 segundos
  searchTimer = setTimeout(func, 1000);
};




function searchArtic3() {
  let input = document.getElementById('searchInput');
  let table = document.getElementById('table-body');

  if (input.value !== "") {
      let filter = input.value.toUpperCase();
      let keywords = filter.split(' ');

      // Restaura la tabla al estado original
      table.innerHTML = originalTable.innerHTML;

      let rows = table.getElementsByTagName('tr');
      let fragment = document.createDocumentFragment();

      for (let row of rows) {
          fragment.appendChild(row.cloneNode(true));
          let fragment_row = fragment.lastChild;
          let shouldShow = true;
          let modifiedCells = [];

          for (let keyword of keywords) {
              if (keyword !== "" && keyword !== " ") {
                  let found = false;

                  for (let col of fragment_row.children) {
                      let col_text = col.innerText;
                      let col_html = col.innerHTML;
                      let index = col_text.toUpperCase().indexOf(keyword.toUpperCase());
                      let highlightedText = col_html;

                      if (index > -1) {
                          found = true;
                          index += col_html.indexOf(col_text);
                          highlightedText = col_html.substring(0, index) +
                              '<span style="color: red;">' +
                              col_html.substring(index, index + keyword.length) +
                              '</span>' +
                              col_html.substring(index + keyword.length);
                      }
                      modifiedCells.push({ col, highlightedText });
                  }

                  if (!found) {
                      shouldShow = false;
                      break;
                  }
              }
          }

          for (let { col, highlightedText } of modifiedCells) {
              col.innerHTML = highlightedText;
          }

          fragment_row.style.display = shouldShow ? '' : 'none';
      }

      table.innerHTML = '';
      table.appendChild(fragment);

      // Reasigna los event listeners después de actualizar el DOM
      assignImageModalListeners();
  } else {
      table.innerHTML = originalTable.innerHTML;
      assignImageModalListeners();
  }
}

// Función para asignar los event listeners a las imágenes
function assignImageModalListeners() {
  const modalImage = document.getElementById('modal-image');
  const prevButton = document.getElementById('prev-image');
  const nextButton = document.getElementById('next-image');
  let images = [];
  let currentIndex = 0;

  document.querySelectorAll('img[data-bs-toggle="modal"]').forEach(img => {
      img.addEventListener('click', function () {
          const imageUrl = this.dataset.image;
          images = this.dataset.images.split(',');
          currentIndex = images.indexOf(imageUrl);

          modalImage.src = imageUrl;
      });
  });

  prevButton.addEventListener('click', function () {
      if (currentIndex > 0) {
          currentIndex--;
          modalImage.src = images[currentIndex];
      }
  });

  nextButton.addEventListener('click', function () {
      if (currentIndex < images.length - 1) {
          currentIndex++;
          modalImage.src = images[currentIndex];
      }
  });
}

// Llama a la función inicial para asignar los listeners cuando cargues la página
document.addEventListener('DOMContentLoaded', assignImageModalListeners);
