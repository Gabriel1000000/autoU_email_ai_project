function fillSamples(){
    const samples = [
      "Preciso de uma atualização sobre o chamado #123, quando será resolvido?",
      "Feliz Natal! Obrigado pelo apoio durante este ano!",
      "Anexo o relatório solicitado. Aguardo retorno."
    ];
    document.getElementById('email_text').value = samples[Math.floor(Math.random()*samples.length)];
}

