$PROBLEM    PHENOBARB SIMPLE MODEL
$DATA      ../est_data1.dta IGNORE=@
$INPUT      ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN1 TRANS2
$PK
CL=THETA(1)*EXP(ETA(1))
V=THETA(2)*EXP(ETA(2))
S1=V

$ERROR
Y=F+F*EPS(1)

$THETA  (0,0.00469307) ; TVCL
$THETA  (0,1.00916) ; TVV
$OMEGA  0.0309626  ;       IVCL
$OMEGA  0.031128  ;        IVV
$SIGMA  0.013241
$ESTIMATION METHOD=1 INTERACTION
$COVARIANCE

