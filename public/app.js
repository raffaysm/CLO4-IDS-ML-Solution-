const coreFeatures = [
  "Destination Port",
  "Flow Duration",
  "Total Fwd Packets",
  "Total Backward Packets",
  "Total Length of Fwd Packets",
  "Total Length of Bwd Packets",
  "Fwd Packet Length Mean",
  "Bwd Packet Length Mean",
  "Flow Bytes/s",
  "Flow Packets/s",
  "Flow IAT Mean",
  "Flow IAT Std",
  "Packet Length Mean",
  "Packet Length Std",
  "Average Packet Size"
];

const form = document.getElementById("form");
coreFeatures.forEach(f => {
  const div = document.createElement("div");
  div.innerHTML = `<label>${f}</label><input type="number" id="${f}">`;
  form.appendChild(div);
});

async function predict() {
  const data = {};
  coreFeatures.forEach(f => {
    const val = document.getElementById(f).value;
    data[f] = val === "" ? null : Number(val);
  });

  const res = await fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ data })
  });

  const out = await res.json();
  document.getElementById("result").innerText =
    `Label: ${out.label} | Score: ${out.score}`;
}