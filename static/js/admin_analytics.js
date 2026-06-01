async function loadAdminAnalytics() {

    const data = await apiRequest(
        "/admin/analytics/"
    );

    document.getElementById(
        "analyticsContainer"
    ).innerHTML = `

        <p>
            Total Reviews:
            ${data.total_reviews}
        </p>

        <p>
            Total Compensation:
            ${data.total_compensations}
        </p>

        <p>
            Average Reputation:
            ${data.average_reputation}
        </p>

    `;

}

loadAdminAnalytics();