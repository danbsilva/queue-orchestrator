function loadPageLotes(page, per_page, search, view){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.page_lotes', {"page": page, "per_page": per_page, "search": search, "view": view}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#lotes").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadSummaryLote(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_lote_summary',{"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
             $("#lotes").html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}

function loadDetailLote(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.detail_lote', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadInscricoes(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_inscricoes', {"id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormInscricao(lote_id, form){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_inscricao_form', {"lote_id": lote_id}),
        beforeSend: function () {
            $(form).html('')
        },
        success: function(data) {
            $(form).html(data)
            $(".tag").tagsinput();
            $('#modalFormInscricao').modal('show');
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadEmplacamentos(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_emplacamentos', {"id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormEmplacamento(lote_id, form){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_emplacamento_form', {"lote_id": lote_id}),
        beforeSend: function () {
            $(form).html('')
        },
        success: function(data) {
            $(form).html(data)
            $(".tag").tagsinput();
            $('#modalFormEmplacamento').modal('show');
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadOcorrencias(id, page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_ocorrencias', {"id": id, "page": page}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadDocumentos(id, page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_documentos_lote', {"id": id, "page": page}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormOcorrencia(lote_id, form){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_ocorrencia_form', {"lote_id": lote_id}),
        beforeSend: function () {
            $(form).html('')
        },
        success: function(data) {
            $(form).html(data)
            $('#modalFormOcorrencia').modal('show');
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadPrestamistas(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_prestamistas', {"id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormPrestamista(lote_id, id, form){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_prestamista_form', {"lote_id": lote_id, "id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $(form).html(data)
            $('.select').select2({
                dropdownParent: $('#modalFormPrestamista'),
                theme: 'bootstrap-5',
                dropdownCssClass: "select2--small",
                tags: true,
                closeOnSelect: false,
                minimumInputLength: 3,
                placeholder: "Digte o nome do cliente"
            });
            $('#modalFormPrestamista').modal('show');
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadOrcamentos(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_orcamentos', {"id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadOrdensServicos(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_ordens_servicos', {"id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#lote-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormLote(form){
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
                loadSummaryLote(form[0][1]['defaultValue']);
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

function addFormLoteInscricao() {

    var $templateForm = $('#inscricao-_-form');
    var $tr = $templateForm.find('[data-index="_"]');
    if ($templateForm.length === 0) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    var $newForm = $templateForm.clone();

    $newForm.attr('id', replaceTemplateIndex($newForm.attr('id'), newIndex));
    $newForm.data('index', newIndex);

    $newForm.find('label, input, select, textarea').each(function(idx) {
        var $item = $(this);
        if ($item.is('label')) {
            // Update labels
            $item.attr('for', replaceTemplateIndex($item.attr('for'), newIndex));
            return;
        }

        if ($item.is('select')) {
            id_select = replaceTemplateIndex($item.attr('id'), newIndex);
            $item.addClass('selectSemPesquisa');
        }

        // Update other fields
        $item.attr('id', replaceTemplateIndex($item.attr('id'), newIndex));
        $item.attr('name', replaceTemplateIndex($item.attr('name'), newIndex));
        $item.attr('data-index', newIndex);
    });

    $newForm.find('a').attr('data-index', newIndex);

    $newForm.attr('data-index', newIndex);

    $('table#table-lote-inscricoes tbody').append($newForm);
    $newForm.addClass('subform');

    $newForm.fadeIn('slow');
    $newForm.removeClass('is-hidden');

    $('.selectSemPesquisa').select2({
        theme: 'bootstrap-5',
        dropdownCssClass: "select2--small",
        placeholder: "Selecione...",
        minimumResultsForSearch: 10,
        scrollAfterSelect: true,
    });

    loadMascaras()
}

function removeFormLoteInscricao(index) {

    var $removedForm = $('table#table-lote-inscricoes tbody').find('[data-index="' + index + '"]');
    $removedForm.remove()
    var $removedForm = $(this).closest('.subform');

    // Update indices
    adjustIndices(index);
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
    $('.layout-page').on('change',"select#lotes-per-page", function(){
        per_page = $(this).children("option:selected").val();
        search = $('#lotes-search').val();
        view = $('.view-ativa').attr('data-view');
        loadPageLotes(1,per_page, search, view);
    });

    $('.layout-page').on('keyup', "#lotes-search", function() {
        per_page = $('select#lotes-per-page').children("option:selected").val();
        search = $(this).val();
        view = $('.view-ativa').attr('data-view');
        loadPageLotes(1,per_page, search, view);
    });


    // View
    $('.layout-page').on('click', '.view-lote', function(e){
        e.preventDefault();
        per_page = $('select#lotes-per-page').children("option:selected").val();
        search = $('#lotes-search').val();
        view = $(this).attr('data-view');
        loadPageLotes(1,per_page, search, view);

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


    // Add Lote
    $('.layout-page').on('click', '.addlote', function(e){
        e.preventDefault();
        window.location.href = Flask.url_for('webui.new_lote');
    });

    $('.layout-page').on('submit', "#NewLoteForm", function(e) {
        e.preventDefault();

        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_lote'),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            window.location.href = Flask.url_for('webui.lote', {"id": data});
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


    // Update Lote
    $('.layout-page').on('click', '.editlote', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.edit_lote', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#lotes').html(data);
          },
          complete: function () {

          },
          error: function(data) {

          }
        });
    });

    $('.layout-page').on('submit',"#UpdateLoteForm", function(e) {
        e.preventDefault();
        var id = $("#id").val()
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.edit_lote', {"id": id}),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadSummaryLote(id);
            sendNotification('Lote atualizado com sucesso!');
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
    $('.layout-page').on('click', '.deletelote', function(e){
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_lote', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            per_page = $('select#lotes-per-page').children("option:selected").val();
            search = $('#lotes-search').val();
            view = $('.view-ativa').attr('data-view');
            $('#confirmDelete').modal('hide');
            loadPageLotes(1,per_page, search, view);
            sendNotification('Lote excluido com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });


    // Menus
    $('.layout-page').on('click', '.lote-informacoes', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadDetailLote(id)

    });

    $('.layout-page').on('click', '.lote-inscricoes', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadInscricoes(id)

    });

    $('.layout-page').on('click', '.lote-emplacamentos', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadEmplacamentos(id)

    });

    $('.layout-page').on('click', '.lote-prestamistas', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadPrestamistas(id)

    });

    $('.layout-page').on('click', '.lote-orcamentos', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadOrcamentos(id)

    });

    $('.layout-page').on('click', '.lote-ordens-servicos', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadOrdensServicos(id)

    });

    $('.layout-page').on('click', '.lote-ocorrencias', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadOcorrencias(id,1)

    });


    // New Prestamista
    $('.layout-page').on('click', '.addprestamista', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        loadFormPrestamista(lote_id, 0, "#NewPrestamistaForm");

    });

    $('.layout-page').on('submit','#NewPrestamistaForm', function(e) {
        e.preventDefault();
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_prestamista'),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadPrestamistas(data);
            $('#modalFormPrestamista').modal('toggle');

            sendNotification('Prestamista adicionado com sucesso!');

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

    $('.layout-page').on('click', '.deleteprestamista', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_prestamista', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#confirmDelete').modal('hide');
            loadPrestamistas(lote_id);
            sendNotification('Prestamista excluido com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });


    //Inscrições
    $('.layout-page').on('click', '.addinscricao', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        loadFormInscricao(lote_id, "#NewInscricaoForm");
    });

    $('.layout-page').on('submit','#NewInscricaoForm', function(e) {
        e.preventDefault();
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_inscricao'),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadInscricoes(data);
            $('#modalFormInscricao').modal('toggle');
            sendNotification('Inscricao adicionada com sucesso!');

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

    $('.layout-page').on('click', '.deleteinscricao', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_inscricao', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#confirmDelete').modal('hide');
            loadInscricoes(lote_id);

            sendNotification('Inscrição excluida com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });


    //Emplacamentos
    $('.layout-page').on('click', '.addemplacamento', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        loadFormEmplacamento(lote_id, "#NewEmplacamentoForm");
    });

    $('.layout-page').on('submit','#NewEmplacamentoForm', function(e) {
        e.preventDefault();
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_emplacamento'),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadEmplacamentos(data);
            $('#modalFormEmplacamento').modal('toggle');
            sendNotification('Emplacamento adicionada com sucesso!');

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

    $('.layout-page').on('click', '.deleteemplacamento', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_emplacamento', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#confirmDelete').modal('hide');
            loadEmplacamentos(lote_id);

            sendNotification('Emplacamento excluida com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });


     //Ocorrencias
    $('.layout-page').on('click', '.addocorrencia', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        loadFormOcorrencia(lote_id, "#NewOcorrenciaForm");
    });

    $('.layout-page').on('submit','#NewOcorrenciaForm', function(e) {
        e.preventDefault();
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_ocorrencia'),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadOcorrencias(data);
            $('#modalFormOcorrencia').modal('toggle');
            sendNotification('Ocrrência adicionada com sucesso!');

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

    $('.layout-page').on('click', '.deleteocorrencia', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-lote');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_ocorrencia', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#confirmDelete').modal('hide');
            loadOcorrencias(lote_id);

            sendNotification('Ocorrência excluida com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });
});

