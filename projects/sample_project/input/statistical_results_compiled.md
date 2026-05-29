# Statistical Results Compiled From statresults/

Generated: 2026-05-30 00:50:59

## Source Manifest Summary

- Files listed: 7
- Files extracted: 7
- Files skipped/failed: 0

## File: anova_results.csv

Source path: C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\statresults\anova_results.csv
Extraction status: extracted

Extraction warning: Table preview limited to first 100 rows.

### Extracted Content

Variable,F,p_value
CG1,8.837461329423018,0.00031555954000081547
CG2,9.669900913305003,0.0001584118463927338
CG3,46.40032418721442,1.5698521801981145e-14
CG4,3.865785225877994,0.024550971095360148
CG5,1.6708416599435663,0.19393391620440603
PB1,4.814134445582471,0.010346477738443037
PB2,29.27522242119177,1.698251530325368e-10
PB3,48.724928815521466,5.103214229965987e-15
PB4,87.6042638705254,9.358824744773023e-22
PB5,289.57040706142647,1.0995860210866974e-39
Subj01,1.2133348865078175,0.30207251315086153
Subj02,0.5940501776251892,0.5542607711788178
Subj03,0.39645542092690716,0.6738823030124114
Subj04,0.8424536667350875,0.4340574279680559
Subj05,1.851102506331585,0.163059997186631
GEN_AVE,1.1699500979866586,0.3151095671298135
CG_mean,5.205223262504468,0.0072799802959347786
PB_mean,58.913325795204464,5.050867784510579e-17

## File: correlations.csv

Source path: C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\statresults\correlations.csv
Extraction status: extracted

Extraction warning: Table preview limited to first 100 rows.

### Extracted Content

Cluster,Variable,Outcome,r,p_value
1,CG1,Subj01,-0.022309192355823973,0.8328226590837846
1,PB1,Subj01,0.09915882706385198,0.34700508097501437
2,CG2,Subj02,-0.05009612232422039,0.635333558446473
2,PB2,Subj02,0.08390822957410506,0.42648601018691124
3,CG3,Subj03,0.17062502785116596,0.10391779450735263
3,PB3,Subj03,0.1102913869617627,0.29527913796476407
4,CG4,Subj04,-0.057852345795919115,0.583848223058136
4,PB4,Subj04,0.21359719379342154,0.04091420419464227
5,CG5,Subj05,0.2911808995031684,0.004862326161524618
5,PB5,Subj05,0.16145240139428899,0.12416366924873438
0,Academic Mean,GEN_AVE,0.016764483353153684,0.8739746932992081
0,Preboard Mean,GEN_AVE,0.22430759824029273,0.031591836090813445

## File: logit_accuracies.csv

Source path: C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\statresults\logit_accuracies.csv
Extraction status: extracted

Extraction warning: Table preview limited to first 100 rows.

### Extracted Content

CG_only,PB_only,Combined
0.7282608695652174,0.5760869565217391,0.7717391304347826

## File: passfail_by_batch.csv

Source path: C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\statresults\passfail_by_batch.csv
Extraction status: extracted

Extraction warning: Table preview limited to first 100 rows.

### Extracted Content

Batch Year,FAILED,PASSED
2022,9,19
2023,15,17
2024,12,20

## File: passfail_chi2.csv

Source path: C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\statresults\passfail_chi2.csv
Extraction status: extracted

Extraction warning: Table preview limited to first 100 rows.

### Extracted Content

Chi2,p_value,dof
1.415497448979592,0.4927522708236569,2

## File: regression_summaries.txt

Source path: C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\statresults\regression_summaries.txt
Extraction status: extracted

### Extracted Content

Outcome: Subj01
--- Model: CG_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj01   R-squared:                       0.090
Model:                            OLS   Adj. R-squared:                  0.037
Method:                 Least Squares   F-statistic:                     1.708
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.141
Time:                        12:11:00   Log-Likelihood:                -345.92
No. Observations:                  92   AIC:                             703.8
Df Residuals:                      86   BIC:                             719.0
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -33.1514     44.760     -0.741      0.461    -122.131      55.829
CG1            0.1898      1.302      0.146      0.884      -2.397       2.777
CG2           -0.4955      1.151     -0.430      0.668      -2.784       1.793
CG3           -0.0756      0.416     -0.182      0.856      -0.903       0.752
CG4           -0.0634      0.317     -0.200      0.842      -0.693       0.566
CG5            1.6138      0.611      2.642      0.010       0.400       2.828
==============================================================================
Omnibus:                        7.483   Durbin-Watson:                   1.334
Prob(Omnibus):                  0.024   Jarque-Bera (JB):                3.158
Skew:                           0.126   Prob(JB):                        0.206
Kurtosis:                       2.128   Cond. No.                     7.74e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 7.74e+03. This might indicate that there are
strong multicollinearity or other numerical problems.

--- Model: PB_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj01   R-squared:                       0.081
Model:                            OLS   Adj. R-squared:                  0.028
Method:                 Least Squares   F-statistic:                     1.520
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.192
Time:                        12:11:00   Log-Likelihood:                -346.38
No. Observations:                  92   AIC:                             704.8
Df Residuals:                      86   BIC:                             719.9
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         58.0957      6.189      9.386      0.000      45.791      70.400
PB1            0.0625      0.127      0.494      0.623      -0.189       0.314
PB2           -0.2094      0.148     -1.412      0.162      -0.504       0.086
PB3            0.0789      0.104      0.759      0.450      -0.128       0.285
PB4            0.2719      0.132      2.060      0.042       0.009       0.534
PB5           -0.0415      0.105     -0.394      0.694      -0.251       0.168
==============================================================================
Omnibus:                        7.093   Durbin-Watson:                   1.271
Prob(Omnibus):                  0.029   Jarque-Bera (JB):                3.191
Skew:                           0.161   Prob(JB):                        0.203
Kurtosis:                       2.146   Cond. No.                         713.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

--- Model: Combined
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj01   R-squared:                       0.129
Model:                            OLS   Adj. R-squared:                  0.021
Method:                 Least Squares   F-statistic:                     1.197
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.305
Time:                        12:11:00   Log-Likelihood:                -343.93
No. Observations:                  92   AIC:                             709.9
Df Residuals:                      81   BIC:                             737.6
Df Model:                          10
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -22.8284     55.289     -0.413      0.681    -132.836      87.179
CG1            0.4314      1.361      0.317      0.752      -2.277       3.140
CG2           -0.6531      1.190     -0.549      0.585      -3.020       1.714
CG3            0.0023      0.580      0.004      0.997      -1.152       1.157
CG4           -0.1392      0.333     -0.418      0.677      -0.802       0.523
CG5            1.4044      0.996      1.409      0.163      -0.578       3.387
PB1            0.0338      0.139      0.243      0.808      -0.243       0.310
PB2           -0.2443      0.154     -1.586      0.117      -0.551       0.062
PB3            0.0449      0.146      0.307      0.760      -0.246       0.336
PB4            0.1996      0.146      1.363      0.177      -0.092       0.491
PB5           -0.0514      0.112     -0.461      0.646      -0.274       0.171
==============================================================================
Omnibus:                        1.973   Durbin-Watson:                   1.395
Prob(Omnibus):                  0.373   Jarque-Bera (JB):                1.567
Skew:                           0.146   Prob(JB):                        0.457
Kurtosis:                       2.431   Cond. No.                     1.14e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.14e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Outcome: Subj02
--- Model: CG_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj02   R-squared:                       0.083
Model:                            OLS   Adj. R-squared:                  0.030
Method:                 Least Squares   F-statistic:                     1.566
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.178
Time:                        12:11:00   Log-Likelihood:                -333.15
No. Observations:                  92   AIC:                             678.3
Df Residuals:                      86   BIC:                             693.4
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         -4.6676     38.959     -0.120      0.905     -82.116      72.781
CG1            0.2064      1.133      0.182      0.856      -2.046       2.458
CG2           -0.2099      1.002     -0.209      0.835      -2.202       1.782
CG3           -0.1253      0.362     -0.346      0.730      -0.846       0.595
CG4           -0.2127      0.276     -0.772      0.442      -0.760       0.335
CG5            1.2879      0.532      2.423      0.018       0.231       2.345
==============================================================================
Omnibus:                       26.448   Durbin-Watson:                   1.706
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               40.641
Skew:                          -1.255   Prob(JB):                     1.50e-09
Kurtosis:                       5.074   Cond. No.                     7.74e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 7.74e+03. This might indicate that there are
strong multicollinearity or other numerical problems.

--- Model: PB_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj02   R-squared:                       0.065
Model:                            OLS   Adj. R-squared:                  0.010
Method:                 Least Squares   F-statistic:                     1.190
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.321
Time:                        12:11:00   Log-Likelihood:                -334.08
No. Observations:                  92   AIC:                             680.2
Df Residuals:                      86   BIC:                             695.3
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         70.5566      5.415     13.030      0.000      59.792      81.321
PB1           -0.0265      0.111     -0.239      0.812      -0.247       0.194
PB2           -0.0898      0.130     -0.692      0.491      -0.348       0.168
PB3            0.0538      0.091      0.592      0.555      -0.127       0.235
PB4            0.2319      0.115      2.008      0.048       0.002       0.461
PB5           -0.0695      0.092     -0.755      0.453      -0.253       0.114
==============================================================================
Omnibus:                       26.533   Durbin-Watson:                   1.787
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               41.150
Skew:                          -1.251   Prob(JB):                     1.16e-09
Kurtosis:                       5.114   Cond. No.                         713.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

--- Model: Combined
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj02   R-squared:                       0.121
Model:                            OLS   Adj. R-squared:                  0.012
Method:                 Least Squares   F-statistic:                     1.115
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.362
Time:                        12:11:00   Log-Likelihood:                -331.23
No. Observations:                  92   AIC:                             684.5
Df Residuals:                      81   BIC:                             712.2
Df Model:                          10
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -10.1939     48.158     -0.212      0.833    -106.013      85.625
CG1            0.5289      1.186      0.446      0.657      -1.830       2.888
CG2           -0.3646      1.036     -0.352      0.726      -2.426       1.697
CG3           -0.2067      0.505     -0.409      0.684      -1.212       0.799
CG4           -0.2734      0.290     -0.943      0.349      -0.850       0.304
CG5            1.3510      0.868      1.556      0.123      -0.376       3.078
PB1           -0.0610      0.121     -0.504      0.616      -0.302       0.180
PB2           -0.1216      0.134     -0.907      0.367      -0.389       0.145
PB3            0.0137      0.127      0.107      0.915      -0.240       0.267
PB4            0.1716      0.128      1.345      0.182      -0.082       0.425
PB5           -0.0706      0.097     -0.726      0.470      -0.264       0.123
==============================================================================
Omnibus:                       27.389   Durbin-Watson:                   1.881
Prob(Omnibus):                  0.000   Jarque-Bera (JB):               44.498
Skew:                          -1.257   Prob(JB):                     2.17e-10
Kurtosis:                       5.300   Cond. No.                     1.14e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.14e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Outcome: Subj03
--- Model: CG_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj03   R-squared:                       0.128
Model:                            OLS   Adj. R-squared:                  0.077
Method:                 Least Squares   F-statistic:                     2.518
Date:                Fri, 29 May 2026   Prob (F-statistic):             0.0355
Time:                        12:11:00   Log-Likelihood:                -352.59
No. Observations:                  92   AIC:                             717.2
Df Residuals:                      86   BIC:                             732.3
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -77.8614     48.126     -1.618      0.109    -173.533      17.810
CG1            2.3107      1.399      1.651      0.102      -0.471       5.093
CG2           -2.1872      1.238     -1.767      0.081      -4.648       0.273
CG3            0.2053      0.448      0.458      0.648      -0.685       1.095
CG4           -0.1255      0.340     -0.369      0.713      -0.802       0.551
CG5            1.4942      0.657      2.275      0.025       0.189       2.800
==============================================================================
Omnibus:                       10.773   Durbin-Watson:                   1.588
Prob(Omnibus):                  0.005   Jarque-Bera (JB):               11.221
Skew:                          -0.842   Prob(JB):                      0.00366
Kurtosis:                       3.297   Cond. No.                     7.74e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 7.74e+03. This might indicate that there are
strong multicollinearity or other numerical problems.

--- Model: PB_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj03   R-squared:                       0.092
Model:                            OLS   Adj. R-squared:                  0.039
Method:                 Least Squares   F-statistic:                     1.740
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.134
Time:                        12:11:00   Log-Likelihood:                -354.44
No. Observations:                  92   AIC:                             720.9
Df Residuals:                      86   BIC:                             736.0
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         60.6925      6.756      8.983      0.000      47.261      74.124
PB1            0.0073      0.138      0.053      0.958      -0.267       0.282
PB2           -0.2068      0.162     -1.277      0.205      -0.529       0.115
PB3            0.1207      0.113      1.064      0.290      -0.105       0.346
PB4            0.2724      0.144      1.890      0.062      -0.014       0.559
PB5            0.0045      0.115      0.039      0.969      -0.224       0.233
==============================================================================
Omnibus:                        8.058   Durbin-Watson:                   1.467
Prob(Omnibus):                  0.018   Jarque-Bera (JB):                8.594
Skew:                          -0.738   Prob(JB):                       0.0136
Kurtosis:                       2.746   Cond. No.                         713.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

--- Model: Combined
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj03   R-squared:                       0.184
Model:                            OLS   Adj. R-squared:                  0.083
Method:                 Least Squares   F-statistic:                     1.825
Date:                Fri, 29 May 2026   Prob (F-statistic):             0.0690
Time:                        12:11:00   Log-Likelihood:                -349.53
No. Observations:                  92   AIC:                             721.1
Df Residuals:                      81   BIC:                             748.8
Df Model:                          10
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -51.5923     58.755     -0.878      0.382    -168.497      65.312
CG1            2.8684      1.447      1.983      0.051      -0.010       5.747
CG2           -2.2709      1.264     -1.796      0.076      -4.786       0.244
CG3            0.4631      0.617      0.751      0.455      -0.764       1.690
CG4           -0.3169      0.354     -0.895      0.373      -1.021       0.387
CG5            0.5584      1.059      0.527      0.599      -1.549       2.665
PB1           -0.0905      0.148     -0.613      0.541      -0.384       0.203
PB2           -0.2460      0.164     -1.503      0.137      -0.572       0.080
PB3            0.2091      0.155      1.347      0.182      -0.100       0.518
PB4            0.2240      0.156      1.439      0.154      -0.086       0.534
PB5            0.0174      0.119      0.146      0.884      -0.219       0.254
==============================================================================
Omnibus:                        9.333   Durbin-Watson:                   1.656
Prob(Omnibus):                  0.009   Jarque-Bera (JB):                9.238
Skew:                          -0.752   Prob(JB):                      0.00986
Kurtosis:                       3.385   Cond. No.                     1.14e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.14e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Outcome: Subj04
--- Model: CG_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj04   R-squared:                       0.097
Model:                            OLS   Adj. R-squared:                  0.044
Method:                 Least Squares   F-statistic:                     1.843
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.113
Time:                        12:11:00   Log-Likelihood:                -309.85
No. Observations:                  92   AIC:                             631.7
Df Residuals:                      86   BIC:                             646.8
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const          1.9432     30.242      0.064      0.949     -58.177      62.063
CG1            0.4995      0.879      0.568      0.571      -1.249       2.248
CG2           -0.4523      0.778     -0.582      0.562      -1.999       1.094
CG3           -0.0682      0.281     -0.242      0.809      -0.628       0.491
CG4           -0.1485      0.214     -0.694      0.489      -0.574       0.277
CG5            1.0660      0.413      2.583      0.011       0.246       1.886
==============================================================================
Omnibus:                        5.783   Durbin-Watson:                   1.618
Prob(Omnibus):                  0.055   Jarque-Bera (JB):                5.423
Skew:                          -0.432   Prob(JB):                       0.0664
Kurtosis:                       3.817   Cond. No.                     7.74e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 7.74e+03. This might indicate that there are
strong multicollinearity or other numerical problems.

--- Model: PB_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj04   R-squared:                       0.070
Model:                            OLS   Adj. R-squared:                  0.016
Method:                 Least Squares   F-statistic:                     1.303
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.270
Time:                        12:11:00   Log-Likelihood:                -311.17
No. Observations:                  92   AIC:                             634.3
Df Residuals:                      86   BIC:                             649.5
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         73.8036      4.221     17.483      0.000      65.412      82.195
PB1           -0.0098      0.086     -0.113      0.910      -0.181       0.162
PB2           -0.1060      0.101     -1.047      0.298      -0.307       0.095
PB3            0.0719      0.071      1.015      0.313      -0.069       0.213
PB4            0.1498      0.090      1.664      0.100      -0.029       0.329
PB5           -0.0026      0.072     -0.036      0.972      -0.145       0.140
==============================================================================
Omnibus:                        5.420   Durbin-Watson:                   1.672
Prob(Omnibus):                  0.067   Jarque-Bera (JB):                5.018
Skew:                          -0.410   Prob(JB):                       0.0814
Kurtosis:                       3.797   Cond. No.                         713.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

--- Model: Combined
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj04   R-squared:                       0.131
Model:                            OLS   Adj. R-squared:                  0.024
Method:                 Least Squares   F-statistic:                     1.226
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.287
Time:                        12:11:00   Log-Likelihood:                -308.05
No. Observations:                  92   AIC:                             638.1
Df Residuals:                      81   BIC:                             665.8
Df Model:                          10
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const          2.7509     37.431      0.073      0.942     -71.725      77.227
CG1            0.7142      0.922      0.775      0.441      -1.120       2.548
CG2           -0.4719      0.805     -0.586      0.560      -2.074       1.131
CG3           -0.0421      0.393     -0.107      0.915      -0.824       0.740
CG4           -0.2305      0.225     -1.022      0.310      -0.679       0.218
CG5            0.9174      0.675      1.360      0.178      -0.425       2.260
PB1           -0.0554      0.094     -0.589      0.558      -0.243       0.132
PB2           -0.1307      0.104     -1.253      0.214      -0.338       0.077
PB3            0.0679      0.099      0.686      0.494      -0.129       0.265
PB4            0.0992      0.099      1.001      0.320      -0.098       0.297
PB5            0.0053      0.076      0.070      0.945      -0.145       0.156
==============================================================================
Omnibus:                        5.828   Durbin-Watson:                   1.747
Prob(Omnibus):                  0.054   Jarque-Bera (JB):                6.697
Skew:                          -0.311   Prob(JB):                       0.0351
Kurtosis:                       4.166   Cond. No.                     1.14e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.14e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Outcome: Subj05
--- Model: CG_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj05   R-squared:                       0.157
Model:                            OLS   Adj. R-squared:                  0.108
Method:                 Least Squares   F-statistic:                     3.212
Date:                Fri, 29 May 2026   Prob (F-statistic):             0.0105
Time:                        12:11:00   Log-Likelihood:                -358.92
No. Observations:                  92   AIC:                             729.8
Df Residuals:                      86   BIC:                             745.0
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -79.7433     51.556     -1.547      0.126    -182.233      22.747
CG1            0.8623      1.499      0.575      0.567      -2.118       3.842
CG2           -1.0785      1.326     -0.813      0.418      -3.714       1.557
CG3           -0.1628      0.480     -0.339      0.735      -1.116       0.791
CG4           -0.2621      0.365     -0.719      0.474      -0.987       0.463
CG5            2.4224      0.704      3.443      0.001       1.024       3.821
==============================================================================
Omnibus:                        6.613   Durbin-Watson:                   1.218
Prob(Omnibus):                  0.037   Jarque-Bera (JB):                6.306
Skew:                          -0.636   Prob(JB):                       0.0427
Kurtosis:                       3.167   Cond. No.                     7.74e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 7.74e+03. This might indicate that there are
strong multicollinearity or other numerical problems.

--- Model: PB_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj05   R-squared:                       0.082
Model:                            OLS   Adj. R-squared:                  0.029
Method:                 Least Squares   F-statistic:                     1.541
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.186
Time:                        12:11:00   Log-Likelihood:                -362.85
No. Observations:                  92   AIC:                             737.7
Df Residuals:                      86   BIC:                             752.8
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         58.4580      7.403      7.896      0.000      43.741      73.175
PB1            0.0193      0.151      0.127      0.899      -0.282       0.320
PB2           -0.0744      0.177     -0.419      0.676      -0.427       0.278
PB3            0.1481      0.124      1.192      0.237      -0.099       0.395
PB4            0.1961      0.158      1.242      0.218      -0.118       0.510
PB5            0.0120      0.126      0.096      0.924      -0.238       0.262
==============================================================================
Omnibus:                       10.559   Durbin-Watson:                   1.102
Prob(Omnibus):                  0.005   Jarque-Bera (JB):               10.854
Skew:                          -0.823   Prob(JB):                      0.00440
Kurtosis:                       3.348   Cond. No.                         713.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

--- Model: Combined
                            OLS Regression Results
==============================================================================
Dep. Variable:                 Subj05   R-squared:                       0.171
Model:                            OLS   Adj. R-squared:                  0.069
Method:                 Least Squares   F-statistic:                     1.671
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.102
Time:                        12:11:00   Log-Likelihood:                -358.17
No. Observations:                  92   AIC:                             738.3
Df Residuals:                      81   BIC:                             766.1
Df Model:                          10
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -63.0349     64.544     -0.977      0.332    -191.458      65.388
CG1            1.0269      1.589      0.646      0.520      -2.135       4.189
CG2           -1.1875      1.389     -0.855      0.395      -3.951       1.576
CG3            0.1558      0.677      0.230      0.819      -1.192       1.504
CG4           -0.3336      0.389     -0.858      0.393      -1.107       0.440
CG5            1.8830      1.163      1.619      0.109      -0.432       4.198
PB1           -0.0277      0.162     -0.171      0.865      -0.350       0.295
PB2           -0.1464      0.180     -0.814      0.418      -0.504       0.211
PB3            0.1409      0.171      0.826      0.411      -0.199       0.480
PB4            0.0948      0.171      0.554      0.581      -0.245       0.435
PB5            0.0012      0.130      0.010      0.992      -0.258       0.261
==============================================================================
Omnibus:                        7.701   Durbin-Watson:                   1.246
Prob(Omnibus):                  0.021   Jarque-Bera (JB):                7.344
Skew:                          -0.673   Prob(JB):                       0.0254
Kurtosis:                       3.323   Cond. No.                     1.14e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.14e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Outcome: GEN_AVE
--- Model: CG_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                GEN_AVE   R-squared:                       0.139
Model:                            OLS   Adj. R-squared:                  0.088
Method:                 Least Squares   F-statistic:                     2.767
Date:                Fri, 29 May 2026   Prob (F-statistic):             0.0229
Time:                        12:11:00   Log-Likelihood:                -328.53
No. Observations:                  92   AIC:                             669.1
Df Residuals:                      86   BIC:                             684.2
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -38.6961     37.050     -1.044      0.299    -112.349      34.956
CG1            0.8137      1.077      0.755      0.452      -1.328       2.955
CG2           -0.8847      0.953     -0.928      0.356      -2.779       1.010
CG3           -0.0453      0.345     -0.132      0.896      -0.731       0.640
CG4           -0.1624      0.262     -0.620      0.537      -0.683       0.358
CG5            1.5768      0.506      3.119      0.002       0.572       2.582
==============================================================================
Omnibus:                        0.522   Durbin-Watson:                   1.514
Prob(Omnibus):                  0.770   Jarque-Bera (JB):                0.672
Skew:                          -0.132   Prob(JB):                        0.715
Kurtosis:                       2.676   Cond. No.                     7.74e+03
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 7.74e+03. This might indicate that there are
strong multicollinearity or other numerical problems.

--- Model: PB_only
                            OLS Regression Results
==============================================================================
Dep. Variable:                GEN_AVE   R-squared:                       0.096
Model:                            OLS   Adj. R-squared:                  0.044
Method:                 Least Squares   F-statistic:                     1.830
Date:                Fri, 29 May 2026   Prob (F-statistic):              0.115
Time:                        12:11:00   Log-Likelihood:                -330.74
No. Observations:                  92   AIC:                             673.5
Df Residuals:                      86   BIC:                             688.6
Df Model:                           5
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         64.3213      5.222     12.318      0.000      53.941      74.702
PB1            0.0106      0.107      0.099      0.921      -0.202       0.223
PB2           -0.1373      0.125     -1.097      0.276      -0.386       0.112
PB3            0.0947      0.088      1.080      0.283      -0.080       0.269
PB4            0.2244      0.111      2.015      0.047       0.003       0.446
PB5           -0.0194      0.089     -0.219      0.828      -0.196       0.157
==============================================================================
Omnibus:                        1.845   Durbin-Watson:                   1.456
Prob(Omnibus):                  0.397   Jarque-Bera (JB):                1.670
Skew:                          -0.213   Prob(JB):                        0.434
Kurtosis:                       2.496   Cond. No.                         713.
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

--- Model: Combined
                            OLS Regression Results
==============================================================================
Dep. Variable:                GEN_AVE   R-squared:                       0.177
Model:                            OLS   Adj. R-squared:                  0.075
Method:                 Least Squares   F-statistic:                     1.737
Date:                Fri, 29 May 2026   Prob (F-statistic):             0.0864
Time:                        12:11:00   Log-Likelihood:                -326.45
No. Observations:                  92   AIC:                             674.9
Df Residuals:                      81   BIC:                             702.6
Df Model:                          10
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const        -28.9797     45.721     -0.634      0.528    -119.950      61.990
CG1            1.1140      1.126      0.990      0.325      -1.126       3.354
CG2           -0.9896      0.984     -1.006      0.317      -2.947       0.968
CG3            0.0745      0.480      0.155      0.877      -0.880       1.029
CG4           -0.2587      0.275     -0.940      0.350      -0.807       0.289
CG5            1.2228      0.824      1.484      0.142      -0.417       2.862
PB1           -0.0402      0.115     -0.349      0.728      -0.269       0.188
PB2           -0.1778      0.127     -1.396      0.167      -0.431       0.076
PB3            0.0953      0.121      0.789      0.433      -0.145       0.336
PB4            0.1578      0.121      1.303      0.196      -0.083       0.399
PB5           -0.0196      0.092     -0.213      0.832      -0.203       0.164
==============================================================================
Omnibus:                        0.460   Durbin-Watson:                   1.623
Prob(Omnibus):                  0.794   Jarque-Bera (JB):                0.284
Skew:                          -0.136   Prob(JB):                        0.868
Kurtosis:                       3.019   Cond. No.                     1.14e+04
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
[2] The condition number is large, 1.14e+04. This might indicate that there are
strong multicollinearity or other numerical problems.

Logistic Regression Results:
--- Model: CG_only
                           Logit Regression Results
==============================================================================
Dep. Variable:             PassBinary   No. Observations:                   92
Model:                          Logit   Df Residuals:                       86
Method:                           MLE   Df Model:                            5
Date:                Fri, 29 May 2026   Pseudo R-squ.:                  0.1365
Time:                        12:11:00   Log-Likelihood:                -53.172
converged:                       True   LL-Null:                       -61.578
Covariance Type:            nonrobust   LLR p-value:                  0.004868
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept    -31.1807     10.766     -2.896      0.004     -52.281     -10.080
CG1            0.4116      0.291      1.416      0.157      -0.158       0.981
CG2           -0.1852      0.250     -0.740      0.459      -0.676       0.305
CG3           -0.0975      0.103     -0.943      0.346      -0.300       0.105
CG4           -0.1979      0.145     -1.370      0.171      -0.481       0.085
CG5            0.4297      0.143      2.998      0.003       0.149       0.711
==============================================================================

--- Model: PB_only
                           Logit Regression Results
==============================================================================
Dep. Variable:             PassBinary   No. Observations:                   92
Model:                          Logit   Df Residuals:                       86
Method:                           MLE   Df Model:                            5
Date:                Fri, 29 May 2026   Pseudo R-squ.:                 0.07425
Time:                        12:11:00   Log-Likelihood:                -57.006
converged:                       True   LL-Null:                       -61.578
Covariance Type:            nonrobust   LLR p-value:                    0.1035
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept     -2.1340      1.257     -1.698      0.090      -4.598       0.330
PB1            0.0171      0.026      0.647      0.518      -0.035       0.069
PB2           -0.0429      0.030     -1.430      0.153      -0.102       0.016
PB3            0.0188      0.021      0.878      0.380      -0.023       0.061
PB4            0.0510      0.028      1.797      0.072      -0.005       0.107
PB5           -0.0009      0.022     -0.039      0.969      -0.044       0.042
==============================================================================

--- Model: Combined
                           Logit Regression Results
==============================================================================
Dep. Variable:             PassBinary   No. Observations:                   92
Model:                          Logit   Df Residuals:                       81
Method:                           MLE   Df Model:                           10
Date:                Fri, 29 May 2026   Pseudo R-squ.:                  0.1716
Time:                        12:11:00   Log-Likelihood:                -51.012
converged:                       True   LL-Null:                       -61.578
Covariance Type:            nonrobust   LLR p-value:                   0.02019
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept    -29.3029     12.614     -2.323      0.020     -54.027      -4.579
CG1            0.4710      0.309      1.526      0.127      -0.134       1.076
CG2           -0.2051      0.261     -0.786      0.432      -0.716       0.306
CG3           -0.0632      0.136     -0.466      0.641      -0.329       0.203
CG4           -0.1995      0.130     -1.533      0.125      -0.455       0.056
CG5            0.3272      0.226      1.450      0.147      -0.115       0.769
PB1            0.0002      0.031      0.008      0.994      -0.061       0.062
PB2           -0.0588      0.033     -1.763      0.078      -0.124       0.007
PB3            0.0263      0.034      0.781      0.435      -0.040       0.092
PB4            0.0417      0.033      1.277      0.202      -0.022       0.106
PB5         5.082e-05      0.026      0.002      0.998      -0.051       0.051
==============================================================================

## File: summary_stats.csv

Source path: C:\MEGA Cloud\Teaching Stuff\Research\Rad Tech Grades and Board Exam\Research Agent\research_agent\projects\sample_project\statresults\summary_stats.csv
Extraction status: extracted

Extraction warning: Table preview limited to first 100 rows.

### Extracted Content

Unnamed: 0,count,mean,std,min,25%,50%,75%,max
CG1,92.0,87.59627329192546,4.21099750363537,58.57142857142857,85.75,87.57142857142857,90.14285714285714,94.0
CG2,92.0,85.7463768115942,4.789174189194864,52.666666666666664,83.0,86.5,89.0,92.0
CG3,92.0,86.71135265700482,4.250373978058885,78.5,82.70833333333333,87.25,90.16666666666667,93.94444444444444
CG4,92.0,86.18925831202046,8.191794925058904,27.352941176470587,84.60294117647058,88.26470588235294,89.80882352941177,93.47058823529412
CG5,92.0,86.41351606805293,2.352144235242531,82.3913043478261,84.83695652173913,85.71739130434783,88.16304347826087,92.82608695652173
PB1,92.0,52.68478260869565,12.603792685620936,29.0,42.0,54.0,60.25,86.0
PB2,92.0,56.93478260869565,12.587106911112741,31.0,47.0,60.0,67.0,88.0
PB3,92.0,49.630434782608695,15.458357667841325,24.0,35.0,50.0,63.0,80.0
PB4,92.0,64.3804347826087,17.168103821327378,33.0,51.0,60.0,82.0,94.0
PB5,92.0,59.55434782608695,21.503571965194592,25.0,43.0,52.0,84.5,97.0
Subj01,92.0,68.41304347826087,10.95560689800357,50.0,62.0,67.0,77.75,90.0
Subj02,92.0,77.51086956521739,9.500138304623551,48.0,74.0,78.0,84.0,93.0
Subj03,92.0,73.09782608695652,12.029322948810732,44.0,66.0,77.5,81.5,92.0
Subj04,92.0,80.31521739130434,7.428678239887775,60.0,76.0,80.0,86.25,94.0
Subj05,92.0,75.93478260869566,13.111361022575407,42.0,67.5,81.0,84.5,95.0
GEN_AVE,92.0,75.05434782608697,9.318920998752175,57.6,68.2,76.0,82.85000000000001,91.6
