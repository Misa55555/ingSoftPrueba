// Cargar productos desde localStorage
function getProductos() {
    return JSON.parse(localStorage.getItem("productos")) || [];
  }
  
  // Guardar productos
  function saveProductos(productos) {
    localStorage.setItem("productos", JSON.stringify(productos));
  }
  
  // === COMPRAS ===
    if (document.getElementById("form-compra")) {
        document.getElementById("form-compra").addEventListener("submit", (e) => {
        e.preventDefault();
      const nuevo = {
        nombre: document.getElementById("nombre").value,
        id: document.getElementById("id").value,
        cantidad: parseInt(document.getElementById("cantidad").value),
        unidad: document.getElementById("unidad").value,
        precioCompra: parseFloat(document.getElementById("precioCompra").value),
        precioVenta: parseFloat(document.getElementById("precioVenta").value)
    };
  
    let productos = getProductos();
    // Filtrar productos activos (con cantidad > 0)
    productos = productos.filter(p => p.cantidad > 0);

    // Validar ID duplicado
      if (productos.some(p => p.id === nuevo.id)) {
        alert("⚠️ Ya existe un producto con ese ID.");
        return;
      }

  
      productos.push(nuevo);
      saveProductos(productos);
      alert("✅ Producto agregado correctamente");
      e.target.reset();


      // Actualizar tabla sin recargar
      const fila = document.createElement("tr");
      fila.innerHTML = `
      <td>${nuevo.nombre}</td>
      <td>${nuevo.id}</td>
      <td>${nuevo.cantidad}</td>
      <td>${nuevo.unidad}</td>
      <td>$${nuevo.precioCompra.toFixed(2)}</td>
      <td>$${nuevo.precioVenta.toFixed(2)}</td>
      `;
document.getElementById("tabla-stock").appendChild(fila);


    });
}
  
// === VENTAS ===
if (document.getElementById("form-venta")) {
  document.getElementById("form-venta").addEventListener("submit", (e) => {
    e.preventDefault();
    const id = document.getElementById("venta-id").value;
    const vendidas = parseInt(document.getElementById("venta-cantidad").value);

    let productos = getProductos();
    const index = productos.findIndex(p => p.id === id);

    if (index === -1) {
      alert("❌ Producto no encontrado.");
      return;
    }

    if (productos[index].cantidad < vendidas) {
      alert("⚠️ No hay suficientes unidades.");
      return;
    }


    // ✅ Guardar copia del producto antes de modificarlo
    const copiaProducto = { ...productos[index] };

    // Restar unidades
    productos[index].cantidad -= vendidas;

    // Registrar la venta con la copia original
    registrarVenta(copiaProducto, vendidas);

    // Eliminar si queda en cero
    if (productos[index].cantidad === 0) {
      productos.splice(index, 1);
    }

    // Guardar cambios
    saveProductos(productos);
    alert("✅ Venta registrada correctamente.");
    e.target.reset();
  });
}

  

//   REGISTRAR VENTA PARA EL HISTORIAL
function registrarVenta(producto, unidadesVendidas) {
    const ventas = JSON.parse(localStorage.getItem("ventas")) || [];
    const fechaHora = new Date().toLocaleString();
  
    ventas.push({
      id: producto.id,
      nombre: producto.nombre,
      cantidadVendida: unidadesVendidas,
      unidad: producto.unidad,
      precioCompra: producto.precioCompra,
      precioVenta: producto.precioVenta,
      fechaHora: fechaHora
    });
  
    localStorage.setItem("ventas", JSON.stringify(ventas));
  }
  
  
// === MOSTRAR STOCK EN LA MISMA PÁGINA DE COMPRAS ===
if (document.getElementById("tabla-stock")) {
  const tbody = document.getElementById("tabla-stock");
  const productos = getProductos();

  productos
    .filter(p => p.cantidad > 0)
    .forEach(p => {
      const fila = document.createElement("tr");
      fila.innerHTML = `
        <td>${p.nombre}</td>
        <td>${p.id}</td>
        <td>${p.cantidad}</td>
        <td>${p.unidad}</td>
        <td>$${p.precioCompra.toFixed(2)}</td>
        <td>$${p.precioVenta.toFixed(2)}</td>
      `;
      tbody.appendChild(fila);
    });
}



// === HISTORIAL DE VENTAS ===
if (document.getElementById("tabla-historial-ventas")) {
  const ventas = JSON.parse(localStorage.getItem("ventas")) || [];
  const tbody = document.getElementById("tabla-historial-ventas");

  // Mostrar la última venta primero (sin modificar permanentemente el array original)
  [...ventas].reverse().forEach(v => {
    const fila = document.createElement("tr");
    fila.innerHTML = `
      <td>${v.fechaHora}</td>
      <td>${v.id}</td>
      <td>${v.nombre}</td>
      <td>${v.cantidadVendida}</td>
      <td>${v.unidad}</td>
      <td>$${v.precioCompra.toFixed(2)}</td>
      <td>$${v.precioVenta.toFixed(2)}</td>
    `;
    tbody.appendChild(fila);
  });
}


//   BOTON PARA BORRAR EL LOCAL STORAGE DE LA APP Y QUE SE RESETEE EL HISTORIAL DE PRODUCTOS POR AHORA, DESPUES BORRAR
  function resetearApp() {
    if (confirm("¿Estás seguro de que querés borrar todo el sistema?")) {
      localStorage.clear();
      alert("✅ Sistema reiniciado. Refrescá la página para ver los cambios.");
      location.reload(); // refresca la página
    }
  }
  

// === CONTROL MODAL FORMULARIO ===
const modal = document.getElementById("modal");
const btnAbrir = document.getElementById("abrir-formulario");
const btnCerrar = document.querySelector(".cerrar");

if (btnAbrir && modal && btnCerrar) {
  btnAbrir.onclick = () => modal.style.display = "block";
  btnCerrar.onclick = () => modal.style.display = "none";
  window.onclick = (e) => {
    if (e.target === modal) modal.style.display = "none";
  };
}
