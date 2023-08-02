// basta a pagina ter os campos referente a cep e endereço

$(document).ready(() => {
  //$('#id_cep').mask('99999-999');

  let formClear = () => {
      // Limpa valores do formulário de cep.
      $("#id_address").val("");
      $("#id_address2").val("");
      $("#id_address3").val("");
      $("#id_unit").val("");
      $("#id_city").val("");
      $("#id_state").val("");
  }

  //Quando o campo cep perde o foco.
  $("#id_zip_code").blur(() => {

      //Nova variável "cep" somente com dígitos.
      let zipCode = $("#id_zip_code").val() //$('#id_zip_code').val().replace(/\D/g, '');

      //Verifica se campo cep possui valor informado.
      if (zipCode != "") {

          //Preenche os campos com "..." enquanto consulta webservice.
          //$("#id_logradouro").val("...");
          //$("#id_complemento").val("...");
          //$("#id_bairro").val("...");
          //$("#id_cidade").val("...");
          //$("#id_uf").val("");

          //Consulta view da app_base
          $.getJSON(`/lookup_br_zipcode/${zipCode}`, data => {

              if (!("erro" in data)) {
                  //Atualiza os campos com os valores da consulta.
                  $("#id_zip_code").val(data.cep);
                  $("#id_address").val(data.logradouro);
                  $("#id_address2").val(data.complemento);
                  $("#id_address3").val(data.bairro);
                  $("#id_city").val(data.cidade);
                  $("#id_state").val(data.uf);
              } //end if.
              else {
                  //CEP pesquisado não foi encontrado.
                  formClear();
                  alert("CEP não encontrado.");
              }
          });

      } //end if.
      else {
          //cep sem valor, limpa formulário.
          formClear();
      }
  });
});
