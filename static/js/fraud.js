async function loadFraudCases() {

    const cases = await apiRequest(
        "/admin/fraud/"
    );

    const container =
        document.getElementById(
            "fraudContainer"
        );

    container.innerHTML = "";

    cases.forEach(item => {

        container.innerHTML += `

        <div class="fraud-card">

            <h3>
                ${item.company}
            </h3>

            <p>
                Risk Score:
                ${item.risk_score}
            </p>

            <button
                onclick="markSafe(${item.id})"
            >
                Mark Safe
            </button>

        </div>

        `;

    });

}

async function markSafe(id){

    await apiRequest(
        `/admin/fraud/${id}/safe/`,
        "POST"
    );

    loadFraudCases();

}

loadFraudCases();