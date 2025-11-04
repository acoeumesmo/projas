// =============================================================
// ARQUIVO: static/js/index.js
// -------------------------------------------------------------
// Responsável por controlar o formulário de envio de reclamações
// na página inicial (index.html).
// Faz a validação, envia os dados para o Flask e mostra alertas
// de sucesso ou erro usando a função App.showToast().
// =============================================================

// Aguarda o carregamento completo da página
App.onReady(function () {

  // Referência ao formulário HTML
  const form = document.getElementById('meuForm');

  // Caso o formulário não exista (ex: em outra página), sai da função
  if (!form) return;

  /**
   * Escuta o evento de envio do formulário.
   * Quando o usuário clica em "Enviar Reclamação", o script:
   * 1. Interrompe o envio padrão do navegador
   * 2. Envia os dados via Fetch para o Flask
   * 3. Mostra um alerta de sucesso ou erro
   * 4. Limpa o formulário
   */
  form.addEventListener('submit', async function (e) {
    e.preventDefault(); // Evita recarregar a página

    // Cria um objeto FormData com todos os campos do formulário
    const formData = new FormData(form);

    try {
      // Envia os dados para o backend (rota Flask /submit)
      const res = await fetch('/submit', {
        method: 'POST',
        body: formData
      });

      // Se o envio não for bem-sucedido, exibe uma mensagem de erro
      if (!res.ok) {
        const txt = await res.text();
        App.showToast('Erro ao enviar reclamação: ' + txt, 'danger');
        return;
      }

      // Exibe mensagem de sucesso
      App.showToast('Reclamação enviada com sucesso! 🎉', 'success');

      // Limpa todos os campos do formulário
      form.reset();
    } catch (err) {
      // Caso ocorra um erro inesperado (ex: sem internet, servidor offline)
      console.error(err);
      App.showToast('Falha de conexão ao enviar reclamação', 'danger');
    }
  });
});
