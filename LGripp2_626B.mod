MODULE LGripp2_626B
  !********************************************************************
  CONST string Ver_LGripp2:="ABB 5.1.1 - 2007-01-10 Type TCH";
  CONST string V_VCC_LGripp2:="VCC 5.1.1.A - 2007-01-11 Type TCH VCC";
  !********************************************************************
  !# A:First version for IRC5
  !******************   ABB IRB F-Pack  *******************************
  !Library for Gripp2
  ! Author:                  Johan Persson, ÅF AB
  !                                         Västra Storgatan 20
  !                                         SE-293 38 Olofström, Sweden
  ! CHANGES:
  !   05.04.2016             initial version
  !********************************************************************
  !# -----------------------------------------------
  !# ------ MESSAGE DECLARATIONS
  !# -----------------------------------------------
  LOCAL CONST string NotInSerPos{2}:=["Robot NOT in service position anymore ","Roboten är inte i sevice position mera "];
  LOCAL CONST string RobInLoosen{2}:=["Gripper in loosen position","Gripper är i lossa läge "];
  LOCAL CONST string LoosenBolts{2}:=["Loosen all bolts before calibrating !","Lossa alla bultar före kalibrering !"];
  LOCAL CONST string InfoManual{2}:=["Run in manual mode from here !","Fortsätt programkörning i manuell mode ! "];
  LOCAL CONST string WaitManual{2}:=["Waiting for manual mode !","Väntar på manuell mode ! "];
  LOCAL CONST string RobInGold{2}:=["Robot in Golden Position","Roboten är i Gyllene läge "];
  LOCAL CONST string TightenBolts{2}:=["Tighten all bolts before returning !","Dra fast alla bultar före återgång !"];
  LOCAL CONST string InCorrPath{2}:=["Incorrect pathselection ","Ogiltigt banval "];
  LOCAL CONST string RecevPath{2}:=["Received pathselection = ","Mottagit banvalet = "];
  LOCAL CONST string RobMovServ{2}:=["The Robot is moving to service position ","Roboten Rör sej mot serviceposition "];
  LOCAL CONST string InServWaitPLC{2}:=["Robot in service position waiting       PLC order to continue  ","Roboten är i service läge, väntar på    PLC order för att forsätta"];
  LOCAL CONST string ToolNeedServ{2}:=["Robot in service position               tool need service ","Roboten är i service läge.              verktyget behöver service"];

  !# -----------------------------------------------
  !# ------ ROBTARGETS
  !# -----------------------------------------------
  !# ------ ToolStand
  !-------- HomeToStand
  LOCAL CONST robtarget ToStand2P_20:=[[-367.99,1433.94,-930.6],[0.989193,-0.0478531,-0.0532671,0.127946],[0,0,0,0],[8471.78,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget ToStand2P_30:=[[-1.23,-0.73,-249.92],[0.999999,0.00118225,-0.00102166,0.000143424],[0,-1,1,0],[8599.67,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget ToStand2P_40:=[[0.01,-0.01,-200.00],[1,2.78206E-08,8.67277E-07,-3.37188E-07],[0,0,1,0],[8600.05,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget InStand2Put:=[[0,0,0],[1,0.000000419,0.000000537,-0.000000546],[0,0,-1,0],[8600.05,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget ToStand2P_05:=[[-98.09,-77.01,1165.50],[2.55199E-05,-2.57939E-05,0.707107,0.707106],[1,0,0,1],[2000,9E+09,9E+09,9E+09,9E+09,9E+09]];

  !-------- StandToPutCheck
  LOCAL CONST robtarget InPutCheckStand2P:=[[-0.00,0.00,-80.00],[1,-9.19183E-07,-7.4427E-07,-1.02358E-07],[0,0,-1,0],[8500,9E+09,9E+09,9E+09,9E+09,9E+09]];
  !-------- PutCheckToBetwen
  LOCAL CONST robtarget ToHomeNoTool2_10:=[[-0.07,-0.12,-199.72],[1,0.000081161,-0.000083686,-0.000035507],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget ToHomeNoTool2_20:=[[0,500,-332],[1,-0.00000002,0.000000031,0.000000008],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  !-------- BetwToStand
  LOCAL CONST robtarget ToStand2G_10:=[[-170.915931371,554.990044717,965.499540499],[0.000000176,0.000000155,0.707107416,0.707106146],[1,0,0,1],[2000,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget ToStand2G_15:=[[5.97,1694.87,-200.00],[1,3.08192E-09,2.16373E-08,-2.18557E-08],[1,0,0,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];

  LOCAL CONST robtarget ToStand2G_20:=[[0,497.72,-300],[1,-0.00000002,0.000000031,0.000000008],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget ToStand2G_30:=[[0,0,-80],[1,-0.000000013,0.000000013,0.000000038],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL PERS robtarget InStand2Get:=[[0,0,0],[1,0,0,0],[0,0,1,0],[8600.03,9E+09,9E+09,9E+09,9E+09,9E+09]];
  !-------- StandToGetChk
  LOCAL CONST robtarget InGetChk2:=[[0,0,-80],[1,-0.000000013,0.000000013,0.000000038],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  !-------- GetChkToHome
  LOCAL CONST robtarget FrGetChk2_10:=[[0.01,-0.05,-245.94],[1,0.000012458,-0.000014488,-0.000014528],[0,-1,-1,0],[8600.02,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget FrGetChk2_20:=[[0,497.16,-280],[1,-0.000000004,0.000000006,0.000000038],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget FrGetChk2_30:=[[0,1694.87,-280],[1,0.000000001,0.000000007,-0.000000008],[1,-1,0,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget FrGetChk2_40:=[[-42.34,-5381.72,1148.32],[0.0500823,0.541594,-0.833482,-0.0973419],[0,0,0,0],[7321.1,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget FrGetChk2_50:=[[-170.916385807,-77.009083266,1165.500684023],[0.000024563,-0.000024536,0.707106702,0.707106859],[1,0,0,1],[2000,9E+09,9E+09,9E+09,9E+09,9E+09]];
  !# ------ Service
  LOCAL CONST robtarget ToService2_10:=[[-10.70,-2422.97,2870.19],[0.587942,0.4429,0.494947,0.461727],[0,-1,0,4],[2378.35,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget ToService2_20:=[[486.78,-1293.37,2709.44],[0.175609,0.103531,0.843584,0.496799],[0,-1,0,0],[2378.35,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget InService2:=[[181.22,-579.79,1033.40],[0.320663,-0.654548,-0.395628,-0.558766],[1,0,1,1],[2377.93,9E+09,9E+09,9E+09,9E+09,9E+09]];
  !# -----------------------------------------------
  !# ------ HOMEPOSITION
  !# -----------------------------------------------
  CONST jointtarget HomeGripp2:=[[0.303952,-48.0292,-9.38968,-4.12509,73.5655,80.6662],[11516.2,9E+09,9E+09,9E+09,9E+09,9E+09]];
  !# -----------------------------------------------
  !# ------ WORKOBJECT DATA
  !# -----------------------------------------------
  PERS wobjdata ToolStand2:=[FALSE,TRUE,"",[[1584.99,-7294.06,270.018],[2.62357E-05,-0.707113,-0.707101,1.39439E-06]],[[0,0,0],[1,0,0,0]]];
  !# -----------------------------------------------
  !# ------ TOOL DATA
  !    !# -----------------------------------------------
  PERS tooldata Gripp2Tcp_BackLeft:=[TRUE,[[833.368132043,730.421953125,514.473335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_Back2:=[TRUE,[[752.489132043,818.483953125,394.031335937],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_Pin2:=[TRUE,[[113.289132043,717.999953125,440.749335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_Back1:=[TRUE,[[749.429132043,-917.686046875,393.989335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_FrontMitt:=[TRUE,[[-588.766867957,-50.000046875,367.093335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_BackMitt:=[TRUE,[[464.170132043,-50.000046875,555.190335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_Pin1:=[TRUE,[[113.289132043,-818.000046875,440.750335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_Front2:=[TRUE,[[-550.935867957,386.694953125,367.767335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2Tcp_BackRight:=[TRUE,[[832.824132043,-833.119046875,514.146335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  CONST tooldata Gripp2NomTCP:=[TRUE,[[0,0,341.331712532],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP:=[TRUE,[[0,0,341.331712532],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  PERS tooldata Gripp2TCP_Front1:=[TRUE,[[-550.086867957,-486.449046875,367.599335938],[1,0,0,0]],[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195]];
  !# -----------------------------------------------
  !# ------ LOAD DATA
  !# -----------------------------------------------
  PERS loaddata Gripp2Load:=[125.2,[74.5,2.6,155.8],[1,0,0,0],15.299,1.804,36.195];
  !# -----------------------------------------------
  !# ------ GRIPPER DATA
  !# -----------------------------------------------
  !# -----------------------------------------------
  !# ------ GRIPPER DATA
  !# -----------------------------------------------
  PERS ClampSeqdata Gripp2Pin11Cls:=["close gripper seq 1(Styrpine 11)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Pin11Opn:=["open gripper seq 1(Styrpine 11)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp13Cls:=["close gripper seq 2(Spänne 13)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp13Opn:=["open gripper seq 2(Spänne 13)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Index14Cls:=["close gripper seq 3(Index 14)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Index14Opn:=["close gripper seq 4(Spänne 16)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp16Cls:=["close gripper seq 4(Spänne 16)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp16Opn:=["open gripper seq 4(Spänne 16)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp17Cls:=["close gripper seq 5(Spänne 17)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp17Opn:=["open gripper seq 5(Spänne 17)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp18Cls:=["close gripper seq 6(Spänne 18)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS ClampSeqdata Gripp2Clamp18Opn:=["open gripper seq 6(Spänne 18)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
  PERS Vacuumdata Gripp2Vacuum12:=["Vacuumdata for Gripper 1(Vacuum 12)",1,TRUE,FALSE,TRUE];
  PERS Vacuumdata Gripp2Vacuum15:=["Vacuumdata for Gripper 1(Vacuum 15)",1,TRUE,FALSE,TRUE];
  PERS Vacuumdata Gripp2Vacuum16:=["Vacuumdata for Gripper 1(Vacuum 15)",1,TRUE,FALSE,TRUE];
  PERS PartChkdata Gripp2Vacuum12Pr:=["PartChkData for Gripper 1(Vacuum 12)",1,TRUE,FALSE,FALSE,FALSE];
  PERS PartChkdata Gripp2Vacuum15Pr:=["PartChkData for Gripper 1(Vacuum 15)",2,TRUE,TRUE,FALSE,FALSE];

  !# -----------------------------------------------
  !# ------ TOOL ID
  !# -----------------------------------------------
  CONST gunnum Gripp2:=2;
  !# -----------------------------------------------
  !#------- GAP SERVICE MENUS
  !# -----------------------------------------------
  !TASK PERS menudata md_Gripp2Serv:=["Gripp2#Gripp2 to service. This service must be exequted in manual","","Gripp2ServSch",1,"",1,True,2,1,True,53];
  !TASK PERS menudata md_Gripp2TCSch:=["Gripp2#Gripp2 ToolChange service. This service must be exequted in manual","","Gripp2ToolCha",1,"",1,True,2,1,True,43];
  !# -----------------------------------------------
  !# ------ OTHER DECLARATIONS
  !# -----------------------------------------------
  CONST bool Gripp2TolCover:=FALSE;
  LOCAL CONST Locksignal WaitService:=[102,""];
  !# -----------------------------------------------
  !# ------ SUB PROCEDURES
  !# -----------------------------------------------
  LOCAL CONST num Pins_11:=1;
  LOCAL CONST num Clamps_13:=2;
  LOCAL CONST num Index14_Vacuum12:=3;
  LOCAL CONST num Clamps_16:=4;
  LOCAL CONST num Clamps_17:=5;
  LOCAL CONST num Vacuum12:=11;
  LOCAL CONST num Vacuum15:=12;
  LOCAL CONST num Clamps_18:=6;
  !*************************************************************************
  ! PLC signals
  !*************************************************************************
  LOCAL CONST Locksignal DriftZon1_2:=[200,"Drift till Zon 1-2"];
  CONST robtarget ToStand2P_50:=[[-0.00,0.00,-80.00],[0.999996,-0.00227757,-0.000858804,-0.00134613],[0,0,-1,0],[8500,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget InPutStand2P:=[[-0.46,-3.55,916.36],[1,-8.75544E-07,-7.855E-07,-1.17665E-07],[0,0,-1,0],[8700,9E+09,9E+09,9E+09,9E+09,9E+09]];
  CONST robtarget InService12:=[[-173.09,-5566.62,1256.95],[0.00209225,-0.543791,0.818245,0.186447],[1,0,0,0],[7272.04,9E+09,9E+09,9E+09,9E+09,9E+09]];
  LOCAL CONST robtarget InPutCheck2:=[[0,0,-80],[1,-0.000000013,0.000000013,0.000000038],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  CONST robtarget ToStand2P_10:=[[-38.94,-5456.87,1019.4],[0.00321743,0.527003,-0.83794,-0.141822],[0,0,0,0],[7354.09,9E+09,9E+09,9E+09,9E+09,9E+09]];
  CONST robtarget p10:=[[4.72,55.44,-241.45],[1,8.29664E-05,-8.36357E-05,-3.7697E-05],[0,0,-1,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  CONST robtarget p190:=[[0.00,1694.87,-1049.53],[1,1.49173E-06,9.2353E-07,-4.58944E-07],[1,0,0,0],[8600,9E+09,9E+09,9E+09,9E+09,9E+09]];
  CONST robtarget p200:=[[-79.54,-6159.79,1240.41],[0.0212407,-0.65425,0.752693,0.0704252],[1,0,0,0],[8190.1,9E+09,9E+09,9E+09,9E+09,9E+09]];

  PROC IniGripp2()
    !***************************************
    ! Routine:IniGripp2
    ! Description:Init Tool Gripper 1
    !
    !***************************************
    IO_Enable 12,Unit_timeout,TRUE;
    IO_Enable 13,Unit_timeout,TRUE;
    IO_Enable 16,Unit_timeout,TRUE;
    ToolCover{Gripp2}:=Gripp2TolCover;
    MappIO_Gripp2;
    RETURN ;
  ENDPROC

  PROC MoveTooLGripp2setup()
    MoveTool Gripp2,HomeToStand;
    MoveTool Gripp2,StandToPutchk;
    MoveTool Gripp2,PutchkToBetw;
    MoveTool Gripp2,BetwToStand;
    MoveTool Gripp2,StandToGetchk;
    MoveTool Gripp2,GetchkToHome;
  ENDPROC

  PROC MappIO_Gripp2()
    !***************************************
    ! Routine:MappIO_Gripp2
    ! Description:I/O setup for Gripper 3
    !
    !***************************************
    !**** Mapping of gripper I/O ****
    !**** Clamping Sequence 1 Close ****
    !Styrpinne 11 Till
    !Alias Connection
    AliasIO O_GRIP5_Chan1,OutSeq1Cls;
    AliasIO I_GRIP1_Chan9,Inp1Seq1Cls;
    AliasIO I_GRIP1_Chan10,Inp2Seq1Cls;
    !Data Assignment
    Gripp2Pin11Cls:=["close gripper seq 1(Styrpine 11)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq1Cls:=Gripp2Pin11Cls;
    !Alarmdata
    A_Inp1Seq1Opn:=["Signal on Gripper Open - Inp1 Seq1 Opn","Signal på Styrpinne Från - 14S11R1",5,153];
    A_Inp1Seq1ClsN:=["Missing Signal - Input1 Seq1 Cls Gripp","Saknar Signal Styrpinne Till- 14S11S1",5,153];
    A_Inp2Seq1Opn:=["Signal on Gripper Open - Inp2 Seq1 Opn","Signal på Styrpinne Från - 14S11R2",5,153];
    A_Inp2Seq1ClsN:=["Missing Signal - Input2 Seq1 Cls Gripp","Saknar Signal Styrpinne Till- 14S11S2",5,153];
    !**** Clamping Sequence 1 Open****
    !Styrpinne 11 Från
    !Alias Connection
    AliasIO O_GRIP5_Chan2,OutSeq1Opn;
    AliasIO I_GRIP1_Chan1,Inp1Seq1Opn;
    AliasIO I_GRIP1_Chan2,Inp2Seq1Opn;
    !Data Assignment
    Gripp2Pin11Opn:=["open gripper seq 1(Styrpine 11)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq1Opn:=Gripp2Pin11Opn;
    !Alarmdata
    A_Inp1Seq1Cls:=["Signal on Gripper Close - Inp1 Seq1 Cls","Signal på Styrpinne Till - 14S11S1",5,154];
    A_Inp1Seq1OpnN:=["Missing Signal - Input1 Seq1 Opn Gripp","Saknar Signal Styrpinne Från- 14S11R1",5,154];
    A_Inp2Seq1Cls:=["Signal on Gripper Close - Inp2 Seq1 Cls","Signal på Styrpinne Till - 14S11S2",5,154];
    A_Inp2Seq1OpnN:=["Missing Signal - Input2 Seq1 Opn Gripp","Saknar Signal Styrpinne Från- 14S11R2",5,154];
    !**** Clamping Sequence 2 Close ****
    !Spänne 13 Till
    !Alias Connection
    AliasIO O_GRIP5_Chan5,OutSeq2Cls;
    AliasIO I_GRIP2_Chan14,Inp1Seq2Cls;
    !Data Assignment
    Gripp2Clamp13Cls:=["close gripper seq 2(Spänne 13)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq2Cls:=Gripp2Clamp13Cls;
    !Alarmdata
    A_Inp1Seq2Opn:=["Signal on Gripper Open - Inp1 Seq2 Opn","Signal på Spänne Från - 14S13R1-R4",5,153];
    A_Inp1Seq2ClsN:=["Missing Signal - Input1 Seq2 Cls Gripp","Saknar Signal Spänne Till- 14S13S1-S4",5,153];
    !**** Clamping Sequence 2 Open****
    !Spänne 13 Från
    !Alias Connection
    AliasIO O_GRIP5_Chan6,OutSeq2Opn;
    AliasIO I_GRIP2_Chan6,Inp1Seq2Opn;
    !Data Assignment
    Gripp2Clamp13Opn:=["open gripper seq 2(Spänne 13)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq2Opn:=Gripp2Clamp13Opn;
    !Alarmdata
    A_Inp1Seq2Cls:=["Signal on Gripper Close - Inp1 Seq2 Cls","Signal på Spänne Till- 14S13S1-S4",5,154];
    A_Inp1Seq2OpnN:=["Missing Signal - Input1 Seq2 Opn Gripp","Saknar Signal Spänne Från - 14S13R1-R4",5,154];
    !**** Clamping Sequence 3 Close ****
    !Index 14 Till
    !Alias Connection
    AliasIO O_GRIP5_Chan7,OutSeq3Cls;
    AliasIO I_GRIP1_Chan11,Inp1Seq3Opn;
    AliasIO I_GRIP1_Chan12,Inp2Seq3Opn;


    !Data Assignment
    Gripp2Index14Cls:=["close gripper seq 3(Index 14)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq3Cls:=Gripp2Index14Cls;
    !Alarmdata
    A_Inp1Seq3Opn:=["Signal on Gripper Open - Inp1 Seq3 Opn","Signal på Index Från - 14S14R1",5,153];
    A_Inp1Seq3ClsN:=["Missing Signal - Input1 Seq3 Cls Gripp","Saknar Signal Index Till - 14S14S1",5,153];
    A_Inp2Seq3Opn:=["Signal on Gripper Open - Inp2 Seq3 Opn","Signal på Index Från - 14S14R2",5,153];
    A_Inp2Seq3ClsN:=["Missing Signal - Input2 Seq3 Cls Gripp","Saknar Signal Index Till - 14S14S2",5,153];

    !**** Clamping Sequence 3 Open****
    !Index 14 Från
    !Alias Connection
    AliasIO O_GRIP5_Chan8,OutSeq3Opn;
    AliasIO I_GRIP1_Chan3,Inp1Seq3Cls;
    AliasIO I_GRIP1_Chan4,Inp2Seq3Cls;

    !Data Assignment
    Gripp2Index14Opn:=["close gripper seq 4(Spänne 16)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq3Opn:=Gripp2Index14Opn;
    !Alarmdata
    A_Inp1Seq3Cls:=["Signal on Gripper Close - Inp1 Seq3 Cls","Signal på Index Till - 14S14S1",5,154];
    A_Inp1Seq3OpnN:=["Missing Signal - Input1 Seq3 Opn Gripp","Saknar Signal Index Från - 14S14R1",5,154];
    A_Inp2Seq3Cls:=["Signal on Gripper Close - Inp2 Seq3 Cls","Signal på Index Till - 14S14S2",5,154];
    A_Inp2Seq3OpnN:=["Missing Signal - Input2 Seq3 Opn Gripp","Saknar Signal Index Från - 14S14R2",5,154];

    !**** Clamping Sequence 4 Close ****
    !Spänne 16 Till
    !Alias Connection
    AliasIO O_GRIP5_Chan11,OutSeq4Cls;
    AliasIO I_GRIP1_Chan13,Inp1Seq4Cls;
    AliasIO I_GRIP1_Chan14,Inp2Seq4Cls;
    !Data Assignment
    Gripp2Clamp16Cls:=["close gripper seq 4(Spänne 16)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq4Cls:=Gripp2Clamp16Cls;
    !Alarmdata
    A_Inp1Seq4Opn:=["Signal on Gripper Open - Inp1 Seq4 Opn","Signal på Spänne Från - 14S16R1",5,153];
    A_Inp1Seq4ClsN:=["Missing Signal - Input1 Seq4 Cls Gripp","Saknar Signal Spänne Till - 14S16S1",5,153];
    A_Inp2Seq4Opn:=["Signal on Gripper Open - Inp2 Seq4 Opn","Signal på Spänne Från - 14S16R2",5,153];
    A_Inp2Seq4ClsN:=["Missing Signal - Input2 Seq4 Cls Gripp","Saknar Signal Spänne Till - 14S16S2",5,153];
    !**** Clamping Sequence 4 Open****
    !Spänne 16 Från
    !Alias Connection
    AliasIO O_GRIP5_Chan12,OutSeq4Opn;
    AliasIO I_GRIP1_Chan5,Inp1Seq4Opn;
    AliasIO I_GRIP1_Chan6,Inp2Seq4Opn;
    !Data Assignment
    Gripp2Clamp16Opn:=["open gripper seq 4(Spänne 16)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq4Opn:=Gripp2Clamp16Opn;
    !Alarmdata
    A_Inp1Seq4Cls:=["Signal on Gripper Close - Inp1 Seq4 Cls","Signal på Spänne Till - 14S16S1",5,154];
    A_Inp1Seq4OpnN:=["Missing Signal - Input1 Seq4 Opn Gripp","Saknar Signal Spänne Från - 14S16R1",5,154];
    A_Inp2Seq4Cls:=["Signal on Gripper Close - Inp2 Seq4 Cls","Signal på Spänne Till - 14S16S2",5,154];
    A_Inp2Seq4OpnN:=["Missing Signal - Input2 Seq4 Opn Gripp","Saknar Signal Spänne Från - 14S16R2",5,154];
    !**** Clamping Sequence 5 Close ****
    !Spänne 17 Till
    !Alias Connection
    AliasIO O_GRIP5_Chan13,OutSeq5Cls;
    AliasIO I_GRIP2_Chan15,Inp1Seq5Cls;
    !Data Assignment
    Gripp2Clamp17Cls:=["close gripper seq 5(Spänne 17)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq5Cls:=Gripp2Clamp17Cls;
    !Alarmdata

    A_Inp1Seq5Opn:=["Signal on Gripper Open - Inp4 Seq5 Opn","Signal på Spänne 17 Från - 14S17R4",5,153];
    A_Inp1Seq5ClsN:=["Missing Signal - Input4 Seq5 Cls Gripp","Saknar Signal Spänne 17 Till - 14S17S4",5,153];
    !**** Clamping Sequence 5 Open****
    !Spänne 17 Från
    !Alias Connection
    AliasIO O_GRIP5_Chan14,OutSeq5Opn;
    AliasIO I_GRIP2_Chan7,Inp1Seq5Opn;
    !Data Assignment
    Gripp2Clamp17Opn:=["open gripper seq 5(Spänne 17)",1,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq5Opn:=Gripp2Clamp17Opn;
    !Alarmdata

    A_Inp1Seq5Cls:=["Signal on Gripper Close - Inp4 Seq5 Cls","Signal på Spänne 17 Till - 14S17S4",5,154];
    A_Inp1Seq5OpnN:=["Missing Signal - Input4 Seq5 Opn Gripp","Saknar Signal Spänne 17 Från - 14S17R4",5,154];
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !**** Clamping Sequence 6 Close ****
    !Spänne 18 Till
    !Alias Connection
    AliasIO O_GRIP5_Chan15,OutSeq6Cls;
    AliasIO I_GRIP2_Chan9,Inp1Seq6Cls;
    AliasIO I_GRIP2_Chan10,Inp2Seq6Cls;
    !Data Assignment
    Gripp2Clamp18Cls:=["close gripper seq 6(Spänne 18)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq6Cls:=Gripp2Clamp18Cls;
    !Alarmdata

    !A_Inp1Seq6Opn:=["Signal on Gripper Open - Inp1 Seq6 Opn","Signal på Spänne 18 Från - 14S18R1_R2",5,153];
    !A_Inp1Seq6ClsN:=["Missing Signal - Input2 Seq6 Cls Gripp","Saknar Signal Spänne 18 Till - 14S18S1_S2",5,153];
    !A_Inp2Seq6Opn:=["Signal on Gripper Open - Inp1 Seq6 Opn","Signal på Spänne 18 Från - 14S18R1_R2",5,153];
    !A_Inp2Seq6ClsN:=["Missing Signal - Input2 Seq6 Cls Gripp","Saknar Signal Spänne 18 Till - 14S18S1_S2",5,153];
    !**** Clamping Sequence 6 Open****
    !Spänne 18 Från
    !Alias Connection
    AliasIO O_GRIP5_Chan16,OutSeq6Opn;
    AliasIO I_GRIP2_Chan1,Inp1Seq6Opn;
    AliasIO I_GRIP2_Chan2,Inp2Seq6Opn;
    !Data Assignment
    Gripp2Clamp18Opn:=["open gripper seq 6(Spänne 18)",2,TRUE,TRUE,TRUE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,FALSE];
    ClampSeq6Opn:=Gripp2Clamp18Opn;
    !Alarmdata
    !A_Inp1Seq6Cls:=["Signal on Gripper Close - Inp1 Seq6 Cls","Signal på Spänne 18 Till - 14S18S1_S4",5,154];
    !A_Inp1Seq6OpnN:=["Missing Signal - Input2 Seq6 Opn Gripp","Saknar Signal Spänne 18 Från - 14S18R1_R4",5,154];
    !A_Inp2Seq6Cls:=["Signal on Gripper Close - Inp1 Seq6 Cls","Signal på Spänne 18 Till - 14S18S1_S4",5,154];
    !A_Inp2Seq6OpnN:=["Missing Signal - Input2 Seq6 Opn Gripp","Saknar Signal Spänne 18 Från - 14S18R1_R4",5,154];
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    !**** Declaration of Vacuum Sequense ****
    ! Vacuum 12
    !Alias Connection
    AliasIO I_Grip1_Chan8,InpVacu1IsOn;
    AliasIO O_GRIP5_Chan3,OutVacuum1On;
    AliasIO O_GRIP5_Chan4,OutVacuum1Off;
    !Data Assignment
    Gripp2Vacuum12:=["Vacuumdata for Gripper 1(Vacuum 12)",1,TRUE,FALSE,TRUE];
    Vacuum_1:=Gripp2Vacuum12;
    !Alarmdata
    A_Vacuum1N:=["Missing Vacuumsensor 1","Saknar Vacuumsensor 1 - 14SB12S1",5,161];
    A_Vacuum1:=["Signal on Vacuumsensor 1","Signal på Vacuumsensor 1 - 14SB12S1",5,162];
    !**** Declaration of Vacuum Sequense ****
    ! Vacuum 15
    !Alias Connection
    AliasIO I_Grip2_Chan8,InpVacu2IsOn;
    AliasIO O_GRIP5_Chan9,OutVacuum2On;
    AliasIO O_GRIP5_Chan10,OutVacuum2Off;
    !Data Assignment
    Gripp2Vacuum15:=["Vacuumdata for Gripper 1(Vacuum 15)",1,TRUE,FALSE,TRUE];
    Vacuum_2:=Gripp2Vacuum15;
    !Alarmdata
    A_Vacuum2N:=["Missing Vacuumsensor 2","Saknar Vacuumsensor 2 - 14SB15",5,161];
    A_Vacuum2:=["Signal on Vacuumsensor 2","Signal på Vacuumsensor 2 - 14SB15",5,162];



    !**** Declaration of Vacuum Sequense ****
    ! Vacuum 16
    !Alias Connection
    AliasIO I_Grip2_Chan16,InpVacu3IsOn;
    AliasIO O_GRIP5_Chan9,OutVacuum3On;
    AliasIO O_GRIP5_Chan10,OutVacuum3Off;
    !Data Assignment
    Gripp2Vacuum16:=["Vacuumdata for Gripper 1(Vacuum 15)",1,TRUE,FALSE,TRUE];
    Vacuum_3:=Gripp2Vacuum16;
    !Alarmdata
    A_Vacuum3N:=["Missing Vacuumsensor 2","Saknar Vacuumsensor 3 - 14SB16",5,161];
    A_Vacuum3:=["Signal on Vacuumsensor 2","Signal på Vacuumsensor 3 - 14SB16",5,162];
    !-------------------------------------------------------------
    !Part Sensors PartSpec 1
    !------------------------------------------------------------
    !Alias Connection
    AliasIO I_Grip1_Chan8,Inp1Part1Press;

    !Data Assignment
    Gripp2Vacuum12Pr:=["PartChkData for Gripper 1(Vacuum 12)",1,TRUE,FALSE,FALSE,FALSE];
    PartPres_1:=Gripp2Vacuum12Pr;
    !Alarmdata
    A_Sens1Part1N:=["Missing Signal - Detaljgivare Opåverkad","Saknar Vacuumsensor 1 - 14SB12S1",5,162];
    A_Sens1Part1:=["Part in Gripper - Detaljgivare","Signal på Vacuumsensor 1 - 14SB12S1",5,162];
    !-------------------------------------------------------------
    !Part Sensors PartSpec 2
    !------------------------------------------------------------
    !Alias Connection
    AliasIO I_Grip2_Chan8,Inp1Part2Press;
    AliasIO I_Grip2_Chan16,Inp2Part2Press;
    !Data Assignment
    Gripp2Vacuum15Pr:=["PartChkData for Gripper 1(Vacuum 15)",2,TRUE,TRUE,FALSE,FALSE];
    PartPres_2:=Gripp2Vacuum15Pr;
    !Alarmdata
    A_Sens1Part2N:=["Missing Signal - Detaljgivare Opåverkad","Saknar Vacuumsensor 2 - 14SB15S1",5,162];
    A_Sens1Part2:=["Part in Gripper - Detaljgivare","Signal på Vacuumsensor 2 - 14SB15S1",5,162];
    A_Sens2Part2N:=["Missing Signal - Detaljgivare Opåverkad","Saknar Vacuumsensor 2 - 14SB15S2",5,162];
    A_Sens2Part2:=["Part in Gripper - Detaljgivare","Signal på Vacuumsensor 2 - 14SB15S2",5,162];
    InitPrtSprVsn;
    RETURN ;
  ENDPROC


  PROC EndGripp2()
    !***************************************
    ! Routine:EndGripp2
    ! Description:Disable Tool Gripper 1
    !
    !***************************************
    IO_Disable 12,Unit_timeout,TRUE;
    IO_Disable 13,Unit_timeout,TRUE;
    IO_Disable 16,Unit_timeout,TRUE;
  ENDPROC

  PROC Gripp2GoldSch()

    VAR gunnum PreviousTool;
    VAR num key_in;
    !***************************************
    ! Routine:Gripp2GoldSch
    ! Description:Manual Gripper Calibration schedule
    ! for Gripp2
    !***************************************
    key_in:=0;

    Reset O_Homepos;
    PreviousTool:=ToolOnRobot();
    ToolChange(Gripp2);
    MoveTool Gripp2,HomeToGrippLoose;
    TPWrite RobInLoosen{Language};
    WaitTime 1;
    TPWrite InfoManual{Language};
    WaitTime 2;
    TPWrite "";
    WHILE key_in<>5 DO
      TPReadFK key_in,LoosenBolts{Language},"","","","","Cont.";
      WaitTime 2;
      TPErase;
    ENDWHILE
    WHILE OpMode()=OP_AUTO DO
      TPWrite WaitManual{Language};
      WaitTime 1;
      TPErase;
    ENDWHILE
    key_in:=0;
    MoveTool Gripp2,GrippLosToGolden;
    TPWrite RobInGold{Language};
    WaitTime 1;
    TPWrite "";
    WHILE key_in<>5 DO
      TPReadFK key_in,TightenBolts{Language},"","","","","Return";
      WaitTime 2;
      TPErase;
    ENDWHILE
    MoveTool Gripp2,GoldenToHome;
    ToolChange(PreviousTool);
  ENDPROC

  PROC Gripp2ToolCha()
    !***************************************
    ! Routine:Gripp2ToolCha
    ! Description:Tool change schedule
    ! for Gripper 1
    !***************************************
    Reset O_Homepos;
    WaitSignal DriftZon1_2;
    ToolChange Gripp2;
  ENDPROC

  PROC Gripp2ServSch()

    VAR gunnum PreviousTool;
    VAR num key_in;
    !***************************************
    ! Routine: Gripp2ServSch
    ! Description:Service schedule
    ! for Gripper 1
    !***************************************
    Reset O_Homepos;
    PreviousTool:=ToolOnRobot();
    ToolChange(Gripp2);
    ! The Robot is moving to service position
    TPWrite RobMovServ{Language};
    MoveTool Gripp2,HomeToServ;
    TPErase;
    IF OpMode()=OP_AUTO THEN
      TPWrite InServWaitPLC{Language};
      WaitSignal WaitService;
    ELSE
      TPReadFK key_in,ToolNeedServ{Language},"","","","","ReStart";
    ENDIF
    TPErase;
    MoveTool Gripp2,ServToHome;
    ToolChange(PreviousTool);

  ENDPROC


  !****************************************************
  PROC MoveTooLGripp2(
    num Direction)

    VAR num key_in;
    !*******************************
    ! Routine: MoveTooLGripp2(
    ! num Direction)
    ! Description: Movments in
    ! certain direction for Gripp2
    !*******************************
    TEST Direction
    CASE HomeToServ:
      MoveAbsJ HomeGripp2,v1500,fine,Gripp2TCP;
      MoveJ ToService2_10,v1500,z100,Gripp2TCP;
      MoveJ ToService2_20,v1500,z100,Gripp2TCP;
      MoveJ InService2,v500,fine,Gripp2TCP;
    CASE ServToHome:
      MoveJ InService2,v500,fine,Gripp2TCP;
      MoveJ ToService2_20,v1500,z100,Gripp2TCP;
      MoveJ ToService2_10,v1500,z100,Gripp2TCP;
      MoveAbsJ HomeGripp2,v1500,fine,Gripp2TCP;
    CASE HomeToStand:
      GripperClose Sequence4;
      ToolLoad NoToolTCP,Gripp2Load;
      GripperClose Clamps_18;
      GripperClose Clamps_17;
      MoveAbsJ HomeGripp2,v1500,fine,Gripp2TCP;
      MoveJ ToStand2P_10,v500,z100,Gripp2TCP;
      MoveJ ToStand2P_20,v500,z10,NoToolTCP\WObj:=ToolStand2;
      MoveL ToStand2P_30,v500,z1,NoToolTCP\WObj:=ToolStand2;
      MoveL ToStand2P_40,v500,z1,NoToolTCP\WObj:=ToolStand2;
      MoveL InStand2Put,v100,fine,NoToolTCP\WObj:=ToolStand2;
      !
    CASE StandToPutchk:
      ToolLoad NoToolTCP,NoToolLoad;
      MoveL InPutCheck2,v100,fine,NoToolTCP\WObj:=ToolStand2;
      !
    CASE PutchkToBetw:
      ToolLoad NoToolTCP,NoToolLoad;
      MoveL ToHomeNoTool2_10,v200,z50,NoToolTCP\WObj:=ToolStand2;
      MoveL p10,v200,z50,NoToolTCP\WObj:=ToolStand2;
      MoveL ToHomeNoTool2_20,v500,z10,NoToolTCP\WObj:=ToolStand2;
      MoveAbsJ HomeNoTool,vTrack500,fine,NoToolTCP;
      !
      WaitTime 0.01;
    CASE BetwToStand:
      ToolLoad Notooltcp,Notoolload;

      MoveJ ToStand2G_20,vTrack500,z10,NoToolTCP\WObj:=ToolStand2;
      MoveL ToStand2G_30,v500,z1,NoToolTCP\WObj:=ToolStand2;
      FrameL InStand2Get,v100,fine,NoToolTCP,ToolStand2;
      !
    CASE StandToGetchk:
      ToolLoad NoToolTCP,Gripp2Load;
      MoveL InGetChk2,v100,fine,NoToolTCP\WObj:=ToolStand2;
    CASE GetchkToHome:
      !Stop;
      IniGripp2;
      GripperClose Sequence4;
      GripperVacuumOff Vacuum1;
      GripperVacuumOff Vacuum2;
      ToolLoad notooltcp,Gripp2Load;
      MoveL FrGetChk2_10,v500,z1,NoToolTCP\WObj:=ToolStand2;
      MoveL FrGetChk2_20,v500,z10,NoToolTCP\WObj:=ToolStand2;
      !ConfJ\Off;
      MoveJ FrGetChk2_30,vRot50Track,z10,NoToolTCP\WObj:=ToolStand2;
      MoveJ p190,vRot50Track,z10,NoToolTCP\WObj:=ToolStand2;
      MoveJ p200,vRot50Track,z10,NoToolTCP;
      MoveJ FrGetChk2_40,vRot50Track,z10,NoToolTCP;
      MoveAbsJ HomeGripp2,vRot50Track,fine,Gripp2TCP;
      !
    CASE HomeToGrippLoose:
      STOP;
      !Insert positions and remove Stop
    CASE GrippLosToGolden:
      STOP;
      !Insert positions and remove Stop
    CASE GoldenToHome:
      STOP;
      !Insert positions and remove Stop
    DEFAULT:
      TPErase;
      ! Received pathselection =
      TPWrite RecevPath{Language}\Num:=Direction;
      ! Incorrect pathselection
      ErrDisplay A_TaskIsMissing,InCorrPath{Language},key_in\text1:=T_TXT_OK;
      SendAlarm A_TaskIsMissing,""\Reset;
      TPErase;
    ENDTEST
  ENDPROC



  PROC Clamp_TEST()
    GripperOpen Clamps_13;
    NoToolToolChaSch;
    Gripp2ToolCha;
    Gripp3ToolCha;
    Stop;
    GripperOpen Index14_Vacuum12;
    GripperOpen Pins_11;
    GripperOpen Index14_Vacuum12;
    GripperOpen Clamps_16;
    GripperOpen Clamps_17;
    GripperOpen Clamps_18;
    GripperClose Clamps_13;
    GripperClose Clamps_16;
    GripperClose Clamps_17;
    GripperClose Clamps_18;
    GripperClose Pins_11;
    GripperClose Index14_Vacuum12;
    IniGripp2;
    Stop;
  ENDPROC
ENDMODULE
