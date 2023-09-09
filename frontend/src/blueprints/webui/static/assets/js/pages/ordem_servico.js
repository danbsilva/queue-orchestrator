function loadPageOrdensServicos(page, per_page, search, view){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.page_ordens_servicos', {"page": page, "per_page": per_page, "search": search, "view": view}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#ordens-servicos").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadSummaryOrdemServico(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_ordem_servico_summary',{"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
             $("#ordens-servicos").html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}

function loadDetailOrdemServico(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.detail_ordem_servico', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#ordem-servico").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadPagamentosOrdemServico(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_pagamentos_ordem_servico', {"id": id}),
        beforeSend: function () {

        },
        success: function(data) {
            $("#ordem-servico").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadClienteOrdemServico(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_cliente_ordem_servico', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
           $("#ordem-servico").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadLoteOrdemServico(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_lote_ordem_servico', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#ordem-servico").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadServicosOrdemServico(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_servicos_ordem_servico', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#ordem-servico").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormOrdemServico(form){
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
            if(newIndex == 4){
                //loadResumoOrcamento();
            }
            form.validate().settings.ignore = ":disabled,:hidden";
            return form.valid();
        },
        onStepChanged: function (event, currentIndex, priorIndex)
        {

        },
        onFinishing: function (event, currentIndex)
        {
            console.log(form);
            form.validate().settings.ignore = ":disabled";
            console.log(form.validate());
            return form.valid();
        },
        onFinished: function (event, currentIndex)
        {
           console.log(form);
           form.submit();

        },
        onCanceled: function (event) {
            if(form[0][1]['defaultValue']){
                loadSummaryOrcamento(form[0][1]['defaultValue']);
            }else{
                history.back();
            }

        }
    });

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
    loadMascaras();
}

function addFormOrdemServicoPagamento(vencimento, parcela, valor) {

    var $templateForm = $('#pagamento-_-form');
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
    $newForm.find('span').attr('data-index', newIndex);

    $newForm.attr('data-index', newIndex);


    $('table#table-orcamento-item tbody').append($newForm);
    $newForm.addClass('subform');

    $newForm.fadeIn('slow');
    $newForm.removeClass('is-hidden');

    $newForm.find('.vencimento').val(vencimento);
    $newForm.find('.parcela').val(parcela);
    $newForm.find('.valor').val(valor);

    $newForm.find('.vencimento').html(formatarData(vencimento));
    $newForm.find('.parcela').html(parcela);
    $newForm.find('.valor').html(valor);

    $('.selectSemPesquisa').select2({
        theme: 'bootstrap-5',
        dropdownCssClass: "select2--small",
        placeholder: "Selecione...",
        minimumResultsForSearch: 10,
        scrollAfterSelect: true,
    });

    loadMascaras()
}

function geraParcelas(){
    var nrParcelas = $('.layout-page #parcelas').children("option:selected").val();
    var dt1Parcela = $('.layout-page #data_primeira_parcela').val();
    var valorTotal = $('.layout-page #total').val();
    var parcela = moeda2float(valorTotal)/nrParcelas;
    var dias = 1;

    if (dt1Parcela == ''){
        var dt1Parcela = new Date();
    }
    $('table#table-orcamento-item tbody').html('');

    for (let i = 0; i < nrParcelas; i++) {
        vencimento = adicionarDiasData(dt1Parcela, dias)
        addFormOrdemServicoPagamento(vencimento, i+1, float2moeda(parcela));
        dias = dias + 31
    }
}


$(document).ready(function () {

    'use strict';

    // Search
    $('.layout-page').on('change', 'select#parcelas', function(e){
        e.preventDefault();
         geraParcelas();

    });

    $('.layout-page').on('change', '#data_primeira_parcela', function(e){
        e.preventDefault();
         geraParcelas();

    });

    $('.layout-page').on('change', '[name=tipo_pagamento]', function(e){
        e.preventDefault();
        var id = $('#id').val();
        var $checked = $('[name=tipo_pagamento]:checked');
        var value = $checked.val();

        if(value=='Parcelado'){
            $.ajax({
              type: "GET",
              url: Flask.url_for('webui.get_parcelado_form', {'id':id}),
              beforeSend: function () {
              },
              success: function(data) {
                $('#form_pagamento').html(data);
                geraParcelas();
              },
              complete: function () {

              },
              error: function(data) {

              }
            });

        }else{
            $.ajax({
              type: "GET",
              url: Flask.url_for('webui.get_a_vista_form', {'id':id}),
              beforeSend: function () {
              },
              success: function(data) {
                $('#form_pagamento').html(data);
                geraParcelas();
              },
              complete: function () {

              },
              error: function(data) {

              }
            });
        }

    });

    $('.layout-page').on('click', '.new-ordem-servico', function(e){
        e.preventDefault();
        var orcamento_id = $(this).attr("data-id");
        var csrf = $(this).attr("data-csrf");
        var json = {orcamento_id: orcamento_id};
        console.log(json);
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_ordem_servico'),
          data: json,
          beforeSend : function(jqXHR, settings) {
                jqXHR.setRequestHeader("x-csrftoken", csrf);
          },
          success: function(data) {
            $('#confirm').modal('hide');
            window.location.href = Flask.url_for('webui.edit_ordem_servico', {'id': data});
          },
          complete: function () {
          },
          error: function(data) {
          }
        });
    });


     // Update Ordem de Serviço
     $('.layout-page').on('click', '.editordemservico', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.edit_ordem_servico', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            console.log(data);
            $('#ordens-servicos').html(data);
          },
          complete: function () {

          },
          error: function(data) {

          }
        });
    });

    $('.layout-page').on('submit',"#UpdateOrdemServicoForm", function(e) {
        e.preventDefault();
        var id = $("#id").val()
        var status = $('.layout-page #status').children("option:selected").val();

        console.log(id);
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.edit_ordem_servico', {"id": id}),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            loadSummaryOrcamento(id);
            sendNotification('Orçamento atualizado com sucesso!');
            setTimeout(function(){
            if(status=='Aprovado'){
                var orcamento = $(this).attr("data-id");
                $('#yes').attr("data-id", id);
                $('#yes').attr("data-status", status);
                $('#yes').addClass('new-ordem-servico');
                $('.modal-body').html('Devido ao orçamento está aprovado, vamos gerar uma ordem de serviço com base neste orçamento');
                $('#confirm').modal('show');
            }
        }, 500);
          },
          complete: function () {

          },
          error: function(data) {
            $(".input-error").removeClass('is-invalid')
            var errors = data['responseJSON']
            for (const key in errors) {
                sendNotification(errors[key][0]);
                const input = document.getElementById(errors[key][0]);
                input.classList.add('is-invalid');
            }
          }
        });

    });

    // Delete Ordem de Serviço
    $('.layout-page').on('click', '.deleteordemservico', function(e){
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_ordem_servico', {"id": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            per_page = $('select#ordens-servicos-per-page').children("option:selected").val();
            search = $('#ordens-servicos-search').val();
            view = $('.view-ativa').attr('data-view');
            $('#confirmDelete').modal('hide');
            loadPageOrdensServicos(1,per_page, search, view);
            sendNotification('Ordem de Serviço excluido com sucesso!');
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });

    // Menus
    $('.layout-page').on('click', '.ordem-servico-informacoes', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadDetailOrdemServico(id)

    });

    $('.layout-page').on('click', '.ordem-servico-cliente', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadClienteOrdemServico(id)

    });

    $('.layout-page').on('click', '.ordem-servico-lote', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadLoteOrdemServico(id)

    });

    $('.layout-page').on('click', '.ordem-servico-servicos', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadServicosOrdemServico(id)

    });

    $('.layout-page').on('click', '.ordem-servico-pagamentos', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadPagamentosOrdemServico(id)

    });

});

