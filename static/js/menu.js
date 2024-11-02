function cargarModulo(url) {
    fetch(url)
        .then((response) => {
            if (!response.ok) {
                throw new Error("La respuesta de la red no era correcta");
            }
            return response.text();
        })
        .then((data) => {
            document.querySelector(".content").innerHTML = data; // Cargar contenido en el área de contenido

            // Espera breve antes de registrar eventos para asegurar que el DOM esté listo
            setTimeout(registrarEventosModulo, 50);
        })
        .catch((error) => {
            console.error("Hubo un problema con la solicitud Fetch:", error);
            document.querySelector(".content").innerHTML = "<p>Error al cargar el módulo</p>";
        });
}

function saveCurrentModule(url) {
    sessionStorage.setItem("lastModule", url); // Guardar la URL del módulo actual
}

function registrarEventosModulo() {
    console.log("Intentando registrar eventos para el módulo cargado"); // Debug log

    // Events specific to dashboard2 elements
    const cantidadElement = document.getElementById("cantidad");
    const precioElement = document.getElementById("precio");
    const totalElement = document.getElementById("total");
    if (cantidadElement && precioElement && totalElement) {
        console.log("Registrando eventos para los campos de cantidad y precio en dashboard2"); // Debug log
        cantidadElement.addEventListener("input", calcularTotal);
        precioElement.addEventListener("input", calcularTotal);
    }

    const registrarButton = document.getElementById("registrar-button");
    if (registrarButton) {
        registrarButton.addEventListener("click", function (e) {
            e.preventDefault();
            console.log("Evento de click en Registrar Venta activado"); // Debug log
            const boleta = document.getElementById("boleta").value;
            const codigo = document.getElementById("codigo").value;
            const cantidad = document.getElementById("cantidad").value;
            const precio = document.getElementById("precio").value;
            const total = document.getElementById("total").value;
            const tienda = document.getElementById("tienda").value;
            const fecha = new Date().toLocaleString();
            const usuario = "Usuario Ejemplo"; // Cambiar según el usuario logueado
            const cliente = "Cliente Ejemplo"; // Cambiar según el cliente seleccionado

            const newRow = `<tr>
                <td>${boleta}</td>
                <td>${codigo}</td>
                <td>${cantidad}</td>
                <td>${precio}</td>
                <td>${total}</td>
                <td>${tienda}</td>
                <td>${fecha}</td>
                <td>${usuario}</td>
                <td>${cliente}</td>
            </tr>`;
            const salesBody = document.getElementById("sales-body");
            if (salesBody) {
                salesBody.insertAdjacentHTML("beforeend", newRow);
                document.getElementById("sales-container").style.display = "block";
                console.log("Venta registrada en la tabla"); // Debug log
            }
        });
    }

    const cancelarButton = document.getElementById("cancelar-button");
    if (cancelarButton) {
        cancelarButton.addEventListener("click", function () {
            const salesForm = document.getElementById("sales-form");
            if (salesForm) {
                salesForm.reset();
                document.getElementById("total").value = "";
                document.getElementById("sales-container").style.display = "none";
                console.log("Formulario de ventas cancelado y limpiado"); // Debug log
            }
        });
    }

    // Chart Rendering
    const chartElement = document.getElementById("sales-chart");
    if (chartElement) {
        console.log("Renderizando gráfico de ventas"); // Debug log
        renderSalesChart();
    }

    // New functionality for form configuration
    const formatoSelect = document.getElementById("formato");
    if (formatoSelect) {
        formatoSelect.addEventListener("change", function () {
            const separadorContainer = document.getElementById("separador-container");
            separadorContainer.style.display = this.value === "csv" || this.value === "txt" ? "block" : "none";
        });
    }

    const agregarCampoButton = document.getElementById("agregar-campo");
    if (agregarCampoButton) {
        agregarCampoButton.addEventListener("click", function () {
            const row = `
                <tr>
                    <td><input type="text" placeholder="Ingrese nombre del campo"></td>
                    <td>
                        <select>
                            <option value="texto">Texto</option>
                            <option value="numerico">Numérico</option>
                            <option value="decimal">Decimal</option>
                            <option value="fecha">Fecha</option>
                            <option value="otro">Otro</option>
                        </select>
                    </td>
                    <td><input type="checkbox"></td>
                    <td><button type="button" class="delete-row">Eliminar</button></td>
                </tr>
            `;
            document.getElementById("campos-body").insertAdjacentHTML("beforeend", row);
            setDeleteRowEvent();
        });
    }

    function setDeleteRowEvent() {
        document.querySelectorAll(".delete-row").forEach(button => {
            button.addEventListener("click", function () {
                this.closest("tr").remove();
            });
        });
    }

    setDeleteRowEvent();

    const guardarConfigButton = document.getElementById("guardar-config");
    if (guardarConfigButton) {
        guardarConfigButton.addEventListener("click", function () {
            alert("Configuración guardada con éxito.");
        });
    }

    const ejecutarButton = document.getElementById("ejecutar");
    if (ejecutarButton) {
        ejecutarButton.addEventListener("click", function () {
            alert("Ejecución en proceso...");
        });
    }

    const cancelarConfigButton = document.getElementById("cancelar");
    if (cancelarConfigButton) {
        cancelarConfigButton.addEventListener("click", function () {
            document.getElementById("config-form").reset();
            document.getElementById("separador-container").style.display = "none";
        });
    }
}

function calcularTotal() {
    const cantidadElement = document.getElementById("cantidad");
    const precioElement = document.getElementById("precio");
    const totalElement = document.getElementById("total");

    console.log("Ejecutando calcularTotal"); // Debug log
    if (cantidadElement && precioElement && totalElement) {
        const cantidad = parseInt(cantidadElement.value);
        const precio = parseFloat(precioElement.value.replace(/,/g, ""));
        if (!isNaN(cantidad) && !isNaN(precio)) {
            const total = cantidad * precio;
            totalElement.value = total.toLocaleString("es-CL", {
                style: "currency",
                currency: "CLP"
            });
        } else {
            totalElement.value = "";
        }
    }
}

function renderSalesChart() {
    const ctx = document.getElementById("sales-chart").getContext("2d");

    if (window.salesChart) {
        window.salesChart.destroy(); // Eliminar el gráfico anterior si existe
    }

    const labels = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
    const ventasDiarias = [8, 12, 9, 11, 7, 10, 15];
    const metaDiaria = 10;

    window.salesChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Ventas Diarias",
                    data: ventasDiarias,
                    borderColor: "rgba(52, 152, 219, 1)",
                    backgroundColor: "rgba(52, 152, 219, 0.2)",
                    fill: true
                },
                {
                    label: "Meta Diaria",
                    data: labels.map(() => metaDiaria),
                    borderColor: "rgba(231, 76, 60, 1)",
                    backgroundColor: "rgba(231, 76, 60, 0.2)",
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "top" },
                title: { display: true, text: "Comparación de Ventas Diarias con la Meta" }
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");
    const currentTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", currentTheme);

    themeToggle.textContent = currentTheme === "dark" ? "Modo Claro" : "Modo Oscuro";
    themeToggle.addEventListener("click", function () {
        let theme = document.documentElement.getAttribute("data-theme");
        if (theme === "light") {
            document.documentElement.setAttribute("data-theme", "dark");
            localStorage.setItem("theme", "dark");
            themeToggle.textContent = "Modo Claro";
        } else {
            document.documentElement.setAttribute("data-theme", "light");
            localStorage.setItem("theme", "light");
            themeToggle.textContent = "Modo Oscuro";
        }
    });

    const links = document.querySelectorAll(".navbar > ul > li > a");
    const submenuLinks = document.querySelectorAll(".submenu a");
    links.forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const submenu = this.nextElementSibling;
            if (submenu) {
                document.querySelectorAll(".submenu").forEach((sm) => {
                    if (sm !== submenu) sm.style.display = "none";
                });
                submenu.style.display = submenu.style.display === "block" ? "none" : "block";
            } else {
                document.querySelectorAll(".submenu").forEach((sm) => (sm.style.display = "none"));
            }
        });
    });

    submenuLinks.forEach((submenuLink) => {
        submenuLink.addEventListener("click", function (e) {
            e.preventDefault();
            const url = this.getAttribute("href");
            if (url) {
                cargarModulo(url);
                saveCurrentModule(url);
            }
        });
    });

    registrarEventosModulo(); // Register events for the initial load
});
document.getElementById("cancelar").addEventListener("click", function () {
  // Reinicia el formulario, limpiando todos los campos de entrada
  document.getElementById("config-form").reset();
  
  // Oculta el contenedor de separador si está visible
  document.getElementById("separador-container").style.display = "none";
  
  // Elimina todas las filas agregadas dinámicamente en la tabla de campos
  const camposBody = document.getElementById("campos-body");
  while (camposBody.rows.length > 1) { // Mantener solo la primera fila por defecto
      camposBody.deleteRow(1);
  }
  
  // Limpia los campos de fecha y los checkboxes de días de la semana
  document.getElementById("fecha-inicio").value = "";
  document.getElementById("fecha-fin").value = "";
  document.querySelectorAll(".checkbox-group input[type='checkbox']").forEach(checkbox => {
      checkbox.checked = false;
  });
});
document.getElementById('crearUsuarioForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creando...';

    const formData = new FormData(this);
    try {
        const response = await fetch('{{ url_for("crear_usuario") }}', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.status === 'success') {
            alert(data.message);
            window.location.href = '{{ url_for("menu") }}';
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error al enviar el formulario:', error);
        alert('Hubo un error al crear el usuario.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Crear Usuario';
    }
});

// formulario de creación de usuarios.

function actualizarTiendas() {
    const tiendasPorCliente = {
        "99": [{ id: 0, nombre: "Dummy" }],
        "1": [
            { id: 0, nombre: "Dummy" },
            { id: 1, nombre: "Ahumada" },
            { id: 2, nombre: "Costanera Center" },
            { id: 3, nombre: "Parque Arauco" }
        ],
        "2": [
            { id: 0, nombre: "Dummy" },
            { id: 4, nombre: "Ahumada" }
        ],
        "3": [{ id: 0, nombre: "Dummy" }],  // Sin tiendas asignadas
        "4": [
            { id: 0, nombre: "Dummy" },
            { id: 1, nombre: "Parque Arauco" },
            { id: 2, nombre: "Costanera Center" }
        ]
    };

    const idCliente = document.getElementById('id_clt')?.value;
    const idTdaSelect = document.getElementById('id_tda');
    
    if (!idCliente || !idTdaSelect) {
        console.warn("No se pudo encontrar el elemento id_clt o id_tda");
        return;
    }

    idTdaSelect.innerHTML = ''; 

    if (tiendasPorCliente[idCliente]) {
        tiendasPorCliente[idCliente].forEach(tienda => {
            const option = document.createElement('option');
            option.value = tienda.id;
            option.textContent = tienda.nombre;
            idTdaSelect.appendChild(option);
        });
    } else {
        const dummyOption = document.createElement('option');
        dummyOption.value = '0';
        dummyOption.textContent = 'Dummy';
        idTdaSelect.appendChild(dummyOption);
    }
}

// Asegúrate de que `actualizarTiendas` se ejecute cuando se cambie el cliente
document.addEventListener("DOMContentLoaded", function() {
    const idClienteSelect = document.getElementById('id_clt');
    if (idClienteSelect) {
        idClienteSelect.addEventListener('change', actualizarTiendas);
    } else {
        console.warn("El elemento con id 'id_clt' no se encontró en el DOM.");
    }
});

// Envío del formulario de creación de usuarios

document.getElementById('crearUsuarioForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creando...';

    const formData = new FormData(this);
    try {
        const response = await fetch('/mod/mAdmcreusr', {
            method: 'POST',
            body: formData
        });

        const contentType = response.headers.get("content-type");
        let data;
        if (contentType && contentType.includes("application/json")) {
            data = await response.json();
        } else {
            throw new Error("La respuesta no es JSON.");
        }

        // Mostrar el mensaje en el contenedor dentro del HTML
        const mensajeConfirmacion = document.getElementById('mensajeConfirmacion');
        mensajeConfirmacion.textContent = data.message;
        mensajeConfirmacion.style.display = 'block';

        // Cambia la clase según el estado de la respuesta
        if (data.status === 'success') {
            mensajeConfirmacion.classList.add('alert-success');
            mensajeConfirmacion.classList.remove('alert-danger');
        } else {
            mensajeConfirmacion.classList.add('alert-danger');
            mensajeConfirmacion.classList.remove('alert-success');
        }
    } catch (error) {
        console.error('Error al enviar el formulario:', error);
        const mensajeConfirmacion = document.getElementById('mensajeConfirmacion');
        mensajeConfirmacion.textContent = 'Hubo un error al crear el usuario.';
        mensajeConfirmacion.classList.add('alert-danger');
        mensajeConfirmacion.style.display = 'block';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Crear Usuario';
    }
});