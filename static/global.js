document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("mbti-form");
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
  
      const inputText = document.getElementById("text-input").value;
  
      try {
        const response = await fetch("/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: inputText })
        });
  
        const result = await response.json();
        console.log("Prediction result:", result); //  Debug

        const sortedResult = Object.entries(result).sort((a, b) => b[1] - a[1]);

        let output = `
        <div class="prediction-box">
        <h3 class="prediction-title">Top 3 MBTI Predictions:</h3>
        <ul class="prediction-list">
        `;

        for (const [type, prob] of sortedResult) {
          const percent = (prob * 100).toFixed(1);
          output += `
              <li><span class="type">${type}</span><span class="score">${percent}%</span></li>
              `;
        }

        output += `</ul>`;

        const topType = sortedResult[0][0];
        const topIconPath = `assets/${topType}.gif`;

        output += `
        <div class="top-result">
            <h3>You're most likely: <span class="top-type">${topType}</span></h3>
            <img src="${topIconPath}" alt="${topType}" class="type-icon">
        </div>
        </div>
        `;

        document.getElementById("result").innerHTML = output;

      } catch (err) {
        console.error("Prediction error:", err);
        document.getElementById("result").innerText = "Prediction failed. Check the console.";
      }
    });
  });
  
