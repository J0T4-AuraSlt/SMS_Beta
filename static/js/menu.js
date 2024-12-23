console.log("menu.js cargado correctamente"); 

// 05/11/24
// function cargarModulo(url) {
//     fetch(url)
//         .then((response) => {
//             if (!response.ok) {
//                 throw new Error("La respuesta de la red no era correcta");
//             }
//             return response.text();
//         })
//         .then((data) => {
//             document.querySelector(".content").innerHTML = data; // Cargar contenido en el área de contenido

//             // Espera breve antes de registrar eventos para asegurar que el DOM esté listo
//             setTimeout(() => {
//                 registrarEventosModulo();
//                 registrarEventoCrearUsuario();  // Registrar el evento submit para crear usuario
//             }, 50);
//         })
//         .catch((error) => {
//             console.error("Hubo un problema con la solicitud Fetch:", error);
//             document.querySelector(".content").innerHTML = "<p>Error al cargar el módulo</p>";
//         });
// }

// function saveCurrentModule(url) {
//     sessionStorage.setItem("lastModule", url); // Guardar la URL del módulo actual
// }

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
// Creacion de usuario document.addEventListener("DOMContentLoaded", registrarEventoCrearUsuario);

// function registrarEventoCrearUsuario() {
//     const crearUsuarioForm = document.getElementById("crearUsuarioForm");
//     if (crearUsuarioForm) {
//         crearUsuarioForm.addEventListener("submit", async function (event) {
//             event.preventDefault();
//             prepararDatos();

//             const submitBtn = document.getElementById("submitBtn");
//             submitBtn.disabled = true;
//             submitBtn.textContent = "Creando...";

//             const formData = new FormData(this);

//             try {
//                 const response = await fetch("/mod/mAdmcreusr", {
//                     method: "POST",
//                     body: formData,
//                     headers: {
//                         "X-Requested-With": "XMLHttpRequest"
//                     },
//                 });

//                 if (response.ok) {
//                     const result = await response.json();
//                     showPopup(result.message, result.status === "success" ? "success" : "error");
//                 } else {
//                     showPopup("Error en la creación, verifique los campos ingresados.", "error");
//                 }
//             } catch (error) {
//                 showPopup("Hubo un error al crear el usuario.", "error");
//             } finally {
//                 submitBtn.disabled = false;
//                 submitBtn.textContent = "Crear Usuario";
//             }
//         });
//     }
// }

// function showPopup(message, type = 'success') {
//     const popup = document.getElementById("popup");
//     const popupMessage = document.getElementById("popup-message");

//     popupMessage.innerText = message;
//     popup.className = `fade-in ${type}`;
//     popup.style.display = "block";

//     setTimeout(() => {
//         popup.classList.add("fade-out");
//         setTimeout(() => {
//             popup.style.display = "none";
//             popup.classList.remove("fade-in", "fade-out", "success", "error");
//         }, 300);
//     }, 3000);
// }

// function prepararDatos() {
//     const rutCompleto = document.getElementById("rut").value;
//     const [rut, dv] = rutCompleto.split("-");
//     document.getElementById("rut_usr").value = rut || "";
//     document.getElementById("dv_usr").value = dv || "";

//     const apellidos = document.getElementById("apellidos").value.split(" ");
//     document.getElementById("ape_pat_usr").value = apellidos[0] || "";
//     document.getElementById("ape_mat_usr").value = apellidos[1] || "";
// }

//Propuesta 30 del GPT
document.addEventListener("DOMContentLoaded", () => {
    const crearUsuarioForm = document.getElementById("crearUsuarioForm");
    
    if (crearUsuarioForm) {
        crearUsuarioForm.addEventListener("submit", async function(event) {
            event.preventDefault();
            prepararDatos(); // Procesar RUT y Apellidos

            const submitBtn = document.getElementById("submitBtn");
            submitBtn.disabled = true;
            submitBtn.textContent = "Creando...";

            const formData = new FormData(this);

            try {
                const response = await fetch(this.action, {  
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    },
                });

                const data = await response.json();
                if (response.ok) {
                    // Aquí mostramos solo el mensaje en el pop-up
                    showPopup(data.message, data.status === "success" ? "success" : "error");
                } else {
                    showPopup("Error en la creación, verifique los campos ingresados.", "error");
                }
            } catch (error) {
                console.error("Error al enviar el formulario:", error);
                showPopup("Hubo un error al crear el usuario.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = "Crear Usuario";
            }
        });
    }
});

// Función para mostrar solo el mensaje en un pop-up o en pantalla
function showPopup(message, status) {
    const popup = document.getElementById("popup");
    const popupMessage = document.getElementById("popup-message");

    popupMessage.textContent = message;
    popup.classList.remove("success", "error");
    popup.classList.add(status);
    popup.style.display = "block";

    setTimeout(() => {
        popup.style.display = "none";
    }, 3000);
}

function closePopup() {
    document.getElementById("popup").style.display = "none";
}

function prepararDatos() {
    const rut = document.getElementById("rut").value;
    const [rutNum, dv] = rut.split("-");
    document.getElementById("rut_usr").value = rutNum;
    document.getElementById("dv_usr").value = dv;

    const apellidos = document.getElementById("apellidos").value.split(" ");
    document.getElementById("ape_pat_usr").value = apellidos[0];
    document.getElementById("ape_mat_usr").value = apellidos[1] || "";
}

// creación de usuarios, version new
// function registrarEventoCrearUsuario() {
//     const crearUsuarioForm = document.getElementById("crearUsuarioForm");
//     if (crearUsuarioForm) {
//         crearUsuarioForm.addEventListener("submit", async function (event) {
//             event.preventDefault(); // Evita el envío normal del formulario
//             prepararDatos();

//             const submitBtn = document.getElementById("submitBtn");
//             submitBtn.disabled = true;
//             submitBtn.textContent = "Creando...";

//             const formData = new FormData(this);

//             try {
//                 const response = await fetch("/mod/mAdmcreusr", {
//                     method: "POST",
//                     body: formData,
//                     headers: {
//                         "X-Requested-With": "XMLHttpRequest" // Indica una solicitud AJAX
//                     },
//                 });

//                 // Verifica que la respuesta sea JSON
//                 if (response.ok && response.headers.get("content-type").includes("application/json")) {
//                     const data = await response.json();
//                     if (data.status === "success") {
//                         showPopup("Usuario creado con éxito", "success");
//                     } else {
//                         showPopup(data.message || "Error en la creación del usuario", "error");
//                     }
//                 } else {
//                     showPopup("Error en la creación, verifique los campos ingresados.", "error");
//                 }
//             } catch (error) {
//                 console.error("Error al enviar el formulario:", error);
//                 showPopup("Hubo un error al crear el usuario.", "error");
//             } finally {
//                 submitBtn.disabled = false;
//                 submitBtn.textContent = "Crear Usuario";
//             }
//         });
//     }
// }

// function showPopup(message, type) {
//     const popup = document.getElementById("popup");
//     const popupMessage = document.getElementById("popup-message");

//     popupMessage.textContent = message;
//     popupMessage.className = type; // Añadir clase para estilos de éxito o error
//     popup.style.display = "block"; // Muestra el pop-up

//     // Cierra el pop-up automáticamente después de unos segundos
//     setTimeout(() => {
//         popup.style.display = "none";
//     }, 3000);
// }

// function closePopup() {
//     const popup = document.getElementById("popup");
//     popup.style.display = "none";
// }

// function prepararDatos() {
//     const rutCompleto = document.getElementById("rut").value;
//     const [rut, dv] = rutCompleto.split("-");
//     document.getElementById("rut_usr").value = rut || "";
//     document.getElementById("dv_usr").value = dv || "";

//     const apellidos = document.getElementById("apellidos").value.split(" ");
//     document.getElementById("ape_pat_usr").value = apellidos[0] || "";
//     document.getElementById("ape_mat_usr").value = apellidos[1] || "";
// }

// function showPopup(message, type = 'success') {
//     const popup = document.getElementById("popup");
//     const popupMessage = document.getElementById("popup-message");

//     popupMessage.innerText = message;
//     popup.className = `fade-in ${type}`;
//     popup.style.display = "block";

//     setTimeout(() => {
//         popup.classList.add("fade-out");
//         setTimeout(() => {
//             popup.style.display = "none";
//             popup.classList.remove("fade-in", "fade-out", "success", "error");
//         }, 300);
//     }, 3000);
// }


// Configuración del gráfico de "Product Statistic"
const productStatCtx = document.getElementById('product-stat-chart').getContext('2d');
new Chart(productStatCtx, {
    type: 'doughnut',
    data: {
        labels: ['Electrónica', 'Juegos', 'Muebles'],
        datasets: [{
            data: [2487, 1828, 1063],
            backgroundColor: ['#4e73df', '#1cc88a', '#e74a3b'],
            hoverOffset: 4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.label + ': ' + tooltipItem.raw.toLocaleString();
                    }
                }
            }
        }
    }
});

// Configuración del gráfico de "Customer Habits"
const customerHabitsCtx = document.getElementById('customer-habits-chart').getContext('2d');
new Chart(customerHabitsCtx, {
    type: 'bar',
    data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul'],
        datasets: [
            {
                label: 'Productos vistos',
                data: [45000, 50000, 55000, 40000, 30000, 52000, 48000],
                backgroundColor: '#4e73df'
            },
            {
                label: 'Ventas',
                data: [39000, 42000, 43000, 38000, 34000, 45000, 47000],
                backgroundColor: '#1cc88a'
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
// Configuración del gráfico de "Segmento de Tienda"
const storeSegmentCtx = document.getElementById('store-segment-chart').getContext('2d');
new Chart(storeSegmentCtx, {
    type: 'pie',
    data: {
        labels: ['Mall', 'Sucursal', 'Retail'],
        datasets: [{
            data: [4500, 3000, 2500], // Datos ficticios de visitas
            backgroundColor: ['#4e73df', '#1cc88a', '#e74a3b'],
            hoverOffset: 4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return tooltipItem.label + ': ' + tooltipItem.raw.toLocaleString();
                    }
                }
            }
        }
    }
});

// Formatear la fecha al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const fechaElement = document.querySelector('.current-date');
    const fechaActual = new Date();
    const opcionesFecha = { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' };
    
    // Obtener la fecha formateada con el mes corto
    let fechaFormateada = fechaActual.toLocaleDateString('es-ES', opcionesFecha);
    
    // Añadir el punto al mes abreviado
    fechaFormateada = fechaFormateada.replace(/\b(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\b/, '$&.');

    fechaElement.textContent = fechaFormateada;
});

// document.addEventListener('DOMContentLoaded', () => {
//     const fechaElement = document.querySelector('.current-date');
//     const fechaActual = new Date();
//     const opcionesFecha = { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' };
//     fechaElement.textContent = fechaActual.toLocaleDateString('es-ES', opcionesFecha);
// });

// Cambiar Tema
// const themeToggleButton = document.getElementById('theme-toggle');
// themeToggleButton.addEventListener('click', () => {
//     document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
// });


// document.addEventListener("DOMContentLoaded", function () {
//     const themeToggle = document.getElementById("theme-toggle");
//     const currentTheme = localStorage.getItem("theme") || "light";
//     document.documentElement.setAttribute("data-theme", currentTheme);

//     themeToggle.textContent = currentTheme === "dark" ? "Modo Claro" : "Modo Oscuro";
//     themeToggle.addEventListener("click", function () {
//         let theme = document.documentElement.getAttribute("data-theme");
//         if (theme === "light") {
//             document.documentElement.setAttribute("data-theme", "dark");
//             localStorage.setItem("theme", "dark");
//             themeToggle.textContent = "Modo Claro";
//         } else {
//             document.documentElement.setAttribute("data-theme", "light");
//             localStorage.setItem("theme", "light");
//             themeToggle.textContent = "Modo Oscuro";
//         }
//     });

//     const links = document.querySelectorAll(".navbar > ul > li > a");
//     const submenuLinks = document.querySelectorAll(".submenu a");
//     links.forEach((link) => {
//         link.addEventListener("click", function (e) {
//             e.preventDefault();
//             const submenu = this.nextElementSibling;
//             if (submenu) {
//                 document.querySelectorAll(".submenu").forEach((sm) => {
//                     if (sm !== submenu) sm.style.display = "none";
//                 });
//                 submenu.style.display = submenu.style.display === "block" ? "none" : "block";
//             } else {
//                 document.querySelectorAll(".submenu").forEach((sm) => (sm.style.display = "none"));
//             }
//         });
//     });

//     submenuLinks.forEach((submenuLink) => {
//         submenuLink.addEventListener("click", function (e) {
//             e.preventDefault();
//             const url = this.getAttribute("href");
//             if (url) {
//                 cargarModulo(url);
//                 saveCurrentModule(url);
//             }
//         });
//     });

//     registrarEventosModulo(); // Register events for the initial load
//     registrarEventoCrearUsuario(); // Registrar evento para el formulario de creación de usuario
// });

document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");
    const currentTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", currentTheme);

    // Establecer el icono inicial según el tema
    themeToggle.className = currentTheme === "dark" ? "fas fa-sun" : "fas fa-moon";

    themeToggle.addEventListener("click", function () {
        // Alternar entre temas claro y oscuro
        let theme = document.documentElement.getAttribute("data-theme");
        if (theme === "light") {
            document.documentElement.setAttribute("data-theme", "dark");
            localStorage.setItem("theme", "dark");
            themeToggle.className = "fas fa-sun"; // Cambiar a icono de sol para modo oscuro
        } else {
            document.documentElement.setAttribute("data-theme", "light");
            localStorage.setItem("theme", "light");
            themeToggle.className = "fas fa-moon"; // Cambiar a icono de luna para modo claro
        }
    });

    // Configuración de submenús en el menú de navegación
    const links = document.querySelectorAll(".navbar > ul > li > a");
    const submenuLinks = document.querySelectorAll(".submenu a");
    links.forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const submenu = this.nextElementSibling;
            if (submenu) {
                // Ocultar otros submenús al abrir uno nuevo
                document.querySelectorAll(".submenu").forEach((sm) => {
                    if (sm !== submenu) sm.style.display = "none";
                });
                submenu.style.display = submenu.style.display === "block" ? "none" : "block";
            } else {
                // Cerrar todos los submenús si no hay un submenu asociado
                document.querySelectorAll(".submenu").forEach((sm) => (sm.style.display = "none"));
            }
        });
    });

    // Enlaces de los submenús y carga de módulos
    submenuLinks.forEach((submenuLink) => {
        submenuLink.addEventListener("click", function (e) {
            e.preventDefault();
            const url = this.getAttribute("href");
            if (url) {
                cargarModulo(url); // Llamada a la función para cargar módulo
                saveCurrentModule(url); // Guardar estado del módulo actual
            }
        });
    });

    // Registrar eventos adicionales
    registrarEventosModulo(); // Registro de eventos para carga inicial
    registrarEventoCrearUsuario(); // Registro para formulario de creación de usuario
});

// Modulo Restablecer Usuarios
// Función para cargar el módulo solo cuando el usuario lo seleccione en el menú
function cargarModulo(url) {
    fetch(url)
        .then((response) => {
            if (!response.ok) throw new Error("La respuesta de la red no era correcta");
            return response.text();
        })
        .then((data) => {
            document.querySelector(".content").innerHTML = data;

            // Observador para esperar a que el módulo esté completamente cargado
            const observer = new MutationObserver((mutations, obs) => {
                if (document.querySelector("#userTable tbody")) {  // Confirma que el tbody de la tabla está en el DOM
                    obs.disconnect();
                    obtenerUsuarios(); // Llama a la función para cargar los usuarios solo si el módulo es madmrstpwd
                }
            });
            observer.observe(document.querySelector(".content"), { childList: true, subtree: true });
        })
        .catch((error) => {
            console.error("Hubo un problema con la solicitud Fetch:", error);
            document.querySelector(".content").innerHTML = "<p>Error al cargar el módulo</p>";
        });
}

// Función para obtener usuarios (solo se usa cuando se carga el módulo de usuarios)
async function obtenerUsuarios() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/api_get_users');
        
        if (!response.ok) {
            throw new Error("Error en la conexión con el servidor");
        }
        
        const result = await response.json();
        console.log(result);  // Verificación de datos en la consola

        if (result.status === 'success' && result.data) {
            populateTable(result.data);
        } else {
            alert('Error al cargar los usuarios.');
        }
    } catch (error) {
        console.error('Error en la solicitud:', error);
        alert('No se pudo conectar con el servidor.');
    }
}

// Función para llenar la tabla con los usuarios obtenidos
function populateTable(users) {
    const tbody = document.querySelector('#userTable tbody'); 

    if (!tbody) {
        console.error("El elemento <tbody> no se encontró en el DOM. Verifica el id 'userTable' en el HTML.");
        return;
    }

    tbody.innerHTML = ''; 

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="checkbox" value="${user.usuario}"></td>
            <td>${user.usuario}</td>
            <td>${user.nombre_completo}</td>
            <td>${user.email}</td>
            <td>${user.rut_usr}</td>
            <td>${user.tienda_usr}</td>
            <td>${user.status}</td>
            <td>${user.perfil || 'N/A'}</td>
            <td>${user.fecha_ult_cambio}</td>
            <td>${user.fecha_expira}</td>
        `;
        tbody.appendChild(row);
    });
}

// Almacenar el módulo actual en sessionStorage
function saveCurrentModule(url) {
    sessionStorage.setItem("lastModule", url);
}

async function executeAction(action) {
    const selectedUsers = Array.from(document.querySelectorAll('#userTable input[type="checkbox"]:checked')).map(input => input.value);
    
    if (selectedUsers.length === 0) {
        alert('Por favor, selecciona al menos un usuario.');
        return;
    }

    const data = { action, users: selectedUsers };

    // Si la acción es "reset_password", pedir nueva contraseña
    if (action === 'reset_password') {
        const newPassword = prompt('Ingresa la nueva contraseña:');
        if (!newPassword) {
            alert("Contraseña no ingresada.");
            return;
        }
        data.newPassword = newPassword;
    }
    
    try {
        const response = await fetch('/api/manage_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.status === 'success') {
            alert(result.message);
            location.reload(); // Recargar la lista de usuarios después de la acción
        } else {
            alert('Error en la acción: ' + result.message);
        }
    } catch (error) {
        console.error('Error en la solicitud:', error);
        alert('No se pudo realizar la acción.');
    }
}
// // Escuchar el evento DOMContentLoaded y cargar el módulo de usuarios
// document.addEventListener('DOMContentLoaded', () => {
//     cargarModulo('/mod/mAdmrstpwd'); // Carga inicial del módulo
// });

// function cargarModulo(url) {
//     fetch(url)
//         .then((response) => {
//             if (!response.ok) throw new Error("La respuesta de la red no era correcta");
//             return response.text();
//         })
//         .then((data) => {
//             document.querySelector(".content").innerHTML = data;

//             // Observador para esperar a que el módulo esté completamente cargado
//             const observer = new MutationObserver((mutations, obs) => {
//                 if (document.querySelector("#userTable tbody")) {  // Confirma que el tbody de la tabla está en el DOM
//                     obs.disconnect();
//                     obtenerUsuarios(); // Llama a la función para cargar los usuarios
//                 }
//             });
//             observer.observe(document.querySelector(".content"), { childList: true, subtree: true });
//         })
//         .catch((error) => {
//             console.error("Hubo un problema con la solicitud Fetch:", error);
//             document.querySelector(".content").innerHTML = "<p>Error al cargar el módulo</p>";
//         });
// }

// // Función para obtener usuarios
// async function obtenerUsuarios() {
//     try {
//         const response = await fetch('http://127.0.0.1:5000/api/api_get_users');
        
//         if (!response.ok) {
//             throw new Error("Error en la conexión con el servidor");
//         }
        
//         const result = await response.json();
//         console.log(result);  // Verificación de datos en la consola

//         if (result.status === 'success' && result.data) {
//             populateTable(result.data);
//         } else {
//             alert('Error al cargar los usuarios.');
//         }
//     } catch (error) {
//         console.error('Error en la solicitud:', error);
//         alert('No se pudo conectar con el servidor.');
//     }
// }

// // Función para llenar la tabla con los usuarios obtenidos
// function populateTable(users) {
//     const tbody = document.querySelector('#userTable tbody'); 

//     if (!tbody) {
//         console.error("El elemento <tbody> no se encontró en el DOM. Verifica el id 'userTable' en el HTML.");
//         return;
//     }

//     tbody.innerHTML = ''; 

//     users.forEach(user => {
//         const row = document.createElement('tr');
//         row.innerHTML = `
//             <td><input type="checkbox" value="${user.usuario}"></td>
//             <td>${user.usuario}</td>
//             <td>${user.nombre_completo}</td>
//             <td>${user.email}</td>
//             <td>${user.rut_usr}</td>
//             <td>${user.tienda_usr}</td>
//             <td>${user.status}</td>
//             <td>${user.perfil || 'N/A'}</td>
//             <td>${user.fecha_ult_cambio}</td>
//             <td>${user.fecha_expira}</td>
//         `;
//         tbody.appendChild(row);
//     });
// }