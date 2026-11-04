# SI 385: Data Exploration

## Application exercise 17, pre-read: groups of penguins

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 19, Monday November 9, 2026.*

---

This pre-read gives Monday's data and question, then reviews how k-means clustering measures the
distance between two rows and how the units of each column change that distance.

## Data

The data are 342 penguins measured between 2007 and 2009 by Kristen Gorman and the Palmer Station
Long Term Ecological Research program, on three islands near Palmer Station, Antarctica. Each row
is one penguin, with its bill length, bill depth and flipper length in millimetres and its body
mass in grams. The file also records each penguin's species (Adelie, Chinstrap or Gentoo), which
we will use only after clustering, to compare with the clusters.

## Question

> **What groups do these penguins' measurements show?**

There are no answer options. In class, we will introduce k-means clustering, and you will use it to
group the penguins by their measurements, describe each group, and compare the groups with the
species.

## Working and submitting

Your team may work on the question together in class. Each of you should then write your own
answer in the session 19 notebook and upload your copy to *AE 17* on Canvas before the end of
class.

## k-means and distance

k-means divides the rows into a number of groups, *k*, that you choose in advance. It starts with
*k* centres, assigns each row to the nearest centre, moves each centre to the mean of the rows
assigned to it, and repeats the last two steps until the assignments stop changing. Each group is
then described by its centre, which is the average penguin in that group.

"Nearest" means the ordinary straight-line distance, computed across all the columns at once. For
two penguins, it is found by squaring the difference in each measurement, adding the squares, and
taking the square root. A difference of ten counts the same in every column, whether it is ten
millimetres or ten grams, so a column whose values vary more contributes more to the distance. In
these penguins, the standard deviation of body mass is about 800 grams, and those of the three
measurements in millimetres are between 2 and 14.

Standardizing, which the session 17 pre-read reviewed, rescales each column so that its values are
measured in standard deviations from its mean. After standardizing, a difference of one counts the
same in every column because it means one standard deviation in each. Whether to standardize is a
decision about which differences between penguins should count, and in class you will try it both
ways.

## Reading

Monday's reading, on which RAT 15 is based, is two sections of James, Witten, Hastie, Tibshirani and
Taylor, *An Introduction to Statistical Learning with Applications in Python* (2023), which is free
to download from statlearning.com: section 12.4.1, *K-Means Clustering*, and section 12.4.3,
*Practical Issues in Clustering*.

## Optional preparation

If you have time before Monday, please think about which measurements you would expect to separate
the species, and what you would expect k-means to do with body mass measured in grams.

*Data: Gorman, K. B., Williams, T. D. and Fraser, W. R. (2014). Ecological sexual dimorphism and
environmental variability within a community of Antarctic penguins (genus Pygoscelis). PLoS ONE
9(3): e90081. Distributed as the palmerpenguins package by Horst, Hill and Gorman (2020), CC0.*
