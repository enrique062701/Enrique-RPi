#ifndef DemoRemoteControlHPP
#define DemoRemoteControlHPP

#include <Grids.hpp>	// Pascal unit
#include <Chart.hpp>	// Pascal unit
#include <TeeProcs.hpp>	// Pascal unit
#include <Series.hpp>	// Pascal unit
#include <TeEngine.hpp>	// Pascal unit
#include <Buttons.hpp>	// Pascal unit
#include <ComCtrls.hpp>	// Pascal unit
#include <ExtCtrls.hpp>	// Pascal unit
#include <StdCtrls.hpp>	// Pascal unit
#include <Menus.hpp>	// Pascal unit
#include <ActnList.hpp>	// Pascal unit
//#include <REMOTECONTROL.hpp>	// Pascal unit
#include <Dialogs.hpp>	// Pascal unit
#include <Forms.hpp>	// Pascal unit
#include <Controls.hpp>	// Pascal unit
#include <Graphics.hpp>	// Pascal unit
#include <Classes.hpp>	// Pascal unit
#include <SysUtils.hpp>	// Pascal unit
#include <Messages.hpp>	// Pascal unit
#include <Windows.hpp>	// Pascal unit
#include <SysInit.hpp>	// Pascal unit
#include <System.hpp>
#include "CSPIN.h"	// Pascal unit

//-- type declarations -------------------------------------------------------
class TfrmMain : public Forms::TForm 
{
//	typedef Forms::TForm inherited;
	
__published:
        TActionList *ActionList;
        TMainMenu *MainMenu;
        TAction *aConnect;
        TAction *aDisconnect;
        TMenuItem *Connect1;
        TMenuItem *aDisconnect1;
        TTimer *Timer1sec;
        TStatusBar *StatusBar;
        TBitBtn *btStart;
        TBitBtn *btStop;
        TAction *aStart;
        TAction *aStop;
        TRadioGroup *rgOutput;
        TChart *chOut;
        TFastLineSeries *Series1;
        TRadioGroup *rgBatch;
        TFastLineSeries *Series2;
        TSpeedButton *btPack;
        TPanel *BatchPanel;
        TStringGrid *sgPList;
        TScrollBox *ScrollBox;
	void __fastcall aConnectExecute(TObject* Sender);
	void __fastcall aDisconnectExecute(TObject* Sender);
	void __fastcall Timer1secTimer(TObject* Sender);
	void __fastcall aStartExecute(TObject* Sender);
	void __fastcall aStopExecute(TObject* Sender);
	void __fastcall aOutputControlExecute(TObject* Sender);
	void __fastcall rgBatchClick(TObject* Sender);
        void __fastcall FormCreate(TObject *Sender);
        void __fastcall FormDestroy(TObject *Sender);
        void __fastcall btPackClick(TObject *Sender);
        void __fastcall SetClick(TObject *Sender);
        void __fastcall SetNVClick(TObject *Sender);
        void __fastcall EditEnter(TObject *Sender, char &Key);
        void __fastcall DownClick(TObject *Sender);
        void __fastcall UpClick(TObject *Sender);
        void __fastcall CBKeyPress(TObject *Sender, char &Key);
        void __fastcall CBChange(TObject *Sender);
	
public:
	bool Connected;
	int Timestamp;
	int Xcount;
	AnsiString __fastcall ErrorCodeToString(int Code, bool PopUpMessage);

        __fastcall TfrmMain(TComponent* Owner);
};


extern PACKAGE TfrmMain *frmMain;

//-- end unit ----------------------------------------------------------------
#endif	// DemoRemoteControl
