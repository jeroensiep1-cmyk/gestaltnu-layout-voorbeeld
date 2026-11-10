const form = document.querySelector("#bericht");

if (form) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const body = [
      `Naam: ${data.get("naam")}`,
      `Telefoon: ${data.get("telefoon") || "-"}`,
      `Onderwerp: ${data.get("onderwerp")}`,
      "",
      String(data.get("tekst") || ""),
    ].join("\n");

    window.location.href =
      "mailto:info@gestaltnu.nl?subject=" +
      encodeURIComponent("Bericht via de site van Gestalt Nu") +
      "&body=" +
      encodeURIComponent(body);
  });
}
