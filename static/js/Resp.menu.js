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
  
        // Registra los eventos para el módulo cargado
        registrarEventosModulo();
      })
      .catch((error) => {
        console.error("Hubo un problema con la solicitud Fetch:", error);
        document.querySelector(".content").innerHTML =
          "<p>Error al cargar el módulo</p>";
      });
  }
  
  function saveCurrentModule(url) {
    sessionStorage.setItem("lastModule", url); // Guardar la URL del módulo actual
  }
  
  function registrarEventosModulo() {
    if (document.getElementById("analyze-button")) {
      document
        .getElementById("analyze-button")
        .addEventListener("click", function () {
          const product = document.getElementById("product").value;
          const startDate = document.getElementById("start-date").value;
          const endDate = document.getElementById("end-date").value;
  
          if (!product || !startDate || !endDate) {
            alert("Por favor, complete todos los campos del formulario.");
            return;
          }
  
          const productData = {
            peak: 150,
            average: 80,
            min: 20,
            sales: [20, 50, 70, 100, 150, 90, 60],
          };
  
          const generalSalesData = {
            peak: 200,
            average: 120,
            min: 30,
            sales: [30, 60, 90, 120, 200, 150, 100],
          };
  
          document.getElementById("product-peak").innerText = productData.peak;
          document.getElementById("product-average").innerText =
            productData.average;
          document.getElementById("product-min").innerText = productData.min;
  
          document.getElementById("general-peak").innerText = generalSalesData.peak;
          document.getElementById("general-average").innerText =
            generalSalesData.average;
          document.getElementById("general-min").innerText = generalSalesData.min;
  
          const ctx = document.getElementById("sales-chart").getContext("2d");
  
          if (window.salesChart) {
            window.salesChart.destroy();
          }
  
          window.salesChart = new Chart(ctx, {
            type: "line",
            data: {
              labels: [
                "Semana 1",
                "Semana 2",
                "Semana 3",
                "Semana 4",
                "Semana 5",
                "Semana 6",
                "Semana 7",
              ],
              datasets: [
                {
                  label: "Producto Seleccionado",
                  data: productData.sales,
                  borderColor: "rgba(52, 152, 219, 1)",
                  backgroundColor: "rgba(52, 152, 219, 0.2)",
                  fill: true,
                },
                {
                  label: "Ventas Generales",
                  data: generalSalesData.sales,
                  borderColor: "rgba(231, 76, 60, 1)",
                  backgroundColor: "rgba(231, 76, 60, 0.2)",
                  fill: true,
                },
              ],
            },
            options: {
              responsive: true,
              plugins: {
                legend: {
                  position: "top",
                },
                title: {
                  display: true,
                  text: "Comparación de Ventas",
                },
              },
            },
          });
        });
    }
  }
  
  document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");
  
    const currentTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", currentTheme);
  
    themeToggle.textContent =
      currentTheme === "dark" ? "Modo Claro" : "Modo Oscuro";
  
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
            if (sm !== submenu) {
              sm.style.display = "none";
            }
          });
  
          submenu.style.display =
            submenu.style.display === "block" ? "none" : "block";
        } else {
          document
            .querySelectorAll(".submenu")
            .forEach((sm) => (sm.style.display = "none"));
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
  
    registrarEventosModulo();
  });
  ///dashboard2

  
// Events for dashboard2 elements and specific modules related to sales
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

document.addEventListener("DOMContentLoaded", function () {
  console.log("Contenido cargado, inicializando eventos"); // Debug log

  // Only attach events if the dashboard2 elements are present
  const cantidad = document.getElementById("cantidad");
  const precio = document.getElementById("precio");
  if (cantidad && precio) {
      console.log("Registrando eventos para cantidad y precio"); // Debug log
      cantidad.addEventListener("input", calcularTotal);
      precio.addEventListener("input", calcularTotal);
  }

  const registrarButton = document.getElementById("registrar-button");
  if (registrarButton) {
      console.log("Registrando evento para el botón registrar"); // Debug log
      registrarButton.addEventListener("click", function (e) {
          e.preventDefault();
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
      console.log("Registrando evento para el botón cancelar"); // Debug log
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

  // Sales Chart Rendering
  const chartElement = document.getElementById("sales-chart");
  if (chartElement) {
      console.log("Renderizando gráfico de ventas"); // Debug log
      renderSalesChart();
  }
});
