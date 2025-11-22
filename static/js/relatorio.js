
// Script de relatório - integra com Flask para rodar scraping + análise
document.addEventListener("DOMContentLoaded", () => {
  const btnRun = document.getElementById("btn-run");
  const loading = document.getElementById("loading");
  const results = document.getElementById("results");
  const emailBtn = document.getElementById("sendEmailBtn");
  const emailInput = document.getElementById("emailInput");
  const emailStatus = document.getElementById("emailStatus");

  async function refresh() {
    try {
      const res = await fetch("/api/relatorio-data");
      if (!res.ok) {
        console.error("Falha ao buscar /api/relatorio-data");
        results.style.display = "none";
        return;
      }
      const data = await res.json();
      const items = data.items || [];

      if (!items.length) {
        results.style.display = "none";
        return;
      }

      // ----- resumo -----
      const summaryList = document.getElementById("summaryList");
      const summary = items.reduce((acc, row) => {
        const s = row.Sentimento || row.sentimento || "Desconhecido";
        acc[s] = (acc[s] || 0) + 1;
        return acc;
      }, {});
      const total = items.length;
      summaryList.innerHTML = Object.keys(summary).map(key => {
        const qtd = summary[key];
        const perc = ((qtd / total) * 100).toFixed(1);
        return `<li>${key}: <b>${qtd}</b> (${perc}%)</li>`;
      }).join("");

      // ----- gráfico -----
      const labels = Object.keys(summary);
      const values = labels.map(k => summary[k]);
      const ctx = document.getElementById("chart");
      if (window._sentChart) {
        window._sentChart.destroy();
      }
      window._sentChart = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels,
          datasets: [{
            data: values,
            backgroundColor: ["#22c55e", "#ef4444", "#6b7280"],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "bottom" }
          }
        }
      });

      // ----- tabela -----
      const tbody = document.querySelector("#table-details tbody");
      tbody.innerHTML = "";
      items.forEach(row => {
        const comentario = row.Texto || row.texto || row["Comentário"] || "";
        const sentimento = row.Sentimento || row.sentimento || "";
        const conf = row.Confianca ?? row.confianca ?? row.confiança ?? null;
        const confStr = (typeof conf === "number") ? (conf * 100).toFixed(2) + "%" : (conf || "");
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${comentario}</td>
          <td>${sentimento}</td>
          <td>${confStr}</td>
        `;
        tbody.appendChild(tr);
      });

      results.style.display = "block";
    } catch (err) {
      console.error("Erro em refresh():", err);
      results.style.display = "none";
    }
  }

  // Botão de rodar análise
  if (btnRun) {
    btnRun.addEventListener("click", async () => {
      btnRun.disabled = true;
      if (loading) loading.style.display = "block";
      try {
        const res = await fetch("/admin/run-analysis", { method: "POST" });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.success) {
          alert("Erro ao executar análise: " + (data.error || res.statusText));
        } else {
          await refresh();
        }
      } catch (err) {
        console.error("Falha ao chamar /admin/run-analysis:", err);
        alert("Erro de comunicação com o servidor.");
      } finally {
        btnRun.disabled = false;
        if (loading) loading.style.display = "none";
      }
    });
  }

  // Botão de envio de e-mail (opcional, somente se backend existir)
  if (emailBtn && emailInput) {
    emailBtn.addEventListener("click", async () => {
      const email = emailInput.value.trim();
      if (!email) {
        emailStatus.textContent = "Informe um e-mail válido.";
        emailStatus.classList.add("text-danger");
        return;
      }
      emailBtn.disabled = true;
      emailStatus.textContent = "Enviando...";
      emailStatus.classList.remove("text-danger", "text-success");
      try {
        const res = await fetch("/send-report-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email })
        });
        if (res.ok) {
          emailStatus.textContent = "Relatório enviado com sucesso (se o endpoint estiver implementado).";
          emailStatus.classList.add("text-success");
        } else {
          emailStatus.textContent = "Falha ao enviar e-mail.";
          emailStatus.classList.add("text-danger");
        }
      } catch (err) {
        console.error("Erro ao enviar e-mail:", err);
        emailStatus.textContent = "Erro de comunicação ao enviar e-mail.";
        emailStatus.classList.add("text-danger");
      } finally {
        emailBtn.disabled = false;
      }
    });
  }

  // Carrega dados já existentes (se houver)
  refresh();
  document.getElementById("btn-download").href = "/download-pdf";
});
