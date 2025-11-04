// Garante que exista um objeto global "App" (evita erros caso já exista outro)
window.App = window.App || {};

/**
 * Executa uma função automaticamente quando o DOM (estrutura HTML) estiver pronto.
 * Isso evita erros de "elemento não encontrado" ao tentar manipular o DOM antes do carregamento completo.

 */
App.onReady = function (callback) {
  // Se o documento ainda estiver carregando, aguarda o evento 'DOMContentLoaded'
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback);
  } else {
    // Caso contrário, executa imediatamente
    callback();
  }
};

/**
 * Exibe uma notificação temporária (tipo "alerta flutuante") no topo da página.
 * 
 * @param {string} message - Texto da mensagem a ser exibida.
 * @param {string} type - Tipo da mensagem (Bootstrap): 'info', 'success', 'warning' ou 'danger'.
 *
 */
App.showToast = function (message, type = 'info') {
  // Procura o container principal (onde o alerta será exibido)
  const container = document.querySelector('.container');
  if (!container) return; // Sai se não encontrar container

  // Cria um elemento <div> para o alerta
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show`;
  alert.innerText = message;

  // Adiciona o alerta no topo da página
  container.prepend(alert);

  // Remove automaticamente após 5 segundos
  setTimeout(() => {
    try {
      alert.remove();
    } catch (err) {
      // ignora caso o elemento já tenha sido removido
    }
  }, 5000);
};
