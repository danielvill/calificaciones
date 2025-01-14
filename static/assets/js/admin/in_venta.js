// Esta es para eliminar cada input
document.addEventListener('click', function (event) {
    if (event.target.classList.contains('delete-product') || event.target.closest('.delete-product')) {
        var productEntry = event.target.closest('.product-entry');
        if (productEntry) {
            productEntry.parentNode.removeChild(productEntry);
             // Recalcular el total después de eliminar el producto
            calculateTotal();
        }
    }
});

// Esta funcion permite recalcular lo que es el total para cada input
// Esto permite cuando se borre no afecte el total eso esta muy bueno del codigo permite esta ayuda

function calculateTotal() {
    var resultados = document.querySelectorAll('input[name="resultado"]');
    var total = 0;
    resultados.forEach(function (input) {
        total += parseFloat(input.value) || 0;
    });
    document.querySelector('input[name="total"]').value = total;
}


// Función para generar identificadores únicos
function generateId() {
    return 'id-' + Math.random().toString(36).substr(2, 16);
}


// Esta parte es para que cargar mas input 

document.getElementById('add-product-btn').addEventListener('click', function () {
    var productSection = document.getElementById('product-section');
    var newProductDiv = document.createElement('div');
    var uniqueId = generateId();
    newProductDiv.className = 'row product-entry';
    newProductDiv.dataset.id = uniqueId; // Añadir identificador único
    newProductDiv.innerHTML = `
        <div class="col-md-12 col-sm-12 col-xs-12">
            <div class="col-md-3">
                <div class="form-group">
                    <label>Producto</label>
                    <input class="form-control p_nombre" name="n_productos" type="text" readonly>
                </div>
            </div>
            <div class="col-md-3" hidden >
                <div class="form-group">
                    <label>Color</label>
                    <input class="form-control color" name="color" type="text" >
                </div>
            </div>
            <div class="col-md-3" hidden >
                <div class="form-group">
                    <label>BD</label>
                    <input class="form-control cantidad" name="can" type="number">
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>Cantidad</label>
                    <input class="form-control" name="cantidad" type="number" > 
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>Precio</label>
                    <input class="form-control precio " name="precio" type="number" readonly>
                </div>
            </div>
            <div class="col-md-3">
                <div class="form-group">
                    <label>Resultado</label>
                    <input class="form-control" name="resultado" type="number" readonly>
                </div>
            </div>
            <div class="col-md-3">
                <button type="button" class="btn btn-danger delete-product">
                    <i class="glyphicon glyphicon-remove"></i> Eliminar
                </button>
                <button type="button" class="btn btn-primary but2" data-id="${uniqueId}">
                    <i class="glyphicon glyphicon-list-alt"></i>
                </button>
            </div>
            <br>
        </div>
        <br>
    `;
    productSection.appendChild(newProductDiv);

        // Multiplicacion de cantidad por resultado y total
        var cantidadInput = newProductDiv.querySelector('input[name="cantidad"]');
        var precioInput = newProductDiv.querySelector('input[name="precio"]');
        var resultadoInput = newProductDiv.querySelector('input[name="resultado"]');
        var totalInput = document.querySelector('input[name="total"]');
    
        function calculateResult() {
            var cantidad = parseFloat(cantidadInput.value) || 0;
            var precio = parseFloat(precioInput.value) || 0;
            var resultado = cantidad * precio;
            resultadoInput.value = resultado;
            calculateTotal();
        }
    
        function calculateTotal() {
            var resultados = document.querySelectorAll('input[name="resultado"]');
            var total = 0;
            resultados.forEach(function (input) {
                total += parseFloat(input.value) || 0;
            });
            totalInput.value = total;
            console.log(total);
            console.log(resultados);
        }
    
        cantidadInput.addEventListener('input', calculateResult);
        precioInput.addEventListener('input', calculateResult);
});


$('#myTable').DataTable({
    "language": {
        "url": "/static/assets/js/Spanish.json"
    }
});
// * Recuerda que estos enlaces de static y assets corresponde a las carpetas 
// que contiene los archivos para que funcione datatables

$('#myTable2').DataTable({
    "language": {
        "url": "/static/assets/js/Spanish.json"
    }
});
$(document).ready(function () {
    // Para el primer botón
    $('.but1').click(function () {
        $('.mosecliente').dialog({
            title: "Seleccionar Cliente",
            width: 500,
            modal: true
        });
    });

    
});


// Copia los datos de una celda para otra
$(document).ready(function () {
    $('#myTable tbody').on('click', 'button', function () {
        var row = $(this).closest('tr');
        var nombre = $.trim(row.find('.valor1').text());
        var apellido = $.trim(row.find('.valor2').text());
        var cedula = $.trim(row.find('.valor3').text());
        var direccion = $.trim(row.find('.valor4').text());

        $('.nombre').val(nombre);
        $('.apellido').val(apellido);
        $('.cedula').val(cedula);
        $('.direccion').val(direccion);
    });
});



$(document).ready(function () {
    // Delegación del evento click para el botón de la clase but2
    $(document).on('click', '.but2', function () {
        var uniqueId = $(this).data('id');
        $('.moseproducto').data('unique-id', uniqueId).dialog({
            title: "Seleccionar Producto",
            width: 500,
            modal: true
        });
    });

    // Delegación del evento click para los botones dentro de la tabla
    $(document).on('click', '#myTable2 tbody button', function () {
        var uniqueId = $('.moseproducto').data('unique-id');
        var row = $(this).closest('tr');
        var p_nombre = $.trim(row.find('.var1').text());
        var color = $.trim(row.find('.var2').text());
        var cantidad = $.trim(row.find('.var3').text());
        var precio = $.trim(row.find('.var4').text());

        var productEntry = $('.product-entry[data-id="' + uniqueId + '"]');
        productEntry.find('.p_nombre').val(p_nombre);
        productEntry.find('.color').val(color);
        productEntry.find('.cantidad').val(cantidad);
        productEntry.find('.precio').val(precio);
    });
});


// Este codigo permite para hacer la validacion si esta en cero algun producto eso tener presente
document.getElementById('dynamic-form').addEventListener('submit', function (event) {
    var isValid = true;
    var productEntries = document.querySelectorAll('.product-entry');

    productEntries.forEach(function (entry) {
        var canInput = entry.querySelector('input[name="can"]');
        var cantidadInput = entry.querySelector('input[name="cantidad"]');

        if (parseInt(canInput.value) === 0 && parseInt(cantidadInput.value) > 0) {
            cantidadInput.classList.add('is-invalid');
            isValid = false;
            
        } else {
            cantidadInput.classList.remove('is-invalid');
        }
    });

    if (!isValid) {
        event.preventDefault();
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No puedes enviar porque no tienes stock de uno o más productos.'
        });
    }
});