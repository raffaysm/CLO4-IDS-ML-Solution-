const form = document.getElementById("predict-form");
const result = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {};
  new FormData(form).forEach((value, key) => {
    data[key] = Number(value);
  });

  result.classList.add("hidden");

  const res = await fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data })
  });

  const json = await res.json();
  result.innerHTML = `
    <strong>Prediction:</strong> ${json.label}<br/>
    <strong>Score:</strong> ${json.score}
  `;
  result.classList.remove("hidden");
});