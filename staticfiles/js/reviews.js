const reviewForm =
document.getElementById(
    "reviewForm"
);

if(reviewForm){

reviewForm.addEventListener(
"submit",

async function(e){

e.preventDefault();

const payload = {

company:
this.company.value,

brand_value:
this.brand_value.value,

work_environment:
this.work_environment.value,

career_growth:
this.career_growth.value,

salary_satisfaction:
this.salary_satisfaction.value,

benefits:
this.benefits.value,

job_security:
this.job_security.value,

management_quality:
this.management_quality.value,

work_life_balance:
this.work_life_balance.value,

employee_respect:
this.employee_respect.value,

recommendation:
this.recommendation.value,

comment:
this.comment.value

};

await apiRequest(
"/reviews/create/",
"POST",
payload
);

alert(
"Review Submitted. +10 Credits"
);

}
);

}