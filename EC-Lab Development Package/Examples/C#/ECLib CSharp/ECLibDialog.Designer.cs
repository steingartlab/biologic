namespace ECLibSharpExample
{
    partial class ECLibDialog
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            wait_threads();
            if (conn_id != -1)
                ECLib.BL_Disconnect(conn_id);
            conn_id = -1;

            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.connection_group = new System.Windows.Forms.GroupBox();
            this.reload_fw_check = new System.Windows.Forms.CheckBox();
            this.connect_radio = new System.Windows.Forms.RadioButton();
            this.information_btn = new System.Windows.Forms.Button();
            this.disconnect_btn = new System.Windows.Forms.Button();
            this.connect_btn = new System.Windows.Forms.Button();
            this.ip_label = new System.Windows.Forms.Label();
            this.ip_textbox = new System.Windows.Forms.TextBox();
            this.techniques_group = new System.Windows.Forms.GroupBox();
            this.show_params = new System.Windows.Forms.CheckBox();
            this.ack_state_radio = new System.Windows.Forms.RadioButton();
            this.ack_stop_btn = new System.Windows.Forms.Button();
            this.ack_start_btn = new System.Windows.Forms.Button();
            this.channel_values_btn = new System.Windows.Forms.Button();
            this.channel_info_btn = new System.Windows.Forms.Button();
            this.technique_combo = new System.Windows.Forms.ComboBox();
            this.channel_combo = new System.Windows.Forms.ComboBox();
            this.technique_label = new System.Windows.Forms.Label();
            this.channel_label = new System.Windows.Forms.Label();
            this.data_group = new System.Windows.Forms.GroupBox();
            this.log_box = new System.Windows.Forms.RichTextBox();
            this.data_grid = new System.Windows.Forms.DataGridView();
            this.copy_btn = new System.Windows.Forms.Button();
            this.quit_btn = new System.Windows.Forms.Button();
            this.points_count_label = new System.Windows.Forms.Label();
            this.points_label = new System.Windows.Forms.Label();
            this.msg_worker = new System.ComponentModel.BackgroundWorker();
            this.data_worker = new System.ComponentModel.BackgroundWorker();
            this.connection_group.SuspendLayout();
            this.techniques_group.SuspendLayout();
            this.data_group.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.data_grid)).BeginInit();
            this.SuspendLayout();
            // 
            // connection_group
            // 
            this.connection_group.Controls.Add(this.reload_fw_check);
            this.connection_group.Controls.Add(this.connect_radio);
            this.connection_group.Controls.Add(this.information_btn);
            this.connection_group.Controls.Add(this.disconnect_btn);
            this.connection_group.Controls.Add(this.connect_btn);
            this.connection_group.Controls.Add(this.ip_label);
            this.connection_group.Controls.Add(this.ip_textbox);
            this.connection_group.Location = new System.Drawing.Point(12, 12);
            this.connection_group.Name = "connection_group";
            this.connection_group.Size = new System.Drawing.Size(533, 130);
            this.connection_group.TabIndex = 0;
            this.connection_group.TabStop = false;
            this.connection_group.Text = "Connection";
            // 
            // reload_fw_check
            // 
            this.reload_fw_check.AutoSize = true;
            this.reload_fw_check.Location = new System.Drawing.Point(250, 24);
            this.reload_fw_check.Name = "reload_fw_check";
            this.reload_fw_check.Size = new System.Drawing.Size(105, 17);
            this.reload_fw_check.TabIndex = 6;
            this.reload_fw_check.Text = "Reload Firmware";
            this.reload_fw_check.UseVisualStyleBackColor = true;
            // 
            // connect_radio
            // 
            this.connect_radio.AutoCheck = false;
            this.connect_radio.AutoSize = true;
            this.connect_radio.Location = new System.Drawing.Point(139, 81);
            this.connect_radio.Name = "connect_radio";
            this.connect_radio.Size = new System.Drawing.Size(91, 17);
            this.connect_radio.TabIndex = 5;
            this.connect_radio.Text = "Disconnected";
            this.connect_radio.UseVisualStyleBackColor = true;
            // 
            // information_btn
            // 
            this.information_btn.Enabled = false;
            this.information_btn.Location = new System.Drawing.Point(28, 78);
            this.information_btn.Name = "information_btn";
            this.information_btn.Size = new System.Drawing.Size(75, 23);
            this.information_btn.TabIndex = 4;
            this.information_btn.Text = "Information";
            this.information_btn.UseVisualStyleBackColor = true;
            this.information_btn.Click += new System.EventHandler(this.information_Click);
            // 
            // disconnect_btn
            // 
            this.disconnect_btn.Enabled = false;
            this.disconnect_btn.Location = new System.Drawing.Point(28, 49);
            this.disconnect_btn.Name = "disconnect_btn";
            this.disconnect_btn.Size = new System.Drawing.Size(75, 23);
            this.disconnect_btn.TabIndex = 3;
            this.disconnect_btn.Text = "Disconnect";
            this.disconnect_btn.UseVisualStyleBackColor = true;
            this.disconnect_btn.Click += new System.EventHandler(this.disconnect_Click);
            // 
            // connect_btn
            // 
            this.connect_btn.Location = new System.Drawing.Point(28, 20);
            this.connect_btn.Name = "connect_btn";
            this.connect_btn.Size = new System.Drawing.Size(75, 23);
            this.connect_btn.TabIndex = 2;
            this.connect_btn.Text = "Connect";
            this.connect_btn.UseVisualStyleBackColor = true;
            this.connect_btn.Click += new System.EventHandler(this.connect_Click);
            // 
            // ip_label
            // 
            this.ip_label.AutoSize = true;
            this.ip_label.Location = new System.Drawing.Point(118, 25);
            this.ip_label.Name = "ip_label";
            this.ip_label.Size = new System.Drawing.Size(20, 13);
            this.ip_label.TabIndex = 1;
            this.ip_label.Text = "IP:";
            // 
            // ip_textbox
            // 
            this.ip_textbox.Location = new System.Drawing.Point(144, 22);
            this.ip_textbox.Name = "ip_textbox";
            this.ip_textbox.Size = new System.Drawing.Size(100, 20);
            this.ip_textbox.TabIndex = 0;
            this.ip_textbox.Text = "192.109.209.138";
            // 
            // techniques_group
            // 
            this.techniques_group.Controls.Add(this.show_params);
            this.techniques_group.Controls.Add(this.ack_state_radio);
            this.techniques_group.Controls.Add(this.ack_stop_btn);
            this.techniques_group.Controls.Add(this.ack_start_btn);
            this.techniques_group.Controls.Add(this.channel_values_btn);
            this.techniques_group.Controls.Add(this.channel_info_btn);
            this.techniques_group.Controls.Add(this.technique_combo);
            this.techniques_group.Controls.Add(this.channel_combo);
            this.techniques_group.Controls.Add(this.technique_label);
            this.techniques_group.Controls.Add(this.channel_label);
            this.techniques_group.Location = new System.Drawing.Point(12, 148);
            this.techniques_group.Name = "techniques_group";
            this.techniques_group.Size = new System.Drawing.Size(533, 125);
            this.techniques_group.TabIndex = 1;
            this.techniques_group.TabStop = false;
            this.techniques_group.Text = "Techniques";
            // 
            // show_params
            // 
            this.show_params.AutoSize = true;
            this.show_params.Location = new System.Drawing.Point(288, 99);
            this.show_params.Name = "show_params";
            this.show_params.Size = new System.Drawing.Size(108, 17);
            this.show_params.TabIndex = 9;
            this.show_params.Text = "Show parameters";
            this.show_params.UseVisualStyleBackColor = true;
            // 
            // ack_state_radio
            // 
            this.ack_state_radio.AutoCheck = false;
            this.ack_state_radio.AutoSize = true;
            this.ack_state_radio.Location = new System.Drawing.Point(28, 99);
            this.ack_state_radio.Name = "ack_state_radio";
            this.ack_state_radio.Size = new System.Drawing.Size(65, 17);
            this.ack_state_radio.TabIndex = 7;
            this.ack_state_radio.TabStop = true;
            this.ack_state_radio.Text = "Stopped";
            this.ack_state_radio.UseVisualStyleBackColor = true;
            // 
            // ack_stop_btn
            // 
            this.ack_stop_btn.Enabled = false;
            this.ack_stop_btn.Location = new System.Drawing.Point(206, 96);
            this.ack_stop_btn.Name = "ack_stop_btn";
            this.ack_stop_btn.Size = new System.Drawing.Size(75, 23);
            this.ack_stop_btn.TabIndex = 8;
            this.ack_stop_btn.Text = "Stop";
            this.ack_stop_btn.UseVisualStyleBackColor = true;
            this.ack_stop_btn.Click += new System.EventHandler(this.stop_btn_Click);
            // 
            // ack_start_btn
            // 
            this.ack_start_btn.Location = new System.Drawing.Point(125, 96);
            this.ack_start_btn.Name = "ack_start_btn";
            this.ack_start_btn.Size = new System.Drawing.Size(75, 23);
            this.ack_start_btn.TabIndex = 7;
            this.ack_start_btn.Text = "Start";
            this.ack_start_btn.UseVisualStyleBackColor = true;
            this.ack_start_btn.Click += new System.EventHandler(this.start_btn_Click);
            // 
            // channel_values_btn
            // 
            this.channel_values_btn.Enabled = false;
            this.channel_values_btn.Location = new System.Drawing.Point(398, 24);
            this.channel_values_btn.Name = "channel_values_btn";
            this.channel_values_btn.Size = new System.Drawing.Size(129, 23);
            this.channel_values_btn.TabIndex = 7;
            this.channel_values_btn.Text = "Current Values";
            this.channel_values_btn.UseVisualStyleBackColor = true;
            this.channel_values_btn.Click += new System.EventHandler(this.channel_values_Click);
            // 
            // channel_info_btn
            // 
            this.channel_info_btn.Enabled = false;
            this.channel_info_btn.Location = new System.Drawing.Point(317, 24);
            this.channel_info_btn.Name = "channel_info_btn";
            this.channel_info_btn.Size = new System.Drawing.Size(75, 23);
            this.channel_info_btn.TabIndex = 6;
            this.channel_info_btn.Text = "Info";
            this.channel_info_btn.UseVisualStyleBackColor = true;
            this.channel_info_btn.Click += new System.EventHandler(this.channel_info_Click);
            // 
            // technique_combo
            // 
            this.technique_combo.DisplayMember = "OCV";
            this.technique_combo.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.technique_combo.FormattingEnabled = true;
            this.technique_combo.Items.AddRange(new object[] {
            "OCV",
            "ChronoAmperometry",
            "ChronoPotentiometry"});
            this.technique_combo.Location = new System.Drawing.Point(109, 57);
            this.technique_combo.Name = "technique_combo";
            this.technique_combo.Size = new System.Drawing.Size(418, 21);
            this.technique_combo.TabIndex = 5;
            // 
            // channel_combo
            // 
            this.channel_combo.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.channel_combo.FormattingEnabled = true;
            this.channel_combo.Location = new System.Drawing.Point(109, 26);
            this.channel_combo.Name = "channel_combo";
            this.channel_combo.Size = new System.Drawing.Size(121, 21);
            this.channel_combo.TabIndex = 4;
            this.channel_combo.SelectedValueChanged += new System.EventHandler(this.channel_combo_selection_changed);
            // 
            // technique_label
            // 
            this.technique_label.AutoSize = true;
            this.technique_label.Location = new System.Drawing.Point(25, 60);
            this.technique_label.Name = "technique_label";
            this.technique_label.Size = new System.Drawing.Size(58, 13);
            this.technique_label.TabIndex = 3;
            this.technique_label.Text = "Technique";
            // 
            // channel_label
            // 
            this.channel_label.AutoSize = true;
            this.channel_label.Location = new System.Drawing.Point(25, 29);
            this.channel_label.Name = "channel_label";
            this.channel_label.Size = new System.Drawing.Size(46, 13);
            this.channel_label.TabIndex = 2;
            this.channel_label.Text = "Channel";
            // 
            // data_group
            // 
            this.data_group.Controls.Add(this.log_box);
            this.data_group.Controls.Add(this.data_grid);
            this.data_group.Controls.Add(this.copy_btn);
            this.data_group.Controls.Add(this.quit_btn);
            this.data_group.Controls.Add(this.points_count_label);
            this.data_group.Controls.Add(this.points_label);
            this.data_group.Location = new System.Drawing.Point(12, 279);
            this.data_group.Name = "data_group";
            this.data_group.Size = new System.Drawing.Size(533, 341);
            this.data_group.TabIndex = 1;
            this.data_group.TabStop = false;
            this.data_group.Text = "Data";
            // 
            // log_box
            // 
            this.log_box.Location = new System.Drawing.Point(7, 214);
            this.log_box.Name = "log_box";
            this.log_box.Size = new System.Drawing.Size(520, 95);
            this.log_box.TabIndex = 7;
            this.log_box.Text = "";
            // 
            // data_grid
            // 
            this.data_grid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.data_grid.Location = new System.Drawing.Point(7, 20);
            this.data_grid.Name = "data_grid";
            this.data_grid.Size = new System.Drawing.Size(520, 187);
            this.data_grid.TabIndex = 6;
            // 
            // copy_btn
            // 
            this.copy_btn.Location = new System.Drawing.Point(144, 315);
            this.copy_btn.Name = "copy_btn";
            this.copy_btn.Size = new System.Drawing.Size(75, 23);
            this.copy_btn.TabIndex = 5;
            this.copy_btn.Text = "Copy";
            this.copy_btn.UseVisualStyleBackColor = true;
            this.copy_btn.Click += new System.EventHandler(this.copy_btn_Click);
            // 
            // quit_btn
            // 
            this.quit_btn.Location = new System.Drawing.Point(452, 315);
            this.quit_btn.Name = "quit_btn";
            this.quit_btn.Size = new System.Drawing.Size(75, 23);
            this.quit_btn.TabIndex = 4;
            this.quit_btn.Text = "Quit";
            this.quit_btn.UseVisualStyleBackColor = true;
            this.quit_btn.Click += new System.EventHandler(this.quit_Click);
            // 
            // points_count_label
            // 
            this.points_count_label.AutoSize = true;
            this.points_count_label.Location = new System.Drawing.Point(71, 320);
            this.points_count_label.Name = "points_count_label";
            this.points_count_label.Size = new System.Drawing.Size(13, 13);
            this.points_count_label.TabIndex = 3;
            this.points_count_label.Text = "0";
            // 
            // points_label
            // 
            this.points_label.AutoSize = true;
            this.points_label.Location = new System.Drawing.Point(25, 320);
            this.points_label.Name = "points_label";
            this.points_label.Size = new System.Drawing.Size(39, 13);
            this.points_label.TabIndex = 2;
            this.points_label.Text = "Points:";
            // 
            // msg_worker
            // 
            this.msg_worker.WorkerReportsProgress = true;
            this.msg_worker.WorkerSupportsCancellation = true;
            // 
            // data_worker
            // 
            this.data_worker.WorkerReportsProgress = true;
            this.data_worker.WorkerSupportsCancellation = true;
            // 
            // ECLibDialog
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(557, 632);
            this.Controls.Add(this.techniques_group);
            this.Controls.Add(this.data_group);
            this.Controls.Add(this.connection_group);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.Name = "ECLibDialog";
            this.Text = "C# ECLib Example";
            this.connection_group.ResumeLayout(false);
            this.connection_group.PerformLayout();
            this.techniques_group.ResumeLayout(false);
            this.techniques_group.PerformLayout();
            this.data_group.ResumeLayout(false);
            this.data_group.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.data_grid)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.GroupBox connection_group;
        private System.Windows.Forms.GroupBox techniques_group;
        private System.Windows.Forms.GroupBox data_group;
        
        private System.Windows.Forms.Label ip_label;
        private System.Windows.Forms.Label technique_label;
        private System.Windows.Forms.Label channel_label;
        private System.Windows.Forms.Label points_label;
        private System.Windows.Forms.Label points_count_label; 
        
        private System.Windows.Forms.TextBox ip_textbox;
        
        private System.Windows.Forms.Button information_btn;
        private System.Windows.Forms.Button disconnect_btn;
        private System.Windows.Forms.Button connect_btn;
        private System.Windows.Forms.Button quit_btn;
        private System.Windows.Forms.Button copy_btn;
        private System.Windows.Forms.Button ack_stop_btn;
        private System.Windows.Forms.Button ack_start_btn;
        private System.Windows.Forms.Button channel_values_btn;
        private System.Windows.Forms.Button channel_info_btn;

        private System.Windows.Forms.ComboBox technique_combo;
        private System.Windows.Forms.ComboBox channel_combo;

        private System.Windows.Forms.DataGridView data_grid;
        
        private System.Windows.Forms.CheckBox reload_fw_check;
        
        private System.Windows.Forms.RadioButton connect_radio;
        private System.Windows.Forms.RadioButton ack_state_radio;
        
        private System.Windows.Forms.RichTextBox log_box;
        private System.ComponentModel.BackgroundWorker msg_worker;
        private System.ComponentModel.BackgroundWorker data_worker;
        private System.Windows.Forms.CheckBox show_params;
    }
}

