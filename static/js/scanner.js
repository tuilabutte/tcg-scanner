const URL = "/static/model/";

let model;
let webcam;
let isRunning = false;
let lastPrediction = "";
let cooldown = false;

const CONFIDENCE_THRESHOLD = 0.97;

async function initScanner() {

    if (isRunning) {
        return;
    }

    isRunning = true;

    const modelURL = URL + "model.json";
    const metadataURL = URL + "metadata.json";

    model = await tmImage.load(
        modelURL,
        metadataURL
    );

    const constraints = {
        facingMode: "environment"
    };

    webcam = new tmImage.Webcam(
        300,
        300,
        false
    );

    await webcam.setup(constraints);
    await webcam.play();

    document
        .getElementById("webcam-container")
        .appendChild(webcam.canvas);

    window.requestAnimationFrame(loop);
}

async function loop() {

    webcam.update();

    await predict();

    window.requestAnimationFrame(loop);
}

async function predict() {

    if (cooldown) {
        return;
    }

    const prediction =
        await model.predict(webcam.canvas);

    let highestPrediction =
        prediction[0];

    for (let i = 1; i < prediction.length; i++) {

        if (
            prediction[i].probability >
            highestPrediction.probability
        ) {

            highestPrediction =
                prediction[i];
        }
    }

    const confidence =
        highestPrediction.probability;

    if (
        confidence >=
        CONFIDENCE_THRESHOLD
    ) {

        const pokemonName =
            highestPrediction.className;

        if (
            pokemonName !==
            lastPrediction
        ) {

            lastPrediction =
                pokemonName;

            handleSuccessfulScan(
                pokemonName,
                confidence
            );
        }
    }
}

async function handleSuccessfulScan(
    name,
    confidence
) {

    document.body.classList.add(
        "scan-flash"
    );

    cooldown = true;

    const resultBox =
        document.getElementById(
            "scan-result"
        );

    resultBox.innerHTML = `
        <div class="success-scan">

            <img
                src="/static/images/pokemon/${name.toLowerCase()}.png"
                class="scanner-pokemon-image">

            <h2>${name}</h2>

            <p>
                Confidence:
                ${(confidence * 100).toFixed(1)}%
            </p>

        </div>
    `;

    try {

        const response =
            await fetch(
                "/api/scan",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                        "application/json"
                    },

                    body: JSON.stringify({
                        pokemon_name: name
                    })
                }
            );

        const data =
            await response.json();

        if (data.success) {

            resultBox.innerHTML += `
                <div class="scan-success-message">
                    ✓ ${data.message}
                </div>
            `;

        } else {

            resultBox.innerHTML += `
                <div class="scan-error-message">
                    ${data.message}
                </div>
            `;
        }

    } catch {

        resultBox.innerHTML += `
            <div class="scan-error-message">
                Scanner error occurred.
            </div>
        `;
    }

    setTimeout(() => {

        document.body.classList.remove(
            "scan-flash"
        );

        cooldown = false;

    }, 3000);
}

document
    .getElementById("start-button")
    .addEventListener(
        "click",
        initScanner
    );