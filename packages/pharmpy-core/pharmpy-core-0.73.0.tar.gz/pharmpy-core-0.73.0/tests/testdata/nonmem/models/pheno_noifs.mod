$PROBLEM PHENOBARB SIMPLE MODEL
$DATA ../pheno.dta IGNORE=@
$INPUT ID TIME AMT WGT APGR DV
$SUBROUTINE ADVAN1 TRANS2

$PK
TVCL=THETA(1)*WGT
TVV=THETA(2)*WGT
CL=TVCL*EXP(ETA(1))
V=TVV*EXP(ETA(2))
S1=V

$ERROR
W=F
Y=F+W*EPS(1)
IPRED=F
IRES=DV-IPRED
IWRES=IRES/W

$THETA (0,0.00469307) ; pCL
$THETA  (0,1.00916) ; pV
$OMEGA  DIAGONAL(2)
 0.0309626  ; IVCL
 0.031128  ; IVV

$SIGMA  1e-7    ; sigma
$ESTIMATION METHOD=1 INTERACTION
