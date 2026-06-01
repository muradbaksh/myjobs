async function loadDashboard() {

    try {

        const data = await apiRequest(
            "/analytics/platform-overview/"
        );

        updateStatistics(data);

        if (
            data.top_companies &&
            data.top_companies.length > 0
        ) {
            renderCompanyChart(
                data.top_companies
            );
        }

        if (
            data.industry_data &&
            data.industry_data.length > 0
        ) {
            renderIndustryChart(
                data.industry_data
            );
        }

    } catch (error) {

        console.error(
            "Dashboard Load Error:",
            error
        );

        alert(
            "Failed to load dashboard data."
        );
    }

}

function updateStatistics(data) {

    document.getElementById(
        "totalCompanies"
    ).innerText =
        data.total_companies || 0;

    document.getElementById(
        "totalReviews"
    ).innerText =
        data.total_reviews || 0;

    document.getElementById(
        "totalCompensations"
    ).innerText =
        data.total_compensations || 0;

    document.getElementById(
        "avgReputation"
    ).innerText =
        Number(
            data.average_platform_reputation || 0
        ).toFixed(2);

}

function renderCompanyChart(companies) {

    const ctx =
        document.getElementById(
            "companyChart"
        );

    new Chart(ctx, {

        type: "bar",

        data: {

            labels: companies.map(
                company => company.name
            ),

            datasets: [
                {
                    label:
                        "Reputation Score",

                    data: companies.map(
                        company =>
                            company.reputation_index
                    )
                }
            ]

        },

        options: {
            responsive: true,
            maintainAspectRatio: false
        }

    });

}

function renderIndustryChart(industryData) {

    const ctx =
        document.getElementById(
            "industryChart"
        );

    new Chart(ctx, {

        type: "pie",

        data: {

            labels: industryData.map(
                item => item.industry
            ),

            datasets: [
                {
                    data: industryData.map(
                        item =>
                            item.total_reviews
                    )
                }
            ]

        },

        options: {
            responsive: true,
            maintainAspectRatio: false
        }

    });

}

const exportCsvBtn =
    document.getElementById(
        "exportCsvBtn"
    );

if (exportCsvBtn) {

    exportCsvBtn.addEventListener(
        "click",
        () => {

            window.location.href =
                "/analytics/export/csv/";

        }
    );

}

const exportExcelBtn =
    document.getElementById(
        "exportExcelBtn"
    );

if (exportExcelBtn) {

    exportExcelBtn.addEventListener(
        "click",
        () => {

            window.location.href =
                "/analytics/export/excel/";

        }
    );

}

document.addEventListener(
    "DOMContentLoaded",
    loadDashboard
);