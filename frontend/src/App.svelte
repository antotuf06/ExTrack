<script>
  // Placeholder shell: the real views (Panoramica, Transazioni, Aggiungi spesa,
  // Categorie, Import, Impostazioni) arrive with phase 1. UI text is Italian.
  let status = $state("verifica in corso…");

  $effect(() => {
    fetch("/api/health")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((d) => (status = d.status === "ok" ? "backend raggiungibile" : "risposta inattesa"))
      .catch(() => (status = "backend non raggiungibile"));
  });
</script>

<main>
  <h1>Dashboard Spese & Investimenti</h1>
  <p>Stato: {status}</p>
</main>
