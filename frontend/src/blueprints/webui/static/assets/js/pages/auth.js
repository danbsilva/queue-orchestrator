// Load Pages Automations
function loadPageAutomations(page, per_page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.page_automations', {"page": page, "per_page": per_page}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#automations").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}


// Load Detail Automation
function loadDetailAutomation(uuid){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.detail_automation', {"uuid": uuid}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#automation-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}


// Load Pages Steps
function loadPageSteps(automation_uuid, page, per_page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.page_steps', {"automation_uuid": automation_uuid, "page": page, "per_page": per_page}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#steps").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}


// Load Detail Step
function loadDetailStep(uuid){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.detail_step', {"uuid": uuid}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#step-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}


// Load Pages Fields
function loadPageFields(step_uuid, page, per_page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.page_fields', {"step_uuid": step_uuid, "page": page, "per_page": per_page}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#fields").html(data);
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}


// Load Pages Items By Automation
function loadPageItemsByAutomation(automation_uuid, page, per_page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.page_items_by_automation', {"automation_uuid": automation_uuid, "page": page, "per_page": per_page}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#items").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}


// Load Pages Items By Step
function loadPageItemsByStep(step_uuid, page, per_page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.page_items', {"step_uuid": step_uuid, "page": page, "per_page": per_page}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#items").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });

}


// Load Detail Item
function loadDetailItem(uuid){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.detail_item', {"uuid": uuid}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#item-detalhe").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
    });
}


// Load Page Historic Item
function loadPageHistoric(item_uuid, page, per_page){
    $.ajax({
        type: "GET",
        url: Flask.url_for('automations.page_historic', {"item_uuid": item_uuid, "page": page, "per_page": per_page}),
        beforeSend: function () {
        },
        success: function(data) {
            $("#historic").html(data)
        },
        complete: function () {

        },
        error: function(data) {

        }
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

    // Cancel
    $('.layout-page').on('click', '.cancel', function(e){
        e.preventDefault();
        $('#modalForm').modal('hide');
    });


    // Per Page
    $('.layout-page').on('change',"select#automation-per-page", function(e){
        e.preventDefault();
        var per_page = $(this).children("option:selected").val();
        loadPageAutomations(1,per_page);

    });

    // Search
    $('.layout-page').on('keyup', "#automation-search", function(e) {
        e.preventDefault();
        filterTable('automation-search', 'table-automations');
    });

    // Pagination
    $('.layout-page').on('click', '.a-page', function(e){
        e.preventDefault();
        var page = $(this).attr('id');
        var per_page = $('select#automation-per-page').children("option:selected").val();
        loadPageAutomations(page,per_page);
    });


    // Add Automation
    $('.layout-page').on('click', '.addautomation', function(e){
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.new_automation'),
          beforeSend: function () {
             $('#modalForm .modal-body').html('');
             $('#modalForm .modal-title').html('NOVA AUTOMAÇÃO');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit', "#NewAutomationForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
          type: "POST",
          url: Flask.url_for('automations.new_automation'),
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            window.location.href = Flask.url_for('automations.view_automation', {"uuid": data['uuid']});
          },
          complete: function () {
          },
          error: function(data) {
           highlightErrors(data);
          }
        });
    });


    // Update Automation
    $('.layout-page').on('click', '.editautomation', function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var origin = $(this).attr('data-origin');
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.edit_automation', {"uuid": automation_uuid}),
          beforeSend: function () {
            $('#modalForm .modal-body').html('');
            $('#modalForm .modal-title').html('ATUALIZAR AUTOMAÇÃO');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm .modal-body form').attr('data-origin', origin);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit',"#UpdateAutomationForm", function(e) {
        e.preventDefault();
        var page = $('.layout-page').find('.a-page').parent().find('.active').attr('id');
        var per_page = $('select#automation-per-page').children("option:selected").val();
        var formData = $(this).serialize();

        var automation_uuid = $('#uuid').val();
        var origin = $(this).attr('data-origin');

        $.ajax({
          type: "POST",
          url: Flask.url_for('automations.edit_automation', {"uuid": automation_uuid}),
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            $('#modalForm').modal('hide');
            if (origin == 'detail'){
                loadDetailAutomation(automation_uuid);
            }else{
                loadPageAutomations(page,per_page);
            }
            sendNotification('Automação atualizada com sucesso!', 'success');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


    // Delete Automation
    $('.layout-page').on('click', '.deleteautomation', function(e){
        var page = $('.layout-page').find('.a-page').parent().find('.active').attr('id');
        var per_page = $('select#automation-per-page').children("option:selected").val();
        e.preventDefault();
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.delete_automation', {"uuid": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            loadPageAutomations(page, per_page);
            sendNotification(data, 'success')
          },
          complete: function () {
            $('#confirmDelete').modal('hide');
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


    // Per Page
    $('.layout-page').on('change',"select#step-per-page", function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var per_page = $(this).children("option:selected").val();
        loadPageSteps(automation_uuid, 1, per_page);
    });

    // Pagination
    $('.layout-page').on('click', '.a-page-step', function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var page = $(this).attr('id');
        var per_page = $('select#step-per-page').children("option:selected").val();
        loadPageSteps(automation_uuid, page, per_page);
    });

    // Search
    $('.layout-page').on('keyup', "#step-search", function(e) {
        e.preventDefault();
        filterTable('step-search', 'table-steps');
    });


    // Add Step
    $('.layout-page').on('click', '.addstep', function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.new_step', {"automation_uuid": automation_uuid}),
          beforeSend: function () {
            $('#modalForm .modal-body').html('');
            $('#modalForm .modal-title').html('NOVA ETAPA');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit', "#NewStepForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var automation_uuid = $(this).attr('data-automation');
        var page = $('.layout-page').find('.a-page-step').parent().find('.active').attr('id');
        var per_page = $('select#step-per-page').children("option:selected").val();
        $.ajax({
          type: "POST",
          url: Flask.url_for('automations.new_step', {"automation_uuid": automation_uuid}),
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            $('#modalForm').modal('hide');
            loadPageSteps(automation_uuid, 1, per_page);
            sendNotification(data, 'success');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


    // Update Step
    $('.layout-page').on('click', '.editstep', function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var uuid = $(this).attr('id');
        var origin = $(this).attr('data-origin');
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.edit_step', {"automation_uuid": automation_uuid, "uuid": uuid}),
          beforeSend: function () {
            $('#modalForm .modal-body').html('');
            $('#modalForm .modal-title').html('ATUALIZAR ETAPA');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm .modal-body form').attr('data-origin', origin);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit',"#UpdateStepForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var uuid = $('#uuid').val();
        var origin = $(this).attr('data-origin');
        var automation_uuid = $(this).attr('data-automation');
        var page = $('.layout-page').find('.a-page-step').parent().find('.active').attr('id');
        var per_page = $('select#step-per-page').children("option:selected").val();
        $.ajax({
          type: "POST",
          url: Flask.url_for('automations.edit_step',  {"automation_uuid": automation_uuid, "uuid": uuid}),
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            $('#modalForm').modal('hide');
            if (origin == 'detail'){
                loadDetailStep(uuid);
            }else{
                loadPageSteps(automation_uuid, page, per_page);
            }
            sendNotification(data, 'success');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
         }
        });
    });


    // Delete Step
    $('.layout-page').on('click', '.deletestep', function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var page = $('.layout-page').find('.a-page-step').parent().find('.active').attr('id');
        var per_page = $('select#step-per-page').children("option:selected").val();
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.delete_step', {"uuid": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            loadPageSteps(automation_uuid, page, per_page);
            sendNotification(data, 'success')
          },
          complete: function () {
            $('#confirmDelete').modal('hide');
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


    // Conveet Text to Lower Case
    $('.layout-page').on('keyup', ".lowercase", function(e) {
        e.preventDefault();
        var text = $(this).val();
        $(this).val(text.toLowerCase());
    });


    // Per Page
    $('.layout-page').on('change',"select#field-per-page", function(e){
        e.preventDefault();
        var step_uuid = $(this).attr('data-step');
        var per_page = $(this).children("option:selected").val();
        loadPageFields(step_uuid, 1, per_page);
    });

    // Pagination
    $('.layout-page').on('click', '.a-page-field', function(e){
        e.preventDefault();
        var step_uuid = $(this).attr('data-step');
        var page = $(this).attr('id');
        var per_page = $('select#field-per-page').children("option:selected").val();
        loadPageFields(step_uuid, page, per_page);
    });

    // Search
    $('.layout-page').on('keyup', "#field-search", function(e) {
        e.preventDefault();
        filterTable('field-search', 'table-fields');
    });


    // Add Field
    $('.layout-page').on('click', '.addfield', function(e){
        e.preventDefault();
        var step_uuid = $(this).attr('data-step');
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.new_field', {"step_uuid": step_uuid}),
          beforeSend: function () {
            $('#modalForm .modal-body').html('');
            $('#modalForm .modal-title').html('NOVO CAMPO');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit', "#NewFieldForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var step_uuid = $(this).attr('data-step');
        var page = $('.layout-page').find('.a-page-field').parent().find('.active').attr('id');
        var per_page = $('select#field-per-page').children("option:selected").val();
        $.ajax({
          type: "POST",
          url: Flask.url_for('automations.new_field', {"step_uuid": step_uuid}),
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            $('#modalForm').modal('hide');
            loadPageFields(step_uuid, page, per_page);
            sendNotification(data, 'success');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


    // Update Field
    $('.layout-page').on('click', '.editfield', function(e){
        e.preventDefault();
        var step_uuid = $(this).attr('data-step');
        var uuid = $(this).attr('id');
        var origin = $(this).attr('data-origin');
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.edit_field', {"uuid": uuid}),
          beforeSend: function () {
            $('#modalForm .modal-body').html('');
            $('#modalForm .modal-title').html('ATUALIZAR CAMPO');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm .modal-body form').attr('data-origin', origin);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit',"#UpdateFieldForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var uuid = $('#uuid').val();
        var step_uuid = $(this).attr('data-step');
        var page = $('.layout-page .page-item.active a').attr("id");
        var per_page = $('select#field-per-page').children("option:selected").val();
        $.ajax({
          type: "POST",
          url: Flask.url_for('automations.edit_field', {"uuid": uuid}),
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            $('#modalForm').modal('hide');
            console.log(step_uuid, page, per_page);
            loadPageFields(step_uuid, page, per_page);
            sendNotification(data, 'success');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
         }
        });
    });

    // Delete Field
    $('.layout-page').on('click', '.deletefield', function(e){
        e.preventDefault();
        var step_uuid = $(this).attr('data-step');
        var page = $('.layout-page').find('.a-page-field').parent().find('.active').attr('id');
        var per_page = $('select#field-per-page').children("option:selected").val();
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.delete_field', {"uuid": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            loadPageFields(step_uuid, page, per_page);
            sendNotification(data, 'success')
          },
          complete: function () {
            $('#confirmDelete').modal('hide');
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });



    // Per Page
    $('.layout-page').on('change',"select#item-per-page", function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var step_uuid = $(this).attr('data-step');
        var page = $('.layout-page').find('.a-page-item-by-step').parent().find('.active').attr('id');
        var per_page = $(this).children("option:selected").val();
        loadPageItemsByStep(step_uuid, page, per_page);
    });

    // Search
    $('.layout-page').on('keyup', "#item-search", function(e) {
        e.preventDefault();
        filterTable('item-search', 'table-items');
    });

    // Pagination
    $('.layout-page').on('click', '.a-page-item', function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var step_uuid = $(this).attr('data-step');
        var page = $(this).attr('id');
        var per_page = $('select#item-per-page-by-step').children("option:selected").val();
        loadPageItemsByStep(step_uuid, page, per_page);
    });


    // Add Item
    $('.layout-page').on('click', '.additem', function(e){
        e.preventDefault();
        var step_uuid = $(this).attr('data-step');
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.new_item', {"step_uuid": step_uuid}),
          beforeSend: function () {
            $('#modalForm .modal-body').html('');
            $('#modalForm .modal-title').html('NOVO ITEM');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit', "#NewItemForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var automation_uuid = $(this).attr('data-automation');
        var step_uuid = $(this).attr('data-step');
        var per_page = $('select#item-per-page').children("option:selected").val();
        var url = Flask.url_for('automations.new_item', {"step_uuid": step_uuid});
        $.ajax({
          type: "POST",
          url: url,
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            $('#modalForm').modal('hide');
            loadPageItemsByStep(step_uuid, 1, per_page);
            sendNotification('Item adicionado com sucesso!', 'success');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


    // Edit Item
    $('.layout-page').on('click', '.edititem', function(e){
        e.preventDefault();
        var step_uuid = $(this).attr('data-step');
        var uuid = $(this).attr('id');
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.edit_item', {"uuid": uuid}),
          beforeSend: function () {
            $('#modalForm .modal-body').html('');
            $('#modalForm .modal-title').html('ATUALIZAR ITEM');
          },
          success: function(data) {
            $('#modalForm .modal-body').html(data);
            $('#modalForm').modal('show');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });

    $('.layout-page').on('submit',"#UpdateItemForm", function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var uuid = $('#uuid').val();
        var automation_uuid = $(this).attr('data-automation');
        var step_uuid = $(this).attr('data-step');
        var page = $('.layout-page').find('.a-page-item').parent().find('.active').attr('id');
        var per_page = $('select#item-per-page').children("option:selected").val();
        var url = Flask.url_for('automations.edit_item', {"uuid": uuid});
        $.ajax({
          type: "POST",
          url: url,
          data: formData,
          beforeSend: function () {
          },
          success: function(data) {
            $('#modalForm').modal('hide');
            loadPageItemsByStep(step_uuid, page, per_page);
            sendNotification('Item atualizado com sucesso!', 'success');
          },
          complete: function () {
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


    // Delete Item
    $('.layout-page').on('click', '.deleteitem', function(e){
        e.preventDefault();
        var automation_uuid = $(this).attr('data-automation');
        var step_uuid = $(this).attr('data-step');
        var page = $('.layout-page').find('.a-page-item').parent().find('.active').attr('id');
        var per_page = $('select#item-per-page').children("option:selected").val();
        $.ajax({
          type: "GET",
          url: Flask.url_for('automations.delete_item', {"uuid": $(this).attr('data-id').replace('div-', '')}),
          beforeSend: function () {
          },
          success: function(data) {
            loadPageItemsByStep(step_uuid, page, per_page);
            sendNotification(data, 'success')
          },
          complete: function () {
            $('#confirmDelete').modal('hide');
          },
          error: function(data) {
            highlightErrors(data);
          }
        });
    });


});

