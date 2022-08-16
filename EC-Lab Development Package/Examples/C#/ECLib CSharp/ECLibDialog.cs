using System;
using System.ComponentModel;
using System.Reflection;
using System.Windows.Forms;
using System.Runtime.InteropServices;
using System.Threading;

namespace ECLibSharpExample
{
    public partial class ECLibDialog : Form
    {
        // Globals
        private int conn_id = -1;
        private ECLib.DeviceInfo infos;
        private byte selected_channel = 0xff;
        private EventWaitHandle msg_done = new EventWaitHandle(false, EventResetMode.ManualReset);
        private EventWaitHandle data_done = new EventWaitHandle(false, EventResetMode.ManualReset);
        private bool in_acquisition = false;

        private class ECLibThreadWork
        {
            public byte channel { get; set; }
            public int id { get; set; }
        }

        private class ECLibData
        {
            public ECLib.DataInfos Infos { get; set; }
            public ECLib.CurrentValues Curr { get; set; }
            public int[] Buf { get; set; }
        }

        public ECLibDialog()
        {
            InitializeComponent();
            technique_combo.SelectedIndex = 0;
            technique_combo.SelectedIndexChanged += (sender, e) => { setupDataGrid(); };
            log("=== LOG ===");

            // thread configuration, use lambdas where possible
            msg_worker.DoWork              += message_worker_task;
            msg_worker.ProgressChanged     += msg_worker_ProgressChanged;
            msg_worker.RunWorkerCompleted  += worker_completed;

            data_worker.DoWork             += data_worker_task;
            data_worker.ProgressChanged    += data_worker_ProgressChanged;
            data_worker.RunWorkerCompleted += worker_completed;
                       
        }

        private void worker_completed(object sender, RunWorkerCompletedEventArgs e)
        {
            if (e.Cancelled || conn_id == -1)
            {
                // this indicates that we were disconnected. At that time we might 
                // be closing the form (if Quit was pressed), so do nothing.
            }
            else if (conn_id != -1)
            {
                String worker = (sender == msg_worker) ? "Message" : "Data";

                log(worker + " thread finished with status " + e.Result);

                if ((ECLib.ErrorCode)e.Result != ECLib.ErrorCode.ERR_NOERROR)
                {
                    // an error occured
                    String thread_to_stop = (sender != data_worker) ? "data" : "message";
                    String error = "An error occured in the " 
                        + worker 
                        + " thread, abort the " 
                        + thread_to_stop
                        + " thread.\r\nThis could freeze the UI for ~20s.";
                    
                    log(error);
                    MessageBox.Show(error);
                    wait_threads();
                    disconnect_Click(sender, e);
                }
                else
                {
                    stop_btn_Click(sender, e);
                }
            }
        }
                
        private void message_worker_task(object sender, DoWorkEventArgs e)
        {
            ECLib.ErrorCode err = ECLib.ErrorCode.ERR_NOERROR;
            try
            {
                BackgroundWorker bw = sender as BackgroundWorker;
                ECLibThreadWork work = e.Argument as ECLibThreadWork;
                int msg_size = 512;
                byte[] msg = new byte[msg_size];
                while (!bw.CancellationPending)
                {
                    err = ECLib.BL_GetMessage(work.id, work.channel, msg, ref msg_size);
                    if (err == ECLib.ErrorCode.ERR_NOERROR && msg[0] != '\0')
                    {
                        bw.ReportProgress(0, System.Text.Encoding.ASCII.GetString(msg));
                    }
                    else if (err != ECLib.ErrorCode.ERR_NOERROR)
                    {
                        bw.ReportProgress((int)err);
                        break;
                    }
                    msg_size = 512;
                    Thread.Sleep(100);
                }
            }
            finally
            {
                e.Result = err;
                msg_done.Set();
            }
        }

        private void data_worker_task(object sender, DoWorkEventArgs e)
        {
            ECLib.ErrorCode err = ECLib.ErrorCode.ERR_NOERROR;
            try
            {
                BackgroundWorker bw = sender as BackgroundWorker;
                ECLibThreadWork work = e.Argument as ECLibThreadWork;

                bool stop = false;
                ECLib.DataInfos infos = default(ECLib.DataInfos);
                ECLib.CurrentValues curr = default(ECLib.CurrentValues);
                while (!bw.CancellationPending && !stop)
                {
                    int[] buf = new int[1000]; // needed for each iteration
                    err = ECLib.BL_GetData(work.id, work.channel, buf, ref infos, ref curr);
                    if (err == ECLib.ErrorCode.ERR_NOERROR)
                    {
                        if ( infos.NbRows != 0 && infos.NbCols != 0)
                        {
                            bw.ReportProgress(0, new ECLibData { Infos = infos, Curr = curr, Buf = buf });
                        }
                        if (curr.State != ECLib.ChannelState.KBIO_STATE_RUN)
                            stop = true;
                    }
                    else
                    {
                        bw.ReportProgress((int)err);
                        stop = true;
                    }
                }
            }
            finally
            {
                e.Result = err;
                data_done.Set();
            }

        }

        private void msg_worker_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            if (e.UserState != null && !msg_worker.CancellationPending)
            {
                log(e.UserState as string);
            }
        }

        private void data_worker_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            // UserState contains the data retrieved on the network by
            // the Data thread
            if (e.UserState != null && !data_worker.CancellationPending)
            {
                ECLibData data = e.UserState as ECLibData;
                for (int i = 0; i < data.Infos.NbRows; i++)
                {
                    string[] row = new string[0];
                    switch (data.Infos.TechniqueID)
                    {
                        case ECLib.TechniqueIdentifier.KBIO_TECHID_OCV:
                            row = parseOcvData(data, i);
                            break;
                        case ECLib.TechniqueIdentifier.KBIO_TECHID_CA: // both share the same data format
                        case ECLib.TechniqueIdentifier.KBIO_TECHID_CP:
                            row = parseChronoData(data, i);
                            break;
                        default:
                            break;
                    }
                    if (row.Length != 0)
                    {
                        data_grid.Rows.Add(row);
                    }
                }

                // update points count
                points_count_label.Text = data_grid.Rows.Count.ToString();
            }
        }

        private void wait_threads()
        {
            int timeout = 30000;
            Cursor.Current = Cursors.WaitCursor;
            if (data_worker.IsBusy && !data_worker.CancellationPending)
            {
                try
                {
                    data_worker.CancelAsync();
                    data_done.WaitOne(timeout);
                }
                catch (Exception e)
                {
                    log("An exception was raised for data_worker: " + e);
                }

            }
            if (msg_worker.IsBusy && !msg_worker.CancellationPending)
            {
                try
                {
                    msg_worker.CancelAsync();
                    msg_done.WaitOne(timeout);
                }
                catch (Exception e)
                {
                    log("An exception was raised for data_worker: " + e);
                }
            }
            Cursor.Current = Cursors.Default;
        }

        private void log(string s)
        {
            log_box.AppendText(s);
            log_box.AppendText(Environment.NewLine);
            log_box.ScrollToCaret();
        }

        private string struct_dump(object obj, Type type)
        {
            // use C# type reflection ability to browse the structure properties,
            // and dump them into a string that can be displayed
            string dump = "";
            FieldInfo[] fi = type.GetFields(BindingFlags.Public | BindingFlags.Instance);
            
            foreach (FieldInfo info in fi)
                dump += info.Name + ": " + info.GetValue(obj) + "\n";
            
            return dump;
        }

        private void setupDataGrid()
        {
            bool vmp4 = ECLib.is_vmp4(infos.DeviceCode);
            data_grid.Rows.Clear();
            data_grid.Columns.Clear();

            switch (technique_combo.SelectedItem.ToString())
            {
                case "OCV":
                    data_grid.ColumnCount = (vmp4) ? 2 : 3;
                    data_grid.Columns[0].Name = "Time";
                    data_grid.Columns[1].Name = "Ewe";
                    if (!vmp4) // one extra column for vmp3 devices
                        data_grid.Columns[2].Name = "Ece";
                    break;
                default:
                    data_grid.ColumnCount = 4;
                    data_grid.Columns[0].Name = "Time";
                    data_grid.Columns[1].Name = "Ewe";
                    data_grid.Columns[2].Name = "I";
                    data_grid.Columns[3].Name = "cycle";
                    break;
            }
        }
        
        private void setupChannels()
        {
            byte size = 15;
            int[] results = new int[size];
            byte[] channels = new byte[size];

            if (ECLib.BL_GetChannelsPlugged(conn_id, channels, size) == ECLib.ErrorCode.ERR_NOERROR)
            {
                for (byte c = 0; c < size; c++)
                    if (channels[c] != 0)
                    {
                        if (infos.DeviceCode != ECLib.DeviceType.KBIO_DEV_NIKITA)
	                    {
                            channel_combo.Items.Add(c.ToString());
	                    }
                        else 
                        {
                            for (int i = 0; i < 16; i++)
                            {
                                int temp = (c+1);
                                channel_combo.Items.Add(temp.ToString());
                            }
                        }
                       
                        
                    }
                        

                if (channel_combo.Items.Count  > 0)
                {
                    channel_combo.SelectedIndex = 0; // autoselect first channel available
                }
               

                ECLib.ErrorCode status = ECLib.BL_LoadFirmware(conn_id, channels, results, size, true, reload_fw_check.Checked, null, null);
                if( status != ECLib.ErrorCode.ERR_NOERROR)
                {
                    MessageBox.Show("Firmware load failed: " + status);
                }
            }
        }

        private string[] parseOcvData(ECLibData data, int idx)
        {
            bool vmp4 = ECLib.is_vmp4(infos.DeviceCode);
            int base_offset = idx * data.Infos.NbCols;
            string[] row = vmp4 ? new string[2] : new string[3];

            int t_high = data.Buf[base_offset + 0];
            int t_low = data.Buf[base_offset + 1];
            int ewe = data.Buf[base_offset + 2];
            long t_64 = (((long)t_high) << 32) + t_low;

            double time = data.Infos.StartTime + data.Curr.TimeBase * t_64;
            float f_ewe = 0.0f;

            if (ECLib.BL_ConvertNumericIntoSingle(ewe, ref f_ewe) == ECLib.ErrorCode.ERR_NOERROR)
            {
                row[0] = time.ToString("F6");
                row[1] = f_ewe.ToString("F6");
                if (!vmp4)
                {
                    // VMP3 sends an additional row of data
                    int ece = data.Buf[base_offset + 3];
                    float f_ece = 0.0f;
                    if (ECLib.BL_ConvertNumericIntoSingle(ece, ref f_ece) == ECLib.ErrorCode.ERR_NOERROR)
                        row[2] = f_ece.ToString("F6");
                }
            }
            return row;
        }

        private string[] parseChronoData(ECLibData data, int idx)
        {
            bool vmp4 = ECLib.is_vmp4(infos.DeviceCode);
            int base_offset = idx * data.Infos.NbCols;
            string[] row = new string[0];

            int t_high = data.Buf[base_offset + 0];
            int t_low = data.Buf[base_offset + 1];
            int ewe = data.Buf[base_offset + 2];
            int I = data.Buf[base_offset + 3];
            int cycle = data.Buf[base_offset + 4];

            long t_64 = (((long)t_high) << 32) + t_low;
            double time = data.Infos.StartTime + data.Curr.TimeBase * t_64;
            float f_ewe = 0.0f, f_I = 0.0f;

            if (ECLib.BL_ConvertNumericIntoSingle(ewe, ref f_ewe) == ECLib.ErrorCode.ERR_NOERROR
                && ECLib.BL_ConvertNumericIntoSingle(I, ref f_I) == ECLib.ErrorCode.ERR_NOERROR)
            {
                row = new string[4];
                row[0] = time.ToString("F6");
                row[1] = f_ewe.ToString("F6");
                row[2] = f_I.ToString("F6");
                row[3] = cycle.ToString();
            }
            return row;
        }

        private ECLib.ErrorCode setOCVParams(ref ECLib.EccParams parameters, ref string file)
        {
            ECLib.ErrorCode err = ECLib.ErrorCode.ERR_NOERROR;
            int structsize = Marshal.SizeOf(typeof(ECLib.EccParam)); // size of a parameter
            file = ECLib.is_vmp4(infos.DeviceCode) ? "ocv4.ecc" : "ocvN.ecc";

            // allocate N (=4 for OCV) parameters in memory for the unmanaged call. 
            parameters.len = 4;
            parameters.pparams = Marshal.AllocHGlobal(parameters.len * structsize);

            // BL_Define[sgl,bool,int]Parameter all take a pointer to a memory space equivalent to a ECLib.EccParam structure
            err = ECLib.BL_DefineSglParameter("Rest_time_T", 3.0f, 0, parameters.pparams + 0 * structsize);
            err = ECLib.BL_DefineSglParameter("Record_every_dE", 0.1f, 0, parameters.pparams + 1 * structsize);
            err = ECLib.BL_DefineSglParameter("Record_every_dT", 0.01f, 0, parameters.pparams + 2 * structsize);
            err = ECLib.BL_DefineIntParameter("E_Range", (int)ECLib.VoltageRange.KBIO_ERANGE_AUTO, 0, parameters.pparams + 3 * structsize);

            return err;
        }

        private ECLib.ErrorCode setCAParams(ref ECLib.EccParams parameters, ref string file)
        {
            ECLib.ErrorCode err = ECLib.ErrorCode.ERR_NOERROR;
            int structsize = Marshal.SizeOf(typeof(ECLib.EccParam)); // size of a parameter
            file = ECLib.is_vmp4(infos.DeviceCode) ? "ca4.ecc" : "ca.ecc";

            // allocate parameters in memory for the unmanaged call. 
            parameters.len = 16;
            parameters.pparams = Marshal.AllocHGlobal(parameters.len * structsize);

            err |= ECLib.BL_DefineSglParameter ("Voltage_step",      1.5f,      0, parameters.pparams + structsize * 0);    // E0 (V)
            err |= ECLib.BL_DefineBoolParameter("vs_initial", false, 0, parameters.pparams + structsize * 1);    // vs. init
            err |= ECLib.BL_DefineSglParameter ("Duration_step",     0.1f,      0, parameters.pparams + structsize * 2);    // Step duration (s)
            // Step #1
            err |= ECLib.BL_DefineSglParameter ("Voltage_step",      -1.0f,     1, parameters.pparams + structsize * 3); // E1 (V)
            err |= ECLib.BL_DefineBoolParameter("vs_initial", false, 1, parameters.pparams + structsize * 4);    // scan to E1 s. init
            err |= ECLib.BL_DefineSglParameter ("Duration_step",     0.2f,      1, parameters.pparams + structsize * 5);    // Step duration (s)
            // Step #2
            err |= ECLib.BL_DefineSglParameter ("Voltage_step",      2.0f,      2, parameters.pparams + structsize * 6);    // E2 (V)
            err |= ECLib.BL_DefineBoolParameter("vs_initial", false, 2, parameters.pparams + structsize * 7);    // vs. init
            err |= ECLib.BL_DefineSglParameter ("Duration_step",     0.1f,      2, parameters.pparams + structsize * 8);    // Step duration (s)
            // others
            err |= ECLib.BL_DefineIntParameter("Step_number", 2, 0, parameters.pparams + structsize * 9);    // step number
            err |= ECLib.BL_DefineIntParameter("N_Cycles", 0, 0, parameters.pparams + structsize * 10);   // cycle Nc time
            err |= ECLib.BL_DefineSglParameter("Record_every_dI", 0.1f, 0, parameters.pparams + structsize * 11);   // record every dI (A)
            err |= ECLib.BL_DefineSglParameter("Record_every_dT", 0.01f, 0, parameters.pparams + structsize * 12);   // or every dT (s)
            err |= ECLib.BL_DefineIntParameter ("I_Range",           (int)ECLib.IntensityRange.KBIO_IRANGE_AUTO, 0, parameters.pparams + structsize * 13);   // I Range
            err |= ECLib.BL_DefineIntParameter ("E_Range",           (int)ECLib.VoltageRange.KBIO_ERANGE_AUTO, 0, parameters.pparams + structsize * 14);   // E Range
            err |= ECLib.BL_DefineIntParameter("Bandwidth", (int)ECLib.Bandwidth.KBIO_BW_5, 0, parameters.pparams + structsize * 15);   // bandwidth

            return err;
        }

        private ECLib.ErrorCode setCPParams(ref ECLib.EccParams parameters, ref string file)
        {
            ECLib.ErrorCode err = ECLib.ErrorCode.ERR_NOERROR;
            int structsize = Marshal.SizeOf(typeof(ECLib.EccParam)); // size of a parameter
            file = ECLib.is_vmp4(infos.DeviceCode) ? "cp4.ecc" : "cp.ecc";

            // allocate N parameters in memory for the unmanaged call. 
            parameters.len = 16;
            parameters.pparams = Marshal.AllocHGlobal(parameters.len * structsize);

            ECLib.BL_DefineSglParameter ("Current_step",      0.002f,       0, parameters.pparams + structsize * 0);   // {I0 (A)}
            ECLib.BL_DefineBoolParameter("vs_initial",        false,        0, parameters.pparams + structsize * 1);   // {vs. init}
            ECLib.BL_DefineSglParameter ("Duration_step",     0.1f,         0, parameters.pparams + structsize * 2);    //{Step duration (s)}
            //{Step #1}
            ECLib.BL_DefineSglParameter ("Current_step",      -0.001f,      1, parameters.pparams + structsize * 3);   // {I1 (A)}
            ECLib.BL_DefineBoolParameter("vs_initial",        false,        1, parameters.pparams + structsize * 4);  //  {scan to E1 s. init}
            ECLib. BL_DefineSglParameter ("Duration_step",     0.2f,        1, parameters.pparams + structsize * 5);  //  {Step duration (s)
            //{Step #2}
            ECLib.BL_DefineSglParameter ("Current_step",      0.004f,       2, parameters.pparams + structsize * 6);  //  {I2 (A)}
            ECLib.BL_DefineBoolParameter("vs_initial",        false,        2, parameters.pparams + structsize * 7);  //  {vs. init}
            ECLib.BL_DefineSglParameter ("Duration_step",     0.1f,         2, parameters.pparams + structsize * 8);   // {Step duration (s)}
            //{others}
            ECLib.BL_DefineIntParameter ("Step_number",       2,            0, parameters.pparams + structsize * 9);   // {step number}
            ECLib.BL_DefineIntParameter ("N_Cycles",          0,            0, parameters.pparams + structsize * 10);  // {cycle Nc time}
            ECLib.BL_DefineSglParameter ("Record_every_dE",   0.1f,         0, parameters.pparams + structsize * 11); //  {record every dE (V)}
            ECLib.BL_DefineSglParameter ("Record_every_dT",   0.01f,        0, parameters.pparams + structsize * 12); //  {or every dT (s)}
            ECLib.BL_DefineIntParameter ("I_Range",           (int)ECLib.IntensityRange.KBIO_IRANGE_10mA, 0, parameters.pparams + structsize * 13);  // {I Range}
            ECLib.BL_DefineIntParameter ("E_Range",           (int)ECLib.VoltageRange.KBIO_ERANGE_AUTO, 0, parameters.pparams + structsize * 14);   //{E Range}
            ECLib.BL_DefineIntParameter ("Bandwidth",         (int)ECLib.Bandwidth.KBIO_BW_5, 0, parameters.pparams + structsize * 15);   //{bandwidth}

            return err;
        }

        private ECLib.ErrorCode loadTechnique()
        {
            // This function is special: we have to manually marshal the parameters structure, 
            // because C# doesn't know how to correctly do it through automatic marshalling.
            // See ECLib.EccParams definition in ECLib.cs .
            string file = "";
            string tech = technique_combo.SelectedItem.ToString();
            
            ECLib.ErrorCode err = ECLib.ErrorCode.ERR_NOERROR;
            ECLib.EccParams parameters = default(ECLib.EccParams);

            switch (tech)
            {
                case "OCV":                 err = setOCVParams(ref parameters, ref file); break;
                case "ChronoPotentiometry": err = setCPParams (ref parameters, ref file); break;
                case "ChronoAmperometry":   err = setCAParams (ref parameters, ref file); break;
                default: break;
            }

            // call LoadTechnique with the parameters that has been allocated through manual marshalling
            if ( selected_channel != 0xff 
                && parameters.len != 0
                && file.Length != 0 
                && err == ECLib.ErrorCode.ERR_NOERROR)
                err = ECLib.BL_LoadTechnique(conn_id, selected_channel, file, parameters, true, true, show_params.Checked);
            else
                MessageBox.Show("Error setting a parameter: " + err.ToString());

            // need to free the allocated memory
            if (parameters.pparams != null) 
                Marshal.FreeHGlobal(parameters.pparams);

            return err;
        }
      
        // Buttons handling
        private void channel_combo_selection_changed(object sender, EventArgs e)
        {
            bool has_channels = (channel_combo.Items.Count != 0);
            channel_info_btn.Enabled = has_channels; // true or false depdending on the channel count
            channel_values_btn.Enabled = has_channels;
            try {
                selected_channel = (byte)int.Parse(channel_combo.SelectedItem.ToString());
                log("Auto selected channel " + selected_channel); //ok
            } catch {
                selected_channel = 0xFF;
            }
        }

        private void quit_Click(object sender, EventArgs e)
        {
            disconnect_Click(sender, e);

            Close();
        }

        private void connect_Click(object sender, EventArgs e)
        {
            if (ip_textbox.Text.Length == 0) return;

            ECLib.ErrorCode err = ECLib.BL_Connect(ip_textbox.Text, 9, ref conn_id, ref infos);
            if (err == ECLib.ErrorCode.ERR_NOERROR)
            {
                // update the form
                connect_btn.Enabled = false;
                disconnect_btn.Enabled = true;
                information_btn.Enabled = true;
                connect_radio.Checked = true;
                connect_radio.Text = "Connected";
                log("Connected, id = " + conn_id + ".");
                setupChannels();
                setupDataGrid();
                //msg_worker.RunWorkerAsync(new ECLibThreadWork { id = conn_id, channel = selected_channel });
            }
            else
            {
                MessageBox.Show("Couldn't connect to the device at address " + ip_textbox.Text + ": " + err.ToString() );
            }
        }

        private void disconnect_Click(object sender, EventArgs e)
        {
            stop_btn_Click(sender, e);

            ECLib.BL_Disconnect(conn_id);
            conn_id = -1;

            // update the form
            log("Disconnected."); //ok
            connect_btn.Enabled = true;
            disconnect_btn.Enabled = false;
            information_btn.Enabled = false;
            connect_radio.Checked = false;
            connect_radio.Text = "Disconnected";
            channel_combo.Items.Clear();
            data_grid.Rows.Clear();
        }

        private void information_Click(object sender, EventArgs e)
        {
            if (conn_id != -1)
            {
                MessageBox.Show(struct_dump(infos, typeof(ECLib.DeviceInfo)));
            }
        }

        private void channel_info_Click(object sender, EventArgs e)
        {
            ECLib.ChannelInfo ci = default(ECLib.ChannelInfo);
            ECLib.ErrorCode err = ECLib.BL_GetChannelInfos(conn_id, selected_channel, ref ci);
            if (err != ECLib.ErrorCode.ERR_NOERROR)
            {
                MessageBox.Show("Get channel info failed: " + err.ToString());
            }
            else
            {
                MessageBox.Show(struct_dump(ci, typeof(ECLib.ChannelInfo)));

            }
        }

        private void channel_values_Click(object sender, EventArgs e)
        {
            ECLib.CurrentValues cv = default(ECLib.CurrentValues);
            ECLib.ErrorCode err = ECLib.BL_GetCurrentValues(conn_id, selected_channel, ref cv);
            if (err != ECLib.ErrorCode.ERR_NOERROR)
            {
                MessageBox.Show("Get channel info failed: " + err.ToString());
            }
            else
            {
                MessageBox.Show(struct_dump(cv, typeof(ECLib.CurrentValues)));
            }
        }

        private void start_btn_Click(object sender, EventArgs e)
        {
            ECLib.ErrorCode err = loadTechnique();
            if (err != ECLib.ErrorCode.ERR_NOERROR) 
                MessageBox.Show("Error loading technique: " + err.ToString());
            else
            {
                err = ECLib.BL_StartChannel(conn_id, selected_channel);
                if (err == ECLib.ErrorCode.ERR_NOERROR)
                {
                    ack_start_btn.Enabled = false;
                    ack_stop_btn.Enabled = true;
                    ack_state_radio.Checked = true;
                    ack_state_radio.Text = "Started";
                    data_grid.Rows.Clear();

                    // reset finished indicator
                    msg_done.Reset();
                    data_done.Reset();
                    // start threads
                    in_acquisition = true;
                    msg_worker.RunWorkerAsync(new ECLibThreadWork { id = conn_id, channel = selected_channel });
                    data_worker.RunWorkerAsync(new ECLibThreadWork { id = conn_id, channel = selected_channel });
                }
                else
                {
                    MessageBox.Show("Couldn't start acquisition");
                }
            }
        }

        private void stop_btn_Click(object sender, EventArgs e)
        {
            // stop threads
            wait_threads(); 
            
            //if (in_acquisition)
            {
                ECLib.BL_StopChannel(conn_id, selected_channel);
                in_acquisition = false;
            }
            ack_start_btn.Enabled = true;
            ack_stop_btn.Enabled = false;
            ack_state_radio.Checked = false;
            ack_state_radio.Text = "Stopped";

        }

        private void copy_btn_Click(object sender, EventArgs e)
        {
            data_grid.SelectAll();
            Clipboard.SetDataObject(data_grid.GetClipboardContent());
        }
    }
}
