const compensationForm =
    document.getElementById("compensationForm");

if (compensationForm) {

    compensationForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const data = {
            company: this.company.value,
            job_title: this.job_title.value,
            department: this.department.value,
            employment_type: this.employment_type.value,
            experience_level: this.experience_level.value,
            years_of_experience: this.years_of_experience.value,
            location: this.location.value,
            base_salary: this.base_salary.value,
            allowances: this.allowances.value,
            bonus: this.bonus.value,
            other_benefits: this.other_benefits.value,
            market_fairness_rating: this.market_fairness_rating.value,
        };

        try {
            const res = await apiRequest(
                "/compensation/create/",
                "POST",
                data
            );

            showToast("Compensation submitted successfully", "success");

            console.log(res);

            setTimeout(() => {
                window.location.href = "/benchmark/";
            }, 1000);

        } catch (err) {
    console.error(err);

    showToast(
        JSON.stringify(err),
        "danger"
    );
}
    });
}