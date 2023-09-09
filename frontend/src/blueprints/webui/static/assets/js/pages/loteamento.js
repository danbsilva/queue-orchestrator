function loadPageLoteamentos(page, per_page, search, view){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.page_loteamentos', {"page": page, "per_page": per_page, "search": search, "view": view}),
        beforeSend: function () {
        },
        success: function(data) {
            console.log(data);
            $("#loteamentos").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadSummaryLoteamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_loteamento_summary',{"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
             $("#loteamentos").html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}

function loadDetailLoteamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.detail_loteamento', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#loteamento-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormLoteamento(form){
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
                loadSummaryLoteamento(form[0][1]['defaultValue']);
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
    $('.layout-page').on('change',"select#loteamentos-per-page", function(){
        per_page = $(this).children("option:selected").val();
        search = $('#loteamentos-search').val();
        view = $('.view-ativa').attr('data-view');
        loadPageLotementos(1,per_page, search, view);
    });

    $('.layout-page').on('keyup', "#loteamentos-search", function() {
        per_page = $('select#loteamentos-per-page').children("option:selected").val();
        search = $(this).val();
        view = $('.view-ativa').attr('data-view');
        loadPageLoteamentos(1,per_page, search, view);
    });


    // View
    $('.layout-page').on('click', '.view-loteamento', function(e){
        e.preventDefault();
        per_page = $('select#loteamentos-per-page').children("option:selected").val();
        search = $('#loteamentos-search').val();
        view = $(this).attr('data-view');
        loadPageLoteamentos(1,per_page, search, view);

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


    // Add loteamento
    $('.layout-page').on('click', '.addloteamento', function(e){
        e.preventDefault();
        window.location.href = Flask.url_for('webui.new_loteamento');
    });

    $('.layout-page').on('submit', "#NewLoteamentoForm", function(e) {
        e.preventDefault();

        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_loteamento'),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            window.location.href = Flask.url_for('webui.loteamento', {"id": data});
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


    // Update loteamento
    $('.layout-page').on('click', '.editloteamento', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.edit_loteamento', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#loteamentos').html(data);
          },
          complete: function () {

          },
          error: function(data) {

          }
        });
    });

    $('.layout-page').on('submit',"#UpdateLoteamentoForm", function(e) {
        e.preventDefault();
        var id = $("#id").val()
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.edit_loteamento', {"id": id}),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadSummaryLoteamento(id);
            sendNotification('Loteamento atualizado com sucesso!');
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
    $('.layout-page').on('click', '.deleteloteamento', function(e){
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_loteamento', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            per_page = $('select#loteamentos-per-page').children("option:selected").val();
            search = $('#loteamentos-search').val();
            view = $('.view-ativa').attr('data-view');
            $('#confirmDelete').modal('hide');
            loadPageLoteamentos(1,per_page, search, view);
            sendNotification('Loteamento excluido com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });


    // Menus
    $('.layout-page').on('click', '.loteamento-informacoes', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadDetailLoteamento(id)

    });

});

