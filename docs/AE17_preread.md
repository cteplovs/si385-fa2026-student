# SI 385: Data Exploration

## Application exercise 17, pre-read: kinds of Olympic athletes

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 19, Monday November 9, 2026.*

---

This pre-read gives Monday's data and question, then reviews how k-means clustering measures the
distance between two people and how the units of each column change that distance.

## Data

The data come from the same file as the Olympic heights in session 3. We will use the 37,643
athletes who competed in the Summer Games from 2000 to 2016 and whose height, weight and age were
all recorded. Each athlete appears once, with their sex, their sport, their height in centimetres,
their weight in kilograms, and their age in years at the Games. Between them, they competed in 36
sports.

## Question

> **What kinds of Olympic athletes are there?**

There are no answer options. In class, we will introduce k-means clustering, and you will use it to
group the athletes by height, weight and age and then describe each group: what its athletes are
like, and which sports they come from.

## Working and submitting

Your team may work on the question together in class. Each of you should then write your own
answer in the session 19 notebook and upload your copy to *AE 17* on Canvas before the end of
class.

## k-means and distance

k-means divides the rows into a number of groups, *k*, that you choose in advance. It starts with
*k* centres, assigns each row to the nearest centre, moves each centre to the mean of the rows
assigned to it, and repeats the last two steps until the assignments stop changing. Each group is
then described by its centre, which is the average athlete in that group.

"Nearest" means the ordinary straight-line distance, computed across all the columns at once. For
two athletes, it is found by squaring the differences in height, weight and age, adding the three,
and taking the square root. A difference of five counts the same in every
column, whether it is five centimetres, five kilograms or five years, so a column whose values vary
more contributes more to the distance. In these athletes, the standard deviation of height is about
11 cm, of weight about 16 kg, and of age about 5 years.

Standardizing, which the session 17 pre-read reviewed, rescales each column so that its values are
measured in standard deviations from its mean. After standardizing, a difference of one counts the
same in every column because it means one standard deviation in each. Whether to standardize is a
decision about which differences between athletes should count, and in class you will try it both
ways.

## Reading

Monday's reading, on which RAT 15 is based, is two sections of James, Witten, Hastie, Tibshirani and
Taylor, *An Introduction to Statistical Learning with Applications in Python* (2023), which is free
to download from statlearning.com: section 12.4.1, *K-Means Clustering*, and section 12.4.3,
*Practical Issues in Clustering*.

## Optional preparation

If you have time before Monday, please think about which sports you would expect to have similar
athletes, and which of height, weight and age you would expect to separate them.

*Data: Griffin, R. (2018). 120 years of Olympic history: athletes and results. Kaggle, compiled
from sports-reference.com, CC0.*
