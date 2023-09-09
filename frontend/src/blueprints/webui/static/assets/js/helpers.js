const ID_RE = /(-)_(-)/;


function moeda2float(moeda){
    if(moeda == '' || moeda == undefined){
        return 0;
    }
    moeda = moeda.replaceAll(".","");
    moeda = moeda.replace(",",".");
    return parseFloat(moeda);
}


function float2moeda(number, decimals, dec_point, thousands_sep) {
    if(decimals == undefined){
        decimals = 2;
    }
    //decimals = casasDecimaisValor;
    dec_point  = ',';
    thousands_sep  = '.';

  number = (number + '')
    .replace(/[^0-9+\-Ee.]/g, '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function (n, prec) {
      var k = Math.pow(10, prec);
      return '' + (Math.round(n * k) / k)
        .toFixed(prec);
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n))
    .split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '')
    .length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1)
      .join('0');
  }
  return s.join(dec);
}

function loadMascaras() {
    $(".celular").inputmask("(99) 99999-9999");
    $(".telefone").inputmask("(99) 9999-9999");
    $(".cpf").inputmask("999.999.999-99");
    $(".cnpj").inputmask("99.999.999/9999-99");
    $(".cep").inputmask("99999-999");
    $(".codigo-lote").inputmask("999.999.999");
    $('.mascara-valor-padrao').on('keypress', function(e){
        if(window.event){
    		tecla = e.keyCode;
    	}else if (e.which){
    		tecla = e.which;
    	}else{
            tecla = 0;
    	}
        if(tecla == 13){
            return false;
        }
    	if ( (tecla >= 48 && tecla <= 57)||(tecla == 8 ) ||(tecla == 44 ) || (tecla == 46) || (tecla == 13)  || (tecla == 45)){
            if(tecla == 13){
                $(this).blur();
            }
            return true;
    	}else{
    		return false;
    	}
   }).on('blur', function(e){
        valor = $(this).val();
        if(valor != ''){
            $(this).val(formataMoedaPadrao(valor));
            valor = moeda2float(valor);
            valor = formataMoedaPadrao(valor);
            $(this).val(valor);
        }
   }).on('focus', function(){
        $(this).attr('placeholder', formataMoedaPadrao(0));
        campo = $(this);
        window.setTimeout (function(){
           campo.select();
        },100);
   }).on('blur', function(){
        $(this).attr('placeholder', '');
   });
}

function formataMoedaPadrao(number, dec_point, thousands_sep) {

    decimals = 2;
    dec_point  = ',';
    thousands_sep  = '.';

  number = (number + '')
    .replace(/[^0-9+\-Ee.]/g, '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function (n, prec) {
      var k = Math.pow(10, prec);
      return '' + (Math.round(n * k) / k)
        .toFixed(prec);
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n))
    .split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '')
    .length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1)
      .join('0');
  }
  return s.join(dec);
}

function highlightErrors(data) {
    var message = '<ul>';
    $(".input-error").removeClass('is-invalid')
    if (data['responseJSON']){
        for (const key in data['responseJSON']) {
            const input = document.getElementById(data['responseJSON'][key][0]);
            console.log(input);
            input.classList.add('is-invalid');
            message += '<li>'+data['responseJSON'][key][1]+'</li>';
        }
        message += '</ul>';

    }else{
        message = data['responseText'];
    }
    sendNotification(message, 'danger');
  }

function sendNotification(message, type) {
    const t = document.querySelector(".toast");
    let c;
    $(".toast .toast-body").html(message);
    if (type == 'success'){
        $(".toast").removeClass("bg-danger");
        $(".toast").addClass("bg-success");
    }else{
        $(".toast").removeClass("bg-success");
        $(".toast").addClass("bg-danger");
    }
    (c = new bootstrap.Toast(t)).show()
}

function filterTable(inputId, tableId) {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById(inputId);
    filter = input.value.toUpperCase();
    table = document.getElementById(tableId);
    tr = table.getElementsByTagName("tr");

    for (i = 1; i < tr.length; i++) {
            tr[i].style.display = "none"; // Oculta todas as linhas

            for (j = 0; j < tr[i].getElementsByTagName("td").length; j++) {
                td = tr[i].getElementsByTagName("td")[j];
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        tr[i].style.display = ""; // Exibe a linha se houver correspondência
                        break; // Sai do loop interno se encontrou correspondência
                    }
                }
            }
        }
}

function replaceTemplateIndex(value, index) {
    return value.replace(ID_RE, '$1'+index+'$2');
}

function adjustIndices(removedIndex) {
    var $forms = $('.subform');

    $forms.each(function(i) {
        var $form = $(this);
        var index = parseInt($form.data('index'));
        var newIndex = index - 1;

        if (index < removedIndex) {
            // Skip
            return true;
        }

        // This will replace the original index with the new one
        // only if it is found in the format -num-, preventing
        // accidental replacing of fields that may have numbers
        // intheir names.
        var regex = new RegExp('(-)'+index+'(-)');
        var repVal = '$1'+newIndex+'$2';

        // Change ID in form itself
        $form.attr('id', $form.attr('id').replace(index, newIndex));
        $form.data('index', newIndex);

        // Change IDs in form fields
        $form.find('label, input, select, textarea').each(function(j) {
            var $item = $(this);

            if ($item.is('label')) {
                // Update labels
                $item.attr('for', $item.attr('for').replace(regex, repVal));
                return;
            }

            // Update other fields
            $item.attr('id', $item.attr('id').replace(regex, repVal));
            $item.attr('name', $item.attr('name').replace(regex, repVal));
        });
    });
}


function formatarData(data){
    var dataCriada = new Date(data);
    var dataFormatada = dataCriada.toLocaleDateString('pt-BR', {
      timeZone: 'UTC',
    });
    return dataFormatada;
}

function adicionarDiasData(data, dias){
  var hoje        = new Date(data);
  var dataVenc    = new Date(hoje.getTime() + (dias * 24 * 60 * 60 * 1000));
  return dataVenc.getFullYear() + "-" + ("0" + (dataVenc.getMonth() + 1)).slice(-2) + "-" +  ("0" + dataVenc.getDate()).slice(-2);
}

function navegacao(link,tipo){
    $.ajax({
       url : link,
       dataType : "HTML", // Pode ser SCRIPT se o retorno for somente comandos JavaScript
       type : tipo, // Pode ser get ou post..
       success : function(conteudo){
            console.log(conteudo);
            window.history.pushState("object or string", "Title", link);
            $(".content").html(conteudo).fadeIn('slow');
       },
       error : function(a,b,c){
             alert("Erro : "+a["status"]+" "+c);
       }
    });
}


$('.layout-page').on('click', '.nok', function(e){
    e.preventDefault();
    $('#confirm').modal('hide');
});


$('.layout-page').on('click', '.menu-link', function(e){
    e.preventDefault();
    var $li = $(this).parent();

    $('.layout-page .active').removeClass("active"); //Remove any "active" class
    $($li).addClass("active"); //Add "active" class to selected tab


});



window.onload =function(){
    var $lista = $('#lista');
    var $a = $('#lista a');
    var $url = window.location.href;

    for (i=0; i < $a.length; i++ ){
        var tag = $a[i].parentElement.classList[1];
        if($url == $a[i].href){
            $a[i].parentElement.classList.add("active");
        }else{
            if($url.indexOf(tag) != -1){
                $a[i].parentElement.classList.add("active");
            }else{
                $a[i].parentElement.classList.remove("active");
            }
        }
    }
}

