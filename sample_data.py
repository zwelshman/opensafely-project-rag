"""
Generate sample data for testing the app when scraping is not available
"""

import json


def create_sample_data():
    """Create sample OpenSAFELY projects for testing"""
    sample_projects = [
        {
            "title": "COVID-19 Vaccine Effectiveness in Elderly Populations",
            "url": "https://www.opensafely.org/project/covid-vaccine-elderly",
            "summary": "A comprehensive study examining the effectiveness of COVID-19 vaccines in patients aged 65 and above, analyzing breakthrough infections and hospitalization rates.",
            "full_description": "This research project investigates the real-world effectiveness of COVID-19 vaccines in elderly populations across England. Using primary care records, we analyze vaccination status, breakthrough infection rates, hospitalization outcomes, and mortality data. The study compares different vaccine types and dosing schedules, with particular focus on vulnerable subgroups including those with underlying health conditions.",
            "authors": "Dr. Jane Smith, Prof. John Doe, Dr. Sarah Johnson",
            "status": "Completed",
            "date": "2023-09-15",
            "topics": "COVID-19, Vaccination, Elderly Care, Infectious Disease",
            "description": "Study on COVID-19 vaccine effectiveness in elderly populations"
        },
        {
            "title": "Mental Health Outcomes During Pandemic Lockdowns",
            "url": "https://www.opensafely.org/project/mental-health-pandemic",
            "summary": "Analysis of mental health service utilization and outcomes during various phases of pandemic lockdowns in England.",
            "full_description": "This study examines the impact of COVID-19 lockdown measures on mental health outcomes across different demographic groups. We analyze primary care consultations, prescriptions for mental health medications, emergency department visits, and referrals to specialist mental health services. The research aims to identify vulnerable populations and inform future public health policy.",
            "authors": "Dr. Emily Brown, Dr. Michael Chen",
            "status": "In Progress",
            "date": "2023-06-20",
            "topics": "Mental Health, COVID-19, Public Health, Social Determinants",
            "description": "Mental health outcomes during pandemic lockdowns"
        },
        {
            "title": "Diabetes Medication Adherence and Glycemic Control",
            "url": "https://www.opensafely.org/project/diabetes-adherence",
            "summary": "Investigating the relationship between medication adherence patterns and glycemic control outcomes in type 2 diabetes patients.",
            "full_description": "This research examines medication adherence patterns among type 2 diabetes patients and their association with glycemic control, complications, and healthcare utilization. Using prescription data and laboratory results, we identify factors associated with poor adherence and evaluate interventions to improve medication-taking behavior. The study includes analysis of socioeconomic factors, comorbidities, and healthcare access.",
            "authors": "Prof. Robert Williams, Dr. Lisa Anderson",
            "status": "Completed",
            "date": "2023-12-01",
            "topics": "Diabetes, Medication Adherence, Chronic Disease Management, Primary Care",
            "description": "Study on diabetes medication adherence"
        },
        {
            "title": "Cancer Screening Uptake in Underserved Communities",
            "url": "https://www.opensafely.org/project/cancer-screening",
            "summary": "Analyzing barriers to cancer screening participation in socioeconomically deprived areas and evaluating targeted intervention strategies.",
            "full_description": "This project investigates disparities in cancer screening uptake (breast, cervical, and colorectal) across different socioeconomic groups in England. We examine factors contributing to lower screening rates in deprived areas, including access barriers, awareness, and cultural factors. The study evaluates the effectiveness of targeted outreach programs and identifies best practices for improving screening participation.",
            "authors": "Dr. Patricia Martinez, Dr. David Lee",
            "status": "In Progress",
            "date": "2023-08-10",
            "topics": "Cancer Prevention, Screening, Health Equity, Public Health",
            "description": "Cancer screening in underserved communities"
        },
        {
            "title": "Cardiovascular Disease Risk Factors in Young Adults",
            "url": "https://www.opensafely.org/project/cvd-young-adults",
            "summary": "Epidemiological study of cardiovascular disease risk factors and early intervention opportunities in adults aged 18-45.",
            "full_description": "This research examines the prevalence and trends of cardiovascular disease risk factors in young adults, including hypertension, hyperlipidemia, obesity, and diabetes. We analyze temporal trends, demographic patterns, and the impact of lifestyle factors. The study aims to identify opportunities for early intervention and prevention strategies targeting younger populations to reduce long-term cardiovascular disease burden.",
            "authors": "Dr. Thomas Clark, Dr. Jennifer White, Prof. Andrew Taylor",
            "status": "Completed",
            "date": "2023-11-05",
            "topics": "Cardiovascular Disease, Prevention, Young Adults, Risk Factors",
            "description": "CVD risk factors in young adults"
        },
        {
            "title": "Antibiotic Prescribing Patterns in Primary Care",
            "url": "https://www.opensafely.org/project/antibiotic-prescribing",
            "summary": "Analysis of antibiotic prescribing trends and appropriateness in primary care settings to inform antimicrobial stewardship efforts.",
            "full_description": "This study examines antibiotic prescribing patterns in primary care across England, assessing appropriateness according to clinical guidelines and identifying factors associated with inappropriate prescribing. We analyze variation between practices, seasonal patterns, and the impact of antimicrobial stewardship interventions. The research aims to support efforts to reduce antibiotic resistance through improved prescribing practices.",
            "authors": "Dr. Susan Miller, Dr. Richard Harris",
            "status": "In Progress",
            "date": "2023-07-22",
            "topics": "Antimicrobial Resistance, Prescribing, Primary Care, Stewardship",
            "description": "Antibiotic prescribing in primary care"
        },
        {
            "title": "Long COVID Syndrome: Clinical Characteristics and Outcomes",
            "url": "https://www.opensafely.org/project/long-covid",
            "summary": "Characterizing the clinical features, risk factors, and long-term outcomes of patients with post-acute COVID-19 syndrome.",
            "full_description": "This research project aims to better understand Long COVID syndrome by analyzing clinical records of patients experiencing persistent symptoms following acute COVID-19 infection. We examine symptom patterns, duration, healthcare utilization, impact on quality of life, and factors predicting prolonged symptoms. The study includes analysis of different COVID-19 variants and vaccination status.",
            "authors": "Prof. Mary Thompson, Dr. James Wilson",
            "status": "In Progress",
            "date": "2023-10-12",
            "topics": "COVID-19, Long COVID, Post-Acute Infection, Chronic Illness",
            "description": "Long COVID clinical characteristics"
        },
        {
            "title": "Childhood Obesity Prevention Interventions",
            "url": "https://www.opensafely.org/project/childhood-obesity",
            "summary": "Evaluating the effectiveness of primary care-based childhood obesity prevention and management interventions.",
            "full_description": "This study evaluates various interventions for childhood obesity prevention and management delivered through primary care settings. We assess the effectiveness of different approaches including lifestyle counseling, family-based interventions, and referral to specialist services. The research examines factors associated with successful weight management and identifies best practices for primary care providers.",
            "authors": "Dr. Karen Moore, Dr. Steven Jackson",
            "status": "Completed",
            "date": "2023-09-28",
            "topics": "Childhood Obesity, Prevention, Pediatrics, Lifestyle Intervention",
            "description": "Childhood obesity prevention study"
        },
        {
            "title": "Opioid Prescribing for Chronic Pain Management",
            "url": "https://www.opensafely.org/project/opioid-prescribing",
            "summary": "Analyzing trends in opioid prescribing for chronic pain and evaluating safer prescribing practices and alternative treatments.",
            "full_description": "This research examines opioid prescribing patterns for chronic pain management in primary care, including trends over time, dose escalation patterns, and concurrent prescribing of other medications. We evaluate the adoption of safer prescribing practices and the use of alternative pain management approaches. The study aims to inform strategies for reducing opioid-related harm while ensuring adequate pain management.",
            "authors": "Dr. Laura Martinez, Prof. Christopher Davis",
            "status": "In Progress",
            "date": "2023-08-30",
            "topics": "Pain Management, Opioids, Prescribing Safety, Chronic Pain",
            "description": "Opioid prescribing patterns study"
        },
        {
            "title": "Asthma Control and Inhaler Technique in Primary Care",
            "url": "https://www.opensafely.org/project/asthma-control",
            "summary": "Investigating asthma control levels and the relationship between inhaler technique education and clinical outcomes.",
            "full_description": "This study examines levels of asthma control in primary care patients and evaluates the impact of inhaler technique assessment and education on clinical outcomes. We analyze prescription patterns, exacerbation rates, emergency healthcare utilization, and the effectiveness of asthma review protocols. The research aims to identify opportunities for improving asthma management in primary care settings.",
            "authors": "Dr. Michelle Adams, Dr. Paul Robinson",
            "status": "Completed",
            "date": "2023-11-18",
            "topics": "Asthma, Chronic Disease Management, Primary Care, Patient Education",
            "description": "Asthma control and inhaler technique"
        }
    ]

    # Save to JSON file
    with open("opensafely_projects.json", "w", encoding="utf-8") as f:
        json.dump(sample_projects, f, indent=2, ensure_ascii=False)

    print(f"Created sample data with {len(sample_projects)} projects")
    print("File saved to: opensafely_projects.json")
    print("\nYou can now run the app with: streamlit run app.py")


if __name__ == "__main__":
    create_sample_data()
