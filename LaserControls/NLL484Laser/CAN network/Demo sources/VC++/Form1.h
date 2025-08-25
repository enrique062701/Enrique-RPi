#pragma once

#include "pl20100.h"

namespace PL20100 {

	using namespace System;
	using namespace System::ComponentModel;
	using namespace System::Collections;
	using namespace System::Windows::Forms;
	using namespace System::Data;
	using namespace System::Drawing;

	/// <summary>
	/// Summary for Form1
	/// </summary>
	public ref class Form1 : public System::Windows::Forms::Form
	{
	public:
		Form1(void)
		{
			InitializeComponent();
			//
			//TODO: Add the constructor code here
			//
		}

	protected:
		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		~Form1()
		{
			if (components)
			{
				delete components;
			}
		}
	private: System::Windows::Forms::Button^  button1;
	protected: 
	private: System::Windows::Forms::Button^  button2;
	private: System::Windows::Forms::NumericUpDown^  numericUpDown1;
	private: System::Windows::Forms::NumericUpDown^  numericUpDown2;
	private: System::Windows::Forms::Label^  label1;
	private: System::Windows::Forms::Label^  label2;
	private: System::Windows::Forms::Label^  label3;
	private: System::Windows::Forms::Label^  label4;

	private:
		/// <summary>
		/// Required designer variable.
		/// </summary>
		System::ComponentModel::Container ^components;

#pragma region Windows Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		void InitializeComponent(void)
		{
			this->button1 = (gcnew System::Windows::Forms::Button());
			this->button2 = (gcnew System::Windows::Forms::Button());
			this->numericUpDown1 = (gcnew System::Windows::Forms::NumericUpDown());
			this->numericUpDown2 = (gcnew System::Windows::Forms::NumericUpDown());
			this->label1 = (gcnew System::Windows::Forms::Label());
			this->label2 = (gcnew System::Windows::Forms::Label());
			this->label3 = (gcnew System::Windows::Forms::Label());
			this->label4 = (gcnew System::Windows::Forms::Label());
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^  >(this->numericUpDown1))->BeginInit();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^  >(this->numericUpDown2))->BeginInit();
			this->SuspendLayout();
			// 
			// button1
			// 
			this->button1->Location = System::Drawing::Point(80, 49);
			this->button1->Name = L"button1";
			this->button1->Size = System::Drawing::Size(75, 23);
			this->button1->TabIndex = 0;
			this->button1->Text = L"STOP";
			this->button1->UseVisualStyleBackColor = true;
			this->button1->Click += gcnew System::EventHandler(this, &Form1::button1_Click);
			// 
			// button2
			// 
			this->button2->Location = System::Drawing::Point(195, 49);
			this->button2->Name = L"button2";
			this->button2->Size = System::Drawing::Size(75, 23);
			this->button2->TabIndex = 1;
			this->button2->Text = L"RUN";
			this->button2->UseVisualStyleBackColor = true;
			this->button2->Click += gcnew System::EventHandler(this, &Form1::button2_Click);
			// 
			// numericUpDown1
			// 
			this->numericUpDown1->DecimalPlaces = 1;
			this->numericUpDown1->Increment = System::Decimal(gcnew cli::array< System::Int32 >(4) {1, 0, 0, 65536});
			this->numericUpDown1->Location = System::Drawing::Point(216, 125);
			this->numericUpDown1->Name = L"numericUpDown1";
			this->numericUpDown1->Size = System::Drawing::Size(120, 22);
			this->numericUpDown1->TabIndex = 2;
			this->numericUpDown1->Value = System::Decimal(gcnew cli::array< System::Int32 >(4) {500, 0, 0, 65536});
			this->numericUpDown1->ValueChanged += gcnew System::EventHandler(this, &Form1::numericUpDown1_ValueChanged);
			// 
			// numericUpDown2
			// 
			this->numericUpDown2->Location = System::Drawing::Point(216, 179);
			this->numericUpDown2->Maximum = System::Decimal(gcnew cli::array< System::Int32 >(4) {500, 0, 0, 0});
			this->numericUpDown2->Minimum = System::Decimal(gcnew cli::array< System::Int32 >(4) {50, 0, 0, 0});
			this->numericUpDown2->Name = L"numericUpDown2";
			this->numericUpDown2->Size = System::Drawing::Size(120, 22);
			this->numericUpDown2->TabIndex = 3;
			this->numericUpDown2->Value = System::Decimal(gcnew cli::array< System::Int32 >(4) {50, 0, 0, 0});
			this->numericUpDown2->ValueChanged += gcnew System::EventHandler(this, &Form1::numericUpDown2_ValueChanged);
			// 
			// label1
			// 
			this->label1->AutoSize = true;
			this->label1->Location = System::Drawing::Point(48, 131);
			this->label1->Name = L"label1";
			this->label1->Size = System::Drawing::Size(80, 17);
			this->label1->TabIndex = 4;
			this->label1->Text = L"Attenuation";
			// 
			// label2
			// 
			this->label2->AutoSize = true;
			this->label2->Location = System::Drawing::Point(51, 181);
			this->label2->Name = L"label2";
			this->label2->Size = System::Drawing::Size(101, 17);
			this->label2->TabIndex = 5;
			this->label2->Text = L"Repetition rate";
			// 
			// label3
			// 
			this->label3->AutoSize = true;
			this->label3->Location = System::Drawing::Point(354, 179);
			this->label3->Name = L"label3";
			this->label3->Size = System::Drawing::Size(32, 17);
			this->label3->TabIndex = 6;
			this->label3->Text = L"kHz";
			// 
			// label4
			// 
			this->label4->AutoSize = true;
			this->label4->Location = System::Drawing::Point(353, 129);
			this->label4->Name = L"label4";
			this->label4->Size = System::Drawing::Size(20, 17);
			this->label4->TabIndex = 7;
			this->label4->Text = L"%";
			// 
			// Form1
			// 
			this->AutoScaleDimensions = System::Drawing::SizeF(8, 16);
			this->AutoScaleMode = System::Windows::Forms::AutoScaleMode::Font;
			this->ClientSize = System::Drawing::Size(422, 263);
			this->Controls->Add(this->label4);
			this->Controls->Add(this->label3);
			this->Controls->Add(this->label2);
			this->Controls->Add(this->label1);
			this->Controls->Add(this->numericUpDown2);
			this->Controls->Add(this->numericUpDown1);
			this->Controls->Add(this->button2);
			this->Controls->Add(this->button1);
			this->Name = L"Form1";
			this->Text = L"PL20100";
			this->Load += gcnew System::EventHandler(this, &Form1::Form1_Load);
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^  >(this->numericUpDown1))->EndInit();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^  >(this->numericUpDown2))->EndInit();
			this->ResumeLayout(false);
			this->PerformLayout();

		}
#pragma endregion
	private: System::Void Form1_Load(System::Object^  sender, System::EventArgs^  e) {
		Connect();	 
		numericUpDown1->Value = Decimal(attenuation);
		numericUpDown2->Value = Decimal(reprate);
	};
private: System::Void button1_Click(System::Object^  sender, System::EventArgs^  e) {
	    Stop();
	}
private: System::Void button2_Click(System::Object^  sender, System::EventArgs^  e) {
	    Run();
	}
private: System::Void numericUpDown1_ValueChanged(System::Object^  sender, System::EventArgs^  e) {
	    SetAttenuation(Decimal::ToDouble(numericUpDown1->Value));
	}
private: System::Void numericUpDown2_ValueChanged(System::Object^  sender, System::EventArgs^  e) {
		SetRepRate(Decimal::ToDouble(numericUpDown2->Value));
	}
};
}

