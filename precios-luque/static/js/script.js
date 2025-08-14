
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

function searchArtic3(inputId = "searchInput", containerId = "tableModal") {
  function highlightOccurrences(text, keyword) {
    const regex = new RegExp(keyword, "gi");
    return text.replace(regex, match => `<span style="color: red;">${match}</span>`);
  }

  // Nueva función de puntuación por similitud basada en substring exacta
  function smartSimilarityScore(input, text) {
    input = input.toLowerCase().replace(/\s+/g, '');
    text = text.toLowerCase().replace(/\s+/g, '');

    if (text === input) return 1000; // máxima similitud
    if (text.includes(input)) return 800 + input.length;
    if (input.includes(text)) return 500;
    if (text.startsWith(input)) return 600;
    if (text.endsWith(input)) return 550;

    let matchLength = 0;
    for (let i = 0; i < text.length; i++) {
      if (input.includes(text[i])) {
        matchLength++;
      }
    }
    return matchLength;
  }

  const input = document.getElementById(inputId);
  if (!input) return;

  const filter = input.value.trim();
  const table = document.querySelector(`#${containerId} .subcategory-table table tbody`);
  if (!table) return;

  const rows = Array.from(table.getElementsByTagName('tr'));

  if (!filter) {
    rows.forEach(row => {
      row.style.display = "";
      const descripcionCell = row.querySelector('[data-label="Descripcion"] p');
      if (descripcionCell) {
        descripcionCell.innerHTML = descripcionCell.textContent;
      }
    });
    return;
  }

  const keywords = filter.split(/\s+/).filter(Boolean);
  const matchedRows = [];

  for (let row of rows) {
    const descripcionCell = row.querySelector('[data-label="Descripcion"]');
    if (!descripcionCell) continue;

    const text = descripcionCell.innerText;
    const textUpper = text.toUpperCase();

    const matchesAll = keywords.every(keyword =>
      textUpper.includes(keyword.toUpperCase())
    );

    if (matchesAll) {
      const score = smartSimilarityScore(filter, text);
      matchedRows.push({ row, descripcionCell, score });
    } else {
      row.style.display = "none";
    }
  }

  // Ordenar por mayor puntaje de similitud
  matchedRows.sort((a, b) => b.score - a.score);

  for (let { row, descripcionCell } of matchedRows) {
    let highlightedContent = descripcionCell.innerHTML;
    for (let keyword of keywords) {
      highlightedContent = highlightOccurrences(highlightedContent, keyword);
    }

    const pTag = descripcionCell.querySelector("p");
    if (pTag) {
      pTag.innerHTML = highlightedContent;
    } else {
      descripcionCell.innerHTML = highlightedContent;
    }

    row.style.display = "";
    table.appendChild(row); // Reordenar visualmente la tabla
  }
}


// function searchArtic3(inputId = "searchInput", containerId = "tableModal") {
//   // Función auxiliar para resaltar todas las ocurrencias de una palabra clave en un texto.
//   function highlightOccurrences(text, keyword) {
//     const regex = new RegExp(keyword, "gi"); // global e insensible a mayúsculas
//     return text.replace(regex, match => `<span style="color: red;">${match}</span>`);
//   }
  
//   const input = document.getElementById(inputId);
//   if (!input) return; // Si no existe el input, salir
  
//   const filter = input.value.trim();
//   const table = document.querySelector(`#${containerId} .subcategory-table table tbody`);
//   if (!table) return; // Si no existe la tabla, salir
  
//   const rows = table.getElementsByTagName('tr');
  
//   // Si el filtro está vacío, se muestran todas las filas
//   if (!filter) {
//     Array.from(rows).forEach(row => {
//       row.style.display = "";
//       // Opcional: restaurar contenido original si se hubiera modificado
//     });
//     return;
//   }
  
//   // Se obtienen las palabras clave tal como fueron ingresadas
//   const keywords = filter.split(/\s+/).filter(Boolean);
//   const rowsArray = Array.from(rows);
  
//   // Procesar cada fila individualmente
//   for (let row of rowsArray) {
//     let rowMatches = true;
    
//     // Extraer información de cada celda: contenido original, texto sin HTML, índice y si es "Descripcion"
//     let cellData = Array.from(row.children).map((cell, index) => ({
//       element: cell,
//       originalContent: cell.innerHTML,
//       text: cell.innerText,
//       index: index,
//       isDescripcion: cell.getAttribute("data-label") === "Descripcion"
//     }));
    
//     // Primero: validar que cada palabra clave se encuentre en alguna de las celdas permitidas (omitiendo la columna de "Precio" índice 2)
//     for (let keyword of keywords) {
//       let keywordUpper = keyword.toUpperCase();
//       let foundKeyword = false;
      
//       for (let data of cellData) {
//         if (data.index === 2) continue; // omitir columna "Precio"
//         if (data.text.toUpperCase().indexOf(keywordUpper) > -1) {
//           foundKeyword = true;
//           break;
//         }
//       }
      
//       if (!foundKeyword) {
//         rowMatches = false;
//         break;
//       }
//     }
    
//     // Si la fila cumple con que todas las palabras clave se encuentran en alguna celda...
//     if (rowMatches) {
//       // Recorremos las celdas y aplicamos el resaltado acumulativo a cada una
//       cellData.forEach(data => {
//         // Omitir la columna "Precio"
//         if (data.index === 2 || data.index === 3) return;
        
//         // Partir del contenido original y aplicar los resaltados para todas las keywords
//         let highlightedContent = data.originalContent;
//         for (let keyword of keywords) {
//           highlightedContent = highlightOccurrences(highlightedContent, keyword);
//         }
        
//         // Si la celda es de "Descripcion", actualizar el contenido del <p> interno
//         if (data.isDescripcion) {
//           let paragraph = data.element.querySelector("p");
//           if (paragraph) {
//             paragraph.innerHTML = highlightedContent;
//           }
//         } else {
//           data.element.innerHTML = highlightedContent;
//         }
//       });
      
//       row.style.display = ""; // Mostrar fila
//     } else {
//       row.style.display = "none"; // Ocultar fila si alguna keyword no se encuentra
//     }
//   }
// }


// function searchArtic3(inputId = "searchInput", containerId = "tableModal") {
//   function highlightOccurrences(text, keyword) {
//     // Crear una expresión regular global e insensible a mayúsculas
//     const regex = new RegExp(keyword, "gi");
//     // Reemplazar todas las coincidencias con un <span> de color rojo
//     return text.replace(regex, match => `<span style="color: red;">${match}</span>`);
//   }
  

//   const input = document.getElementById(inputId);
//   if (!input) return; // Evitar errores si el input no existe

//   const filter = input.value.trim().toUpperCase();
//   const table = document.querySelector(`#${containerId} .subcategory-table table tbody`);
//   if (!table) return; // Evitar errores si la tabla no existe

//   const rows = table.getElementsByTagName('tr');

//   // Si no hay filtro, mostrar todas las filas
//   if (!filter) {
//     Array.from(rows).forEach(row => (row.style.display = ""));
//     return;
//   }

//   const keywords = filter.split(/\s+/); // Usar expresión regular para evitar espacios vacíos
//   const rowsArray = Array.from(rows); 

//   // Procesar todas las filas en un solo bucle
//   for (let row of rowsArray) {
//     let shouldShow = true;
//     let modifiedCells = [];
    
//     // Obtener el texto de todas las celdas en una sola pasada
//     let cells = Array.from(row.children).map((cell, index) => {
//       return {
//         element: cell,
//         text: cell.innerText.toUpperCase(),
//         index: index,
//         isDescripcion: cell.getAttribute("data-label") === "Descripcion"
//       };
//     });

//     for (let keyword of keywords) {
//       if (!keyword) continue;
//       let found = false;

//       // for (let cell of cells) {
//       //   if (cell.index === 2) continue; // Omitir la columna "Precio"
//       //   const searchIndex = cell.text.indexOf(keyword);

//       //   if (searchIndex > -1) {
//       //     found = true;
//       //     // Almacenar la modificación sin modificar el DOM aún
//       //     let highlightedText =
//       //       cell.text.substring(0, searchIndex) +
//       //       '<span style="color: red;">' +
//       //       cell.text.substring(searchIndex, searchIndex + keyword.length) +
//       //       '</span>' +
//       //       cell.text.substring(searchIndex + keyword.length);

//       //     modifiedCells.push({ cell, highlightedText });
//       //   }
//       // }

//       for (let cell of cells) {
//         if (cell.index === 2) continue; // Omitir la columna "Precio"
        
//         // Obtener el contenido original de la celda
//         const originalContent = cell.element.innerHTML;
//         let modifiedContent = originalContent;
//         let found = false;
        
//         // Para cada palabra clave, resaltar todas sus ocurrencias
//         for (let keyword of keywords) {
//           if (!keyword) continue;
          
//           // Comprobar si la palabra clave existe en el contenido (busqueda insensible a mayúsculas)
//           if (new RegExp(keyword, "i").test(modifiedContent)) {
//             // Resaltar todas las ocurrencias en el contenido
//             modifiedContent = highlightOccurrences(modifiedContent, keyword);
//             found = true;
//           }
//         }
        
//         if (found) {
//           // Guardar la celda modificada para actualizarla posteriormente
//           modifiedCells.push({ cell, highlightedText: modifiedContent });
//         }
//       }

//       if (!found) {
//         shouldShow = false;
//         break;
//       }
//     }

//     // Aplicar cambios al DOM después de procesar todo
//     if (shouldShow) {
//       modifiedCells.forEach(({ cell, highlightedText }) => {
//         if (cell.isDescripcion) {
//           let paragraph = cell.element.querySelector("p");
//           if (paragraph) {
//             paragraph.innerHTML = highlightedText;
//           }
//         } else {
//           cell.element.innerHTML = highlightedText;
//         }
//       });
//     }

//     row.style.display = shouldShow ? "" : "none";
//   }
// }

// function searchArtic3(inputId = "searchInput", containerId = "tableModal", ) {
//   console.log(containerId)
//   console.log(inputId)
//   const input = document.getElementById(inputId);
//   console.log(input)
//     const filter = input.value.toUpperCase();
    
//     const table = document.querySelector(`#${containerId} .subcategory-table table tbody`);
//     const rows = table.getElementsByTagName('tr');
  
//     if (filter === "") {
//       // Muestra todas las filas si el input está vacío
//       Array.from(rows).forEach(row => (row.style.display = ""));
//     } else {
//       const keywords = filter.split(' ');
  
//       Array.from(rows).forEach(row => {
//         let shouldShow = true;
//         const cells = Array.from(row.children);
//         let modifiedCells = [];
  
//         for (let keyword of keywords) {
//           if (keyword !== "" && keyword !== " ") {
//             let found = false;
  
//             cells.forEach((cell, index) => {
//               // Omitir la columna "Precio" (índice 2)
//               if (index === 2) return;
  
//               const cellText = cell.innerText;
//               const searchIndex = cellText.toUpperCase().indexOf(keyword);
  
//               if (searchIndex > -1) {
//                 found = true;
  
//                 // Resaltar texto encontrado
//                 const highlightedText =
//                   cellText.substring(0, searchIndex) +
//                   '<span style="color: red;">' +
//                   cellText.substring(searchIndex, searchIndex + keyword.length) +
//                   '</span>' +
//                   cellText.substring(searchIndex + keyword.length);
//                 modifiedCells.push({ cell, highlightedText });
//               }
//             });
  
//             if (!found) {
//               shouldShow = false;
//               break;
//             }
//           }
//         }
  
//         // Actualizar celdas con el texto resaltado
//         modifiedCells.forEach(({ cell, highlightedText }) => {
//           if (cell.getAttribute("data-label") === "Descripcion") {
//             // Modificar solo el <p> dentro de la celda
//             const paragraph = cell.querySelector("p");
//             if (paragraph) {
//               paragraph.innerHTML = highlightedText;
//             }
//           } else {
//             // Modificar directamente el contenido de la celda
//             cell.innerHTML = highlightedText;
//           }
          
//         });
  
//         // Mostrar u ocultar la fila
//         row.style.display = shouldShow ? "" : "none";
//       });
//     }
//   }

// Evento para mostrar todas las filas al cerrar la modal
document.getElementById('tableModal').addEventListener('hidden.bs.modal', () => {
  const table = document.querySelector('#tableModal .subcategory-table table tbody');
  const rows = table.getElementsByTagName('tr');
  Array.from(rows).forEach(row => (row.style.display = ""));
  document.getElementById('searchInput').value = ""; // Limpia el campo de búsqueda
});




// Llama a la función inicial para asignar los listeners cuando cargues la página
document.addEventListener('DOMContentLoaded', assignImageModalListeners);
