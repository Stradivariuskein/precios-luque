
let originalTable;


document.addEventListener('DOMContentLoaded', function() {
    const auxTable = document.getElementById('categoryTabContent');
  
    if (auxTable) {
      originalTable = auxTable.cloneNode(true);
  
    }
})


let searchTimer;

// function startSearchTimer(func, tableId = "tableModal", inputId = "searchInput") {
//   clearTimeout(searchTimer);
//   searchTimer = setTimeout(() => func(tableId, inputId), 1000);
// }

function startSearchTimer(func, inputId = "searchInput", tableId = "tableModal") {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    // Verifica si el elemento existe antes de llamar a la función
    const inputElement = document.getElementById(inputId);
    if (inputElement) {
      func(inputId, tableId);
    } else {
      console.error(`El elemento con ID ${inputId} no se encuentra.`);
    }
  }, 1000);
}

function searchArtic3(inputId = "searchInput", containerId = "tableModal", ) {
  console.log(containerId)
  console.log(inputId)
  const input = document.getElementById(inputId);
  console.log(input)
    const filter = input.value.toUpperCase();
    
    const table = document.querySelector(`#${containerId} .subcategory-table table tbody`);
    const rows = table.getElementsByTagName('tr');
  
    if (filter === "") {
      // Muestra todas las filas si el input está vacío
      Array.from(rows).forEach(row => (row.style.display = ""));
    } else {
      const keywords = filter.split(' ');
  
      Array.from(rows).forEach(row => {
        let shouldShow = true;
        const cells = Array.from(row.children);
        let modifiedCells = [];
  
        for (let keyword of keywords) {
          if (keyword !== "" && keyword !== " ") {
            let found = false;
  
            cells.forEach((cell, index) => {
              // Omitir la columna "Precio" (índice 2)
              if (index === 2) return;
  
              const cellText = cell.innerText;
              const searchIndex = cellText.toUpperCase().indexOf(keyword);
  
              if (searchIndex > -1) {
                found = true;
  
                // Resaltar texto encontrado
                const highlightedText =
                  cellText.substring(0, searchIndex) +
                  '<span style="color: red;">' +
                  cellText.substring(searchIndex, searchIndex + keyword.length) +
                  '</span>' +
                  cellText.substring(searchIndex + keyword.length);
                modifiedCells.push({ cell, highlightedText });
              }
            });
  
            if (!found) {
              shouldShow = false;
              break;
            }
          }
        }
  
        // Actualizar celdas con el texto resaltado
        modifiedCells.forEach(({ cell, highlightedText }) => {
          if (cell.getAttribute("data-label") === "Descripcion") {
            // Modificar solo el <p> dentro de la celda
            const paragraph = cell.querySelector("p");
            if (paragraph) {
              paragraph.innerHTML = highlightedText;
            }
          } else {
            // Modificar directamente el contenido de la celda
            cell.innerHTML = highlightedText;
          }
          
        });
  
        // Mostrar u ocultar la fila
        row.style.display = shouldShow ? "" : "none";
      });
    }
  }

// Evento para mostrar todas las filas al cerrar la modal
document.getElementById('tableModal').addEventListener('hidden.bs.modal', () => {
  const table = document.querySelector('#tableModal .subcategory-table table tbody');
  const rows = table.getElementsByTagName('tr');
  Array.from(rows).forEach(row => (row.style.display = ""));
  document.getElementById('searchInput').value = ""; // Limpia el campo de búsqueda
});


// // Función para asignar los event listeners a las imágenes
// function assignImageModalListeners() {
//   const modalImage = document.getElementById('modal-image');
//   const prevButton = document.getElementById('prev-image');
//   const nextButton = document.getElementById('next-image');
//   let images = [];
//   let currentIndex = 0;

//   document.querySelectorAll('img[data-bs-toggle="modal"]').forEach(img => {
//       img.addEventListener('click', function () {
//           const imageUrl = this.dataset.image;
//           images = this.dataset.images.split(',');
//           currentIndex = images.indexOf(imageUrl);

//           modalImage.src = imageUrl;
//       });
//   });

//   prevButton.addEventListener('click', function () {
//       if (currentIndex > 0) {
//           currentIndex--;
//           modalImage.src = images[currentIndex];
//       }
//   });

//   nextButton.addEventListener('click', function () {
//       if (currentIndex < images.length - 1) {
//           currentIndex++;
//           modalImage.src = images[currentIndex];
//       }
//   });
// }

// Llama a la función inicial para asignar los listeners cuando cargues la página
document.addEventListener('DOMContentLoaded', assignImageModalListeners);
