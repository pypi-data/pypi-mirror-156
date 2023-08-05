;; 1. Based on: 5
$PROBLEM    PHENOBARB SIMPLE MODEL
$INPUT      ID DV MDV OPRED D_EPS1 TIME AMT WGT APGR FA1 FA2 D_ETA1
            D_ETA2 OETA1 OETA2 D_EPSETA1_1 D_EPSETA1_2 TAD
$DATA      pheno_real_linbase.dta IGNORE=@ IGNORE(MDV.NEN.0)
$PRED
BASE1=D_ETA1*(ETA(1)-OETA1)
BASE2=D_ETA2*(ETA(2)-OETA2)
BSUM1=BASE1+BASE2
BASE_TERMS=BSUM1
IPRED=OPRED+BASE_TERMS
ERR1=EPS(1)*(D_EPS1+D_EPSETA1_1*(ETA(1)-OETA1))
ERR2=EPS(1)*(D_EPSETA1_2*(ETA(2)-OETA2))
ESUM1=ERR1+ERR2
ERROR_TERMS=ESUM1
Y=IPRED+ERROR_TERMS
$OMEGA  DIAGONAL(2)
 0.0285735  ;       IVCL
 0.0278954  ;        IVV
$SIGMA  0.013131
;$SIGMA  0.0130865
$SIMULATION (672686) SUBPROB=3
$ESTIMATION PRINT=1 MCETA=1 MAXEVALS=2
$ESTIMATION METHOD=COND INTERACTION PRINT=1 MCETA=1 MAXEVALS=2
$TABLE      ID DV MDV CWRES IPRED NOPRINT NOAPPEND ONEHEADER
            FILE=sim_res_table-1.dta
