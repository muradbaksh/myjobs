async function loadModerationQueue() {

    const reports = await apiRequest(
        "/admin/moderation/"
    );

    const container =
        document.getElementById(
            "moderationContainer"
        );

    container.innerHTML = "";

    reports.forEach(report => {

        container.innerHTML += `

        <div class="report-card">

            <h3>
                ${report.content_type}
            </h3>

            <p>
                Reason:
                ${report.reason}
            </p>

            <p>
                ${report.description || ""}
            </p>

            <button
                onclick="resolveReport(${report.id})"
            >
                Resolve
            </button>

        </div>

        `;

    });

}

async function resolveReport(id){

    await apiRequest(
        `/admin/moderation/${id}/resolve/`,
        "POST"
    );

    loadModerationQueue();

}

loadModerationQueue();