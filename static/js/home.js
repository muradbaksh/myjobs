async function loadHomePage() {

    try {

        await loadPlatformStats();

        await loadTopCompanies();

        await loadLatestReviews();

        await loadSalaryPreview();

    } catch (error) {

        console.error(
            "Home Page Error:",
            error
        );
    }
}

async function loadPlatformStats() {

    const data =
        await apiRequest(
            "/analytics/platform-overview/"
        );

    document.getElementById(
        "companiesCount"
    ).innerText =
        data.total_companies || 0;

    document.getElementById(
        "reviewsCount"
    ).innerText =
        data.total_reviews || 0;

    document.getElementById(
        "salaryCount"
    ).innerText =
        data.total_compensations || 0;
}

async function loadTopCompanies() {

    const companies =
        await apiRequest(
            "/analytics/company-rankings/"
        );

    const container =
        document.getElementById(
            "topCompaniesContainer"
        );

    if (!container) return;

    container.innerHTML = "";

    companies
    .slice(0, 6)
    .forEach(company => {

        container.innerHTML += `

        <div class="company-card">

            <h3>
                ${company.name}
            </h3>

            <p>
                Reputation:
                ${company.reputation_score}
            </p>

        </div>

        `;
    });
}

async function loadLatestReviews() {

    const container =
        document.getElementById(
            "latestReviewsContainer"
        );

    if (!container) return;

    container.innerHTML = `

        <div class="review-card">
            Anonymous review example
        </div>

        <div class="review-card">
            Salary and culture feedback
        </div>

        <div class="review-card">
            Good workplace environment
        </div>

    `;

    /*
    Later create endpoint:

    /api/reviews/latest/

    then load dynamically
    */
}

async function loadSalaryPreview() {

    const container =
        document.getElementById(
            "salaryPreviewContainer"
        );

    if (!container) return;

    container.innerHTML = `

        <div class="salary-card">

            <h4>
                Software Engineer
            </h4>

            <p>
                P50 Salary
            </p>

        </div>

        <div class="salary-card">

            <h4>
                Senior Software Engineer
            </h4>

            <p>
                P50 Salary
            </p>

        </div>

        <div class="salary-card">

            <h4>
                Backend Engineer
            </h4>

            <p>
                P50 Salary
            </p>

        </div>

    `;
}

document.addEventListener(
    "DOMContentLoaded",
    loadHomePage
);