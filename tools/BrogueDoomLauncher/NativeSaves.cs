using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;

namespace BrogueDoomLauncher;

internal sealed record LaunchSelection(ulong? Seed, string? SavePath);

internal static class NativeSaves
{
    internal const uint BridgeApiVersion = 20;
    internal static string DirectoryPath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "ProjectBroom", "saves");

    [StructLayout(LayoutKind.Sequential)]
    private struct Request
    {
        public uint Version;
        public int Operation;
        public ulong Revision, Session;
        public byte Consume;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 4096)] public byte[] Path;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct State
    {
        public uint Version;
        public int ErrorCode, Phase;
        public ulong Session, Revision, Seed, Turns, Total;
        public int Mode;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)] public byte[] NativeVersion;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 256)] public byte[] Error;
    }

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    private delegate int Persistence(ref Request request, out State state);

    internal static ulong Probe(string path)
    {
        string dll;
        string manifest = Path.Combine(AppContext.BaseDirectory, "release-manifest.json");
        if (File.Exists(manifest))
        {
            using JsonDocument json = JsonDocument.Parse(File.ReadAllText(manifest));
            string engine = json.RootElement.GetProperty("paths").GetProperty("engine").GetString()!;
            dll = Path.Combine(AppContext.BaseDirectory, Path.GetDirectoryName(engine)!, "brogue-bridge.dll");
        }
        else
        {
            DirectoryInfo? root = new(AppContext.BaseDirectory);
            while (root != null && !File.Exists(Path.Combine(root.FullName, "scripts", "launch-source-bridge.ps1"))) root = root.Parent;
            if (root == null) throw new FileNotFoundException("Project Broom source folder was not found.");
            dll = Path.Combine(root.FullName, "src", "brogue-mapgen", "bin", "brogue-bridge.dll");
        }
        IntPtr module = NativeLibrary.Load(dll);
        try
        {
            var call = Marshal.GetDelegateForFunctionPointer<Persistence>(NativeLibrary.GetExport(module, "brogue_bridge_persistence"));
            var request = new Request { Version = BridgeApiVersion, Operation = 1, Path = new byte[4096] };
            byte[] encoded = Encoding.UTF8.GetBytes(Path.GetFullPath(path));
            if (encoded.Length >= request.Path.Length) throw new IOException("The save path is too long.");
            encoded.CopyTo(request.Path, 0);
            if (call(ref request, out State state) != 0)
                throw new InvalidDataException(Encoding.UTF8.GetString(state.Error).TrimEnd('\0'));
            return state.Seed;
        }
        finally { NativeLibrary.Free(module); }
    }

    internal static LaunchSelection FromFile(string path)
    {
        ulong seed = Probe(path);
        Directory.CreateDirectory(DirectoryPath);
        string fullPath = Path.GetFullPath(path);
        if (!string.Equals(Path.GetDirectoryName(fullPath), Path.GetFullPath(DirectoryPath), StringComparison.OrdinalIgnoreCase))
        {
            string copy = Path.Combine(DirectoryPath, $"import-{Guid.NewGuid():N}.broguesave");
            File.Copy(fullPath, copy);
            File.SetAttributes(copy, File.GetAttributes(copy) & ~FileAttributes.ReadOnly);
            fullPath = copy;
        }
        return new(seed, fullPath);
    }

    internal static LaunchSelection? Choose()
    {
        using var window = new Form {
            Text = "Project Broom", ClientSize = new Size(480, 286),
            StartPosition = FormStartPosition.CenterScreen, FormBorderStyle = FormBorderStyle.FixedDialog,
            MaximizeBox = false, MinimizeBox = false, BackColor = Color.Black, ForeColor = Color.Gold
        };
        var title = new Label { Text = "PROJECT BROOM", Dock = DockStyle.Top, Height = 70,
            TextAlign = ContentAlignment.MiddleCenter, Font = new Font(FontFamily.GenericMonospace, 22) };
        window.Controls.Add(title);
        var panel = new FlowLayoutPanel { Dock = DockStyle.Bottom, Height = 196, FlowDirection = FlowDirection.TopDown,
            WrapContents = false, Padding = new Padding(110, 0, 0, 0) };
        window.Controls.Add(panel);
        LaunchSelection? selection = null;
        void Add(string text, Action action, bool enabled = true)
        {
            var button = new Button { Text = text, Width = 260, Height = 36, Enabled = enabled,
                BackColor = Color.FromArgb(35, 35, 35), ForeColor = Color.Gold };
            button.Click += (_, _) => { try { action(); if (selection != null) window.Close(); }
                catch (Exception error) { MessageBox.Show(window, error.Message, "Cannot load save", MessageBoxButtons.OK, MessageBoxIcon.Error); } };
            panel.Controls.Add(button);
        }
        string? latest = Directory.Exists(DirectoryPath)
            ? Directory.EnumerateFiles(DirectoryPath, "*.broguesave").OrderByDescending(File.GetLastWriteTimeUtc).FirstOrDefault() : null;
        Add("Continue", () => selection = FromFile(latest!), latest != null);
        Add("Load / Import", () => {
            using var dialog = new OpenFileDialog { Filter = "Brogue saves|*.broguesave", InitialDirectory = DirectoryPath };
            if (dialog.ShowDialog(window) == DialogResult.OK) selection = FromFile(dialog.FileName);
        });
        Add("New Game", () => selection = new(null, null));
        Add("New Game with Seed", () => {
            ulong? seed = PromptForSeed(window);
            if (seed.HasValue) selection = new(seed, null);
        });
        window.ShowDialog();
        return selection;
    }

    private static ulong? PromptForSeed(IWin32Window owner)
    {
        using var dialog = new Form {
            Text = "Launch a Seed", ClientSize = new Size(420, 176),
            StartPosition = FormStartPosition.CenterParent, FormBorderStyle = FormBorderStyle.FixedDialog,
            MaximizeBox = false, MinimizeBox = false, ShowInTaskbar = false,
            BackColor = Color.Black, ForeColor = Color.Gold
        };
        var prompt = new Label {
            Text = "Enter a positive Brogue seed:", Left = 28, Top = 24, Width = 364, Height = 24,
            Font = new Font(FontFamily.GenericMonospace, 10), TextAlign = ContentAlignment.MiddleLeft
        };
        var seedBox = new TextBox {
            Left = 28, Top = 56, Width = 364, Height = 28,
            Font = new Font(FontFamily.GenericMonospace, 10), MaxLength = 20
        };
        var launch = new Button {
            Text = "Launch", Left = 206, Top = 112, Width = 88, Height = 32,
            BackColor = Color.FromArgb(35, 35, 35), ForeColor = Color.Gold
        };
        var cancel = new Button {
            Text = "Cancel", Left = 304, Top = 112, Width = 88, Height = 32,
            BackColor = Color.FromArgb(35, 35, 35), ForeColor = Color.Gold,
            DialogResult = DialogResult.Cancel
        };
        ulong? result = null;
        launch.Click += (_, _) => {
            if (!ulong.TryParse(seedBox.Text.Trim(), out ulong seed) || seed == 0)
            {
                MessageBox.Show(dialog, "Enter a whole number from 1 to 18,446,744,073,709,551,615.",
                    "Invalid seed", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                seedBox.SelectAll();
                seedBox.Focus();
                return;
            }
            result = seed;
            dialog.DialogResult = DialogResult.OK;
        };
        dialog.AcceptButton = launch;
        dialog.CancelButton = cancel;
        dialog.Controls.AddRange(new Control[] { prompt, seedBox, launch, cancel });
        dialog.Shown += (_, _) => seedBox.Focus();
        return dialog.ShowDialog(owner) == DialogResult.OK ? result : null;
    }
}
