function loadPageClientes(page, per_page, search, view){

    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.page_clientes', {"page": page, "per_page": per_page, "search": search, "view": view}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#clientes").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadSummaryCliente(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_cliente_summary',{"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
             $("#clientes").html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}

function loadDetailCliente(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.detail_cliente', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#cliente-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadLotes(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_lotes', {"id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $('.lotes').html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormCliente(form){
    form = $(form);
    form.steps({
        headerTag: "h3",
        bodyTag: "fieldset",
        transitionEffect: "fade",
        enableAllSteps: true,
        autoFocus: true,
        saveState: true,
        showFinishButtonAlways: true,
        enableCancelButton: true,
        onStepChanging: function (event, currentIndex, newIndex)
        {
            if (currentIndex > newIndex)
            {
                return true;
            }
            form.validate().settings.ignore = ":disabled,:hidden";
            return form.valid();
        },
        onStepChanged: function (event, currentIndex, priorIndex)
        {

        },
        onFinishing: function (event, currentIndex)
        {
            form.validate().settings.ignore = ":disabled";
            return form.valid();
        },
        onFinished: function (event, currentIndex)
        {
            form.submit();
        },
        onCanceled: function (event) {

            if(form[0][1]['defaultValue']){
                loadSummaryCliente(form[0][1]['defaultValue']);
            }else{
                history.back();
            }
        }
    });

    loadMascaras();

    var select = $('.select').select2({
        theme: 'bootstrap-5',
        dropdownCssClass: "select2--small",
        placeholder: "Selecione...",
        allowClear: true,
        minimumInputLength: 3,
        scrollAfterSelect: true,
    });

    var selectSemPesquisa = $('.selectSemPesquisa').select2({
        theme: 'bootstrap-5',
        dropdownCssClass: "select2--small",
        placeholder: "Selecione...",
        allowClear: true,
        minimumResultsForSearch: 10,
        scrollAfterSelect: true,
    });
}


$(document).ready(function () {
    var search = '';
    var status = '';
    var i= 0;

    'use strict';

    // Search
    $('.layout-page').on('change', "select#clientes-per-page", function(){
        per_page = $(this).children("option:selected").val();
        search = $('#clientes-search').val();
        view = $('.view-ativa').attr('data-view');
        console.log(view);
        loadPageClientes(1,per_page, search, view);
    });

    $('.layout-page').on('keyup', "#clientes-search", function() {
        per_page = $('select#clientes-per-page').children("option:selected").val();
        search = $(this).val();
        view = $('.view-ativa').attr('data-view');
        loadPageClientes(1,per_page, search, view);
    });


    // View
    $('.layout-page').on('click', '.view-cliente', function(e){
        e.preventDefault();
        per_page = $('select#clientes-per-page').children("option:selected").val();
        search = $('#clientes-search').val();
        view = $(this).attr('data-view');
        loadPageClientes(1,per_page, search, view);

        $(this).addClass('active');

        if (view == 'list'){
            $('.grid').removeClass('active');
            $('.grid').removeClass('view-ativa');
            $('.list').addClass('view-ativa');
        }else{
            $('.list').removeClass('active');
            $('.list').removeClass('view-ativa');
            $('.grid').addClass('view-ativa');
        }
    });



    // Add Cliente
    $('.layout-page').on('click', '.addcliente', function(e){
        e.preventDefault();
        window.location.href = Flask.url_for('webui.new_cliente');
    });

    $('.layout-page').on('submit', "#NewClienteForm", function(e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: Flask.url_for('webui.new_cliente'),
            data: $(this).serialize(),
            beforeSend: function () {
            },
            success: function(data) {
                window.location.href = Flask.url_for('webui.cliente', {"id": data});
            },
            complete: function () {

            },
            error: function(data) {
                $(".input-error").removeClass('is-invalid')
                var errors = data['responseJSON']
                for (const key in errors) {
                    const input = document.getElementById(errors[key][0]);
                    input.classList.add('is-invalid');
                }
            }
        });

    });


    // Update Cliente
    $('.layout-page').on('click', '.editcliente', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.edit_cliente', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            console.log(data);
            $('#clientes').html(data);
          },
          complete: function () {

          },
          error: function(data) {

          }
        });
    });

    $('.layout-page').on('submit', "#UpdateClienteForm", function(e) {
        e.preventDefault();
        var id = $("#id").val()
        $.ajax({
            type: "POST",
            url: Flask.url_for('webui.edit_cliente', {"id": id}),
            data: $(this).serialize(),
            beforeSend: function () {
            },
            success: function(data) {
                loadSummaryCliente(id);
                sendNotification('Cliente atualizado com sucesso!');
            },
            complete: function () {

            },
            error: function(data) {
                $(".input-error").removeClass('is-invalid')
                var errors = data['responseJSON']
                for (const key in errors) {
                    const input = document.getElementById(errors[key][0]);
                    input.classList.add('is-invalid');
                }
            }
        });
    });


    // Delete Cliente
    $('.layout-page').on('click', '.deletecliente', function(e){
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_cliente', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            per_page = $('select#clientes-per-page').children("option:selected").val();
            search = $('#clientes-search').val();
            view = $('.view-ativa').attr('data-view');
            $('#confirmDelete').modal('hide');
            loadPageClientes(1,per_page, search, view);
            $(".toast-placement-ex .toast-body").html('Cliente excluído com sucesso');
            (c = new bootstrap.Toast(t)).show()
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });

});

