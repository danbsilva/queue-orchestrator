function loadPageOrcamentos(page, per_page, search, view){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.page_orcamentos', {"page": page, "per_page": per_page, "search": search, "view": view}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#orcamentos").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadSummaryOrcamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_orcamento_summary',{"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
             $("#orcamentos").html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}

function loadDetailOrcamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.detail_orcamento', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#orcamento-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadClienteOrcamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_cliente_orcamento', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#orcamento-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadLoteOrcamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_lote_orcamento', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#orcamento-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadServicosOrcamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_servicos_orcamento', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#orcamento-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadHistoryOrcamento(id){
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.all_historico_orcamento', {"id": id}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#orcamento-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}

function loadFormOrcamento(form){
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
                loadResumoOrcamento();
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

function loadInfocliente(id){
    if(id>0){
        $.ajax({
            type: "GET",
            url: Flask.url_for('webui.get_cliente_info',{"id": id}),
            beforeSend: function () {
            },
            success: function(data) {
                 $(".cliente").html(data);
            },
            complete: function () {

            },
            error: function(data) {

            }
        });
    }else{
        $(".cliente").html('');
    }
}

function addFormOrcamentoItem() {

    var $templateForm = $('#item-_-form');
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


    $('table#table-orcamento-item tbody').append($newForm);
    $newForm.addClass('subform');

    $newForm.fadeIn('slow');
    $newForm.removeClass('is-hidden');

    $newForm.find('.servico').attr('required', 'required');
    $newForm.find('.valor').attr('required', 'required');
    $newForm.find('.subtotal').attr('required', 'required');

    $('.selectSemPesquisa').select2({
        theme: 'bootstrap-5',
        dropdownCssClass: "select2--small",
        placeholder: "Selecione...",
        minimumResultsForSearch: 10,
        scrollAfterSelect: true,
    });

    loadMascaras()
}

function removeFormOrcamentoItem(index) {

    var $removedForm = $('table#table-orcamento-item tbody').find('[data-index="' + index + '"]');
    $removedForm.remove()
    var $removedForm = $(this).closest('.subform');

    // Update indices
    adjustIndices(index);
}

function loadResumoOrcamento(){
    prev_entrega = $('.layout-page #previsao_entrega').val()
    table_orcamento = '<table class="table table-sm table-bordered">';
    table_orcamento += '<tr class="bg-tr">';
    table_orcamento += '<th colspan="2">Previsão de Entrega: ' + formatarData(prev_entrega) + '</th>';
    table_orcamento += '</tr>';
    table_orcamento += '</table>';
    $('.layout-page #resumo-orcamento').html(table_orcamento);

    var cliente_id = $('.layout-page #cliente').children("option:selected").val();

    table_cliente = '<table class="table table-sm table-bordered">';
    table_cliente += '<tr class="bg-tr">';

    table_cliente += '<th colspan="2">Informação do Cliente</th>';

    if(cliente_id > 0){
        cliente = $(".layout-page #cliente").children("option:selected").text()
        table_cliente += '</tr>';
        table_cliente += '<tr>';
        table_cliente += '<th>Cliente</th>';
        table_cliente += '<td>' + cliente + '</td>';
        table_cliente += '</tr>';
    }else{
        table_cliente += '<tr>';
        table_cliente += '<td>Sem informação</td>';
        table_cliente += '</tr>';
    }

    table_cliente += '</table>';
    $('.layout-page #resumo-cliente').html(table_cliente);

    var lote_id = $('.layout-page #lote').children("option:selected").val();
    var codigo;
    var lote;
    var quadra;
    var area;
    $.ajax({
        type: "GET",
        url: Flask.url_for('webui.get_lote_json', {"id": lote_id}),
        beforeSend: function () {
        },
        success: function(data) {

            codigo = data['codigo'];
            lote = data['lote'];
            quadra = data['quadra'];
            area = data['area'];

            table_lote = '<table class="table table-sm table-bordered">';
            table_lote += '<tr class="bg-tr">';
            table_lote += '<th colspan="4">Informação do Lote</th>';
            table_lote += '</tr>';
            table_lote += '<tr>';
            table_lote += '<th>Código</th>';
            table_lote += '<th>Lote</th>';
            table_lote += '<th>Quadra</th>';
            table_lote += '<th>Área</th>';
            table_lote += '</tr>';
            table_lote += '<tr>';
            table_lote += '<td>' + codigo + '</td>';
            table_lote += '<td>' + $(".layout-page #lote").children("option:selected").text() + '</td>';
            table_lote += '<td>' + quadra + '</td>';
            table_lote += '<td>' + area + '</td>';
            table_lote += '</tr>';
            table_lote += '</table>';
            $('.layout-page #resumo-lote').html(table_lote);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

    table_servico = '<table class="table table-sm table-bordered">';
    table_servico += '<tr class="bg-tr">';
    table_servico += '<th colspan="5">Serviços</th>';
    table_servico += '</tr>';
    table_servico += '<tr>';
    table_servico += '<th>Item</th>';
    table_servico += '<th>Serviço</th>';
    table_servico += '<th>Valor</th>';
    table_servico += '<th>Desconto</th>';
    table_servico += '<th>Subtotal</th>';
    table_servico += '</tr>';

    valorTotal = 0;
    i = 1;
    $('#table-orcamento-item > tbody  > .subform ').each(function() {
        servico = $(this).find('.servico').children("option:selected").text();
        if(servico != 'Selecione...'){
            valor = $(this).find('.valor').val();
            desconto = $(this).find('.desconto').val();
            subtotal = $(this).find('.subtotal').val();

            table_servico += '<tr>';
            table_servico += '<td>' + i + '</td>';
            table_servico += '<td>' + servico + '</td>';
            table_servico += '<td>' + valor + '</td>';
            table_servico += '<td>' + desconto + '</td>';
            table_servico += '<td>' + subtotal + '</td>';
            table_servico += '</tr>';
        }
        i += 1;
    });
    table_servico += '<tr class="bg-tr">';
    table_servico += '<td colspan="2">Total</td>';
    table_servico += '<td>' + $('.layout-page #total_valor').val() + '</td>';
    table_servico += '<td>' + $('.layout-page #total_desconto').val() + '</td>';
    table_servico += '<td>' + $('.layout-page #total_subtotal').val() + '</td>';
    table_servico += '</tr>';
    table_servico += '</table>';

    $('.layout-page #resumo-servicos').html(table_servico);

    validade = $('.layout-page #validade').val()
    table_validade = '<table class="table table-sm table-bordered">';
    table_validade += '<tr class="bg-tr">';
    table_validade += '<th colspan="2">Válido por ' + validade + ' dias </th>';
    table_validade += '</tr>';
    table_validade += '</table>';
    $('.layout-page #resumo-validade').html(table_validade);


    observacao = $('.layout-page #observacao').val()
    table_observacao = '<table class="table table-sm table-bordered">';
    table_observacao += '<tr class="bg-tr">';
    table_observacao += '<th>Observações</th>';
    table_observacao += '</tr>';
    table_observacao += '<tr>';
    table_observacao += '<td>' + observacao + '</td>';
    table_observacao += '</tr>';
    table_observacao += '</table>';
    $('.layout-page #resumo-observacao').html(table_observacao);
}

function calculaValorSubTotal(index){

    valorSubTotal = 0;
    valor = ($('.layout-page #itens-'+ index +'-valor').val() !='') ? moeda2float($('.layout-page #itens-'+ index +'-valor').val()) : 0;
    desconto = ($('.layout-page #itens-'+ index +'-desconto').val() !='') ? moeda2float($('.layout-page #itens-'+ index +'-desconto').val()) : 0;

    valorSubTotal = valor - desconto;

    $('.layout-page #itens-'+ index +'-subtotal').val(float2moeda(valorSubTotal));


    calculaValorTotal();

}

function calculaValorTotal(){

    totalValor = 0;
    totalDesconto = 0;
    totalSubtotal = 0;
    i = 0;
    $('#table-orcamento-item > tbody  > .subform    ').each(function() {
        valor = moeda2float($(this).find('.valor').val());
        desconto = moeda2float($(this).find('.desconto').val());
        subtotal = moeda2float($(this).find('.subtotal').val());

        valor = (valor) ? valor : 0;
        desconto = (desconto) ? desconto : 0;
        subtotal = (subtotal) ? subtotal : 0;

        totalValor += valor;
        totalDesconto += desconto;
        totalSubtotal += subtotal;
    });

    $('.layout-page #total_valor').val(float2moeda(totalValor));
    $('.layout-page #total_subtotal').val(float2moeda(totalSubtotal));
    $('.layout-page .total').html(float2moeda(totalSubtotal));

    $('.layout-page #total_desconto').val(float2moeda(totalDesconto));
    $('.layout-page .total-desconto').html(float2moeda(totalDesconto));



    if (totalSubtotal < 0){
        $('.layout-page .total').removeClass('bg-success');
        $('.layout-page .label-total').removeClass('bg-label-success');
        $('.layout-page .total').addClass('bg-danger');
        $('.layout-page .label-total').addClass('bg-label-danger');
    }else{
        $('.layout-page .total').addClass('bg-success');
        $('.layout-page .label-total').addClass('bg-label-success');
        $('.layout-page .total').removeClass('bg-danger');
        $('.layout-page .label-total').removeClass('bg-label-danger');
    }
}


$(document).ready(function () {

    'use strict';

    calculaValorTotal();

    // Search
    $('.layout-page').on('change',"select#orcamentos-per-page", function(){
        per_page = $(this).children("option:selected").val();
        search = $('#orcamentos-search').val();
        view = $('.view-ativa').attr('data-view');
        loadPageOrcamentos(1,per_page, search, view);
    });

    $('.layout-page').on('keyup', "#orcamentos-search", function() {
        per_page = $('select#orcamentos-per-page').children("option:selected").val();
        search = $(this).val();
        view = $('.view-ativa').attr('data-view');
        loadPageOrcamentos(1,per_page, search, view);
    });

    $('.layout-page').on('change', 'select#cliente', function(e){
        e.preventDefault();
        var id = $(this).children("option:selected").val();
        //loadInfocliente(id);
    });


    // View
    $('.layout-page').on('click', '.view-orcamento', function(e){
        e.preventDefault();
        per_page = $('select#orcamentos-per-page').children("option:selected").val();
        search = $('#orcamentos-search').val();
        view = $(this).attr('data-view');
        loadPageOrcamentos(1,per_page, search, view);

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


    // Add Orçamento
    $('.layout-page').on('click', '.addorcamento', function(e){
        e.preventDefault();
        var lote_id = $(this).attr('data-id');
        window.location.href = Flask.url_for('webui.new_orcamento', {"lote_id": lote_id});
    });

    $('.layout-page').on('submit', "#NewOrcamentoForm", function(e) {
        e.preventDefault();

        var lote_id = $('#lote').val();
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.new_orcamento', {"id": lote_id}),
          data: $(this).serialize(),
          beforeSend: function () {
          },
          success: function(data) {
            window.location.href = '/webui/orcamentos/';
          },
          complete: function () {

          },
          error: function(data) {
            console.log(data.status);
            if (data.status == 400){
                $(".input-error").removeClass('is-invalid')
                var errors = data['responseJSON']
                for (const key in errors) {
                    sendNotification(errors[key][0]);
                    const input = document.getElementById(errors[key][0]);
                    input.classList.add('is-invalid');
                }
            }else{
                sendNotification(data.responseJSON.message);
            }
          }
        });
    });


    // Update Orçamento
    $('.layout-page').on('click', '.editorcamento', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.edit_orcamento', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#orcamentos').html(data);
          },
          complete: function () {

          },
          error: function(data) {

          }
        });
    });

    $('.layout-page').on('submit',"#UpdateOrcamentoForm", function(e) {
        e.preventDefault();
        var id = $("#id").val();
        var status = $('.layout-page #status').children("option:selected").val();
        var csrf = $('#csrf_token').val();
        $.ajax({
          type: "POST",
          url: Flask.url_for('webui.edit_orcamento', {"id": id}),
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
                $('#yes').attr("data-csrf", csrf);
                $('#yes').addClass('new-ordem-servico');
                $('.modal-body').html('Devido ao orçamento está aprovado, vamos gerar uma ordem de serviço com base neste orçamento');
                $('#confirm').modal('show');
            }
        }, 500);
          },
          complete: function () {

          },
          error: function(data) {
            console.log(data.status);
            if (data.status == 400){
                $(".input-error").removeClass('is-invalid')
                var errors = data['responseJSON']
                for (const key in errors) {
                    sendNotification(errors[key][0]);
                    const input = document.getElementById(errors[key][0]);
                    input.classList.add('is-invalid');
                }
            }else{
                sendNotification(data.responseJSON.message);
            }
          }
        });

    });


    // Delete Orçamento
    $('.layout-page').on('click', '.deleteorcamento', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id').replace('div-', '');
        var lote_id = $(this).attr('data-lote');
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_orcamento', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            loadOrcamentos(lote_id);
            sendNotification('Orçamento excluido com sucesso!');
          },
          complete: function () {
            $('#confirmDelete').modal('hide');
          },
          error: function(data) {
            sendNotification('Erro ao excluir orçamento!');
          }
        });

    });


    // Serviços
    $('.layout-page').on('click', '#addOrcamentoItem', function(e){
        e.preventDefault();
        addFormOrcamentoItem();
    });

    $('.layout-page').on('click', '.remove-servico', function(e){
        e.preventDefault();

        var index = $(this).attr('data-index');
        var id =  $('.layout-page #itens-'+ index +'-id').val();
        if(id){
            $('#delete').attr("data-id", "div-" + id);
            $('#delete').attr("data-index", index);
            $('#delete').addClass('deleteitemorcamento');
            $('#confirmDelete .modal-body').html('Deseja realmente excluir o item?');
            $('#confirmDelete').modal('show');
        }else{
            removeFormOrcamentoItem(index);
            calculaValorTotal();
        }

    });

    $('.layout-page').on('click', '.deleteitemorcamento', function(e){
        e.preventDefault();
        var index = $(this).attr('data-index');
        var id = $(this).attr('data-id').replace('div-', '')
        $.ajax({
          type: "GET",
          url: Flask.url_for('webui.delete_orcamento_item', {"id": id}),
          beforeSend: function () {
          },
          success: function(data) {
            $('#confirmDelete').modal('hide');
            removeFormOrcamentoItem(index);
            calculaValorTotal();
          },
          complete: function () {

          },
          error: function(data) {

          }
        });

    });

    $('.layout-page').on('change', '.servico', function(e){
        e.preventDefault();
        var index = $(this).attr('data-index');
        var servico = $(this).val();
        var valor_servico = 0;
        if(servico > 0){
            $.ajax({
                type: "GET",
                url: Flask.url_for('webui.get_servico_json',{"id": servico}),
                beforeSend: function () {
                },
                success: function(data) {
                    valor_servico = data['valor'];
                    $('.layout-page #itens-'+ index +'-valor').val(float2moeda(valor_servico));
                    $('.layout-page #itens-'+ index +'-desconto').attr('readonly', false).val();
                },
                complete: function () {
                },
                error: function(data) {
                }
            });
        }else{
            $('.layout-page #itens-'+ index +'-valor').val(float2moeda(0));
            $('.layout-page #itens-'+ index +'-desconto').attr('readonly', 'readonly');
        }

       setTimeout(function (){
            calculaValorSubTotal(index);
        }, 100);

    });

    $('.layout-page').on('focusout', '.valor', function(e){
        e.preventDefault();
        var index = $(this).attr('data-index');
        calculaValorSubTotal(index);
    });

    $('.layout-page').on('focusout', '.desconto', function(e){
        e.preventDefault();
        var index = $(this).attr('data-index');
        calculaValorSubTotal(index);
    });


    // Menus
    $('.layout-page').on('click', '.orcamento-informacoes', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadDetailOrcamento(id)

    });

    $('.layout-page').on('click', '.orcamento-cliente', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadClienteOrcamento(id)

    });

    $('.layout-page').on('click', '.orcamento-lote', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadLoteOrcamento(id)

    });

    $('.layout-page').on('click', '.orcamento-servicos', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadServicosOrcamento(id)

    });

    $('.layout-page').on('click', '.orcamento-historico', function(e){
        e.preventDefault();
        var id = $(this).attr('data-id');
        loadHistoryOrcamento(id)

    });

});

