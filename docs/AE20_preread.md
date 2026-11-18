# SI 385: Data Exploration

## Application exercise 20, pre-read: choose who is enrolled in a follow-up programme

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 22, Wednesday November 18, 2026.*

---

This pre-read gives the data and question for session 22 and introduces the idea we will use in
class, which is choosing a classifier's threshold to fit what the people using it can do.

## Data

The data describe 69,973 patients with diabetes who were admitted to one of 130 US hospitals
between 1999 and 2008, in `data/diabetes_readmission.parquet`. Each row is one patient's first
stay in the data, and the columns describe the patient's age group, sex and race, how they were
admitted and where they were discharged to, what happened during the stay (days in hospital, lab
tests, procedures, medications, the number of diagnoses and the primary one, an A1C test and
insulin), and how often they had used the hospital in the year before.

The outcome is `readmitted_30`, which is true if the patient was admitted to hospital again within
30 days of being discharged. Patients who died or were discharged to a hospice are not in the
file. About 9% of the patients were readmitted.

## Question

> **A hospital can enrol only a fixed share of the patients it discharges in a follow-up programme
> that is meant to prevent readmissions. Should it use a classifier to choose who is enrolled, and
> how does the answer depend on how many patients it can enrol?**

There are no answer options. In class, each member of your team will take a different capacity
for the programme, of 5%, 10%, 20% or 40% of discharged patients, and your team will compare what
you found. If your team has three members, you should choose together which capacity to leave out.

## Working and submitting

Your team may work on the question together in class. Each of you should then write your own
answer in the session 22 notebook and upload your copy to *AE 20* on Canvas before the end of
class. Your answer should use the numbers from your own capacity and say what your teammates'
capacities added to it.

## Thresholds and capacity

A classifier such as logistic regression or a random forest gives each patient a score, usually an
estimated probability of readmission, and it predicts *readmitted* for every patient whose score is
above a threshold. The usual threshold is 0.5, but nothing requires it. A hospital that can enrol
10% of its patients can rank them by score and enrol the top 10%, which sets the threshold at
whatever score separates that 10% from the rest.

The result is described by its *precision*, which is the share of the enrolled patients who would
have been readmitted, and its *recall*, which is the share of the patients who would have been
readmitted that the programme enrolled. Enrolling more patients usually raises recall and lowers precision, and how
much of one is worth giving up for the other depends on what the programme costs and what a
readmission costs, both to the hospital and to the patient.

## Reading

Session 22's reading, on which RAT 18 is based, is chapter 3 of Géron, *Hands-On Machine Learning
with Scikit-Learn and PyTorch* (2025), from the subsection *Training a Binary Classifier* to the
end of the section *Performance Measures*. The book is available through the University Library's
access to O'Reilly.

## Optional preparation

If you have time before session 22, think about how accurate a classifier would be if
it predicted that no patient would be readmitted, and about who bears the cost when a patient who
needed the programme is not enrolled, and who bears it when a patient who did not need it is.

*Data: Strack, B., DeShazo, J. P., Gennings, C., Olmo, J. L., Ventura, S., Cios, K. J. and Clore,
J. N. (2014). Impact of HbA1c measurement on hospital readmission rates: analysis of 70,000
clinical database patient records. BioMed Research International, 781670. Distributed by the UCI
Machine Learning Repository, dataset 296, under CC BY 4.0.*
