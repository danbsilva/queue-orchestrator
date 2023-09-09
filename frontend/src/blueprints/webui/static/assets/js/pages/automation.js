function loadPageLoteadores(page, per_page, search, view){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.page_loteadores', {"page": page, "per_page": per_page, "search": search, "view": view}),
        beforeSend: function () {
        },
        success: function(data) {
            console.log(data);
            $("#loteadores").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadSummaryLoteador(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_loteador_summary',{"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
             $("#loteadores").html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}

function loadDetailLoteador(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.detail_loteador', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#loteador-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormLoteador(form){
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
            console.log(form.validate());
            form.validate().settings.ignore = ":disabled";
            return form.valid();
        },
        onFinished: function (event, currentIndex)
        {
            form.submit();
        },
        onCanceled: function (event) {
            if(form[0][1]['defaultValue']){
                loadSummaryLoteador(form[0][1]['defaultValue']);
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
    'use strict';

    var selectedloteamento = '';
    var selectederaverbada = '';
    var selectedtopografia = '';
    var selectededificacao = '';
    var selectedstatus = '';
    var selectedclientes = ''

    var search = ''

    var i = 0;

    // Search
    $('.layout-page').on('change',"select#loteadores-per-page", function(){
        per_page = $(this).children("option:selected").val();
        search = $('#loteadores-search').val();
        view = $('.view-ativa').attr('data-view');
        loadPageLoteadores(1,per_page, search, view);
    });

    $('.layout-page').on('keyup', "#loteadores-search", function() {
        per_page = $('select#lotes-per-page').children("option:selected").val();
        search = $(this).val();
        view = $('.view-ativa').attr('data-view');
        loadPageLoteadores(1,per_page, search, view);
    });


    // View
    $('.layout-page').on('click', '.view-loteador', function(e){
        e.preventDefault();
        per_page = $('select#loteadores-per-page').children("option:selected").val();
        search = $('#loteadores-search').val();
        view = $(this).attr('data-view');
        loadPageLoteadores(1,per_page, search, view);

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


    // Add Loteador
    $('.layout-page').on('click', '.addloteador', function(e){
        e.preventDefault();
        window.location.href = Flask.url_for('webui.new_loteador');
    });

    $('.layout-page').on('submit', "#NewLoteadorForm", function(e) {
        e.preventDefault();

        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_loteador'),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            window.location.href = Flask.url_for('webui.loteador', {"id": data});
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


    // Update Loteador
    $('.layout-page').on('click', '.editloteador', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.edit_loteador', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#loteadores').html(data);
          },
          complete: function () {

          },
          error: function(data) {

          }
        });
    });

    $('.layout-page').on('submit',"#UpdateLoteadorForm", function(e) {
        e.preventDefault();
        var id = $("#id").val()
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.edit_loteador', {"id": id}),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadSummaryLoteador(id);
            sendNotification('Loteador atualizado com sucesso!');
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


    // Delete Lote
    $('.layout-page').on('click', '.deleteloteador', function(e){
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_loteador', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            per_page = $('select#loteadores-per-page').children("option:selected").val();
            search = $('#loteadores-search').val();
            view = $('.view-ativa').attr('data-view');
            $('#confirmDelete').modal('hide');
            loadPageLoteadores(1,per_page, search, view);
            sendNotification('Loteador excluido com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });


    // Menus
    $('.layout-page').on('click', '.loteador-informacoes', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadDetailLoteador(id)

    });

});

