using System.Diagnostics;
using System.Drawing;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Windows.Forms;

namespace BrogueDoomLauncher;

internal static class Program
{
    [STAThread]
    private static void Main(string[] args)
    {
        ApplicationConfiguration.Initialize();
        if (args.Any(value => value.Equals("--clear-cache", StringComparison.OrdinalIgnoreCase)))
        {
            ClearCache();
            return;
        }
        if (args.Any(value => value.Equals("--diagnostics", StringComparison.OrdinalIgnoreCase)))
        {
            CreateDiagnosticBundle();
            return;
        }
        Application.Run(new PreparationWindow(ParseSeed(args)));
    }

    private static string DataRoot => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "ProjectBroom");

    private static void ClearCache()
    {
        string cache = Path.Combine(DataRoot, "cache");
        if (Directory.Exists(cache)) Directory.Delete(cache, recursive: true);
        MessageBox.Show("Generated Project Broom campaigns were removed. Settings and logs were preserved.",
            "Project Broom", MessageBoxButtons.OK, MessageBoxIcon.Information);
    }

    private static void CreateDiagnosticBundle()
    {
        string desktop = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
        string output = Path.Combine(desktop, $"ProjectBroom-Diagnostics-{DateTime.Now:yyyyMMdd-HHmmss}.zip");
        using ZipArchive archive = ZipFile.Open(output, ZipArchiveMode.Create);
        foreach (string directoryName in new[] { "logs", "config" })
        {
            string directory = Path.Combine(DataRoot, directoryName);
            if (!Directory.Exists(directory)) continue;
            foreach (string file in Directory.EnumerateFiles(directory, "*", SearchOption.AllDirectories))
            {
                string relative = Path.Combine(directoryName, Path.GetRelativePath(directory, file));
                archive.CreateEntryFromFile(file, relative, CompressionLevel.Optimal);
            }
        }
        ZipArchiveEntry system = archive.CreateEntry("system.txt");
        using (var writer = new StreamWriter(system.Open(), Encoding.UTF8))
        {
            writer.WriteLine($"Project Broom diagnostics created {DateTimeOffset.Now:O}");
            writer.WriteLine($"Windows: {Environment.OSVersion}");
            writer.WriteLine($"64-bit process: {Environment.Is64BitProcess}");
        }
        string releaseManifest = Path.Combine(AppContext.BaseDirectory, "release-manifest.json");
        if (File.Exists(releaseManifest)) archive.CreateEntryFromFile(releaseManifest, "release-manifest.json");
        MessageBox.Show($"Diagnostic bundle created:\n{output}", "Project Broom",
            MessageBoxButtons.OK, MessageBoxIcon.Information);
    }

    private static int? ParseSeed(string[] args)
    {
        for (int index = 0; index < args.Length - 1; index++)
        {
            if (args[index].Equals("--seed", StringComparison.OrdinalIgnoreCase)
                && int.TryParse(args[index + 1], out int seed)
                && seed > 0)
                return seed;
        }
        return null;
    }
}

internal sealed class PreparationWindow : Form
{
    private readonly Label status;
    private readonly Label detail;
    private readonly ProgressBar progress;
    private readonly int? requestedSeed;

    public PreparationWindow(int? requestedSeed)
    {
        this.requestedSeed = requestedSeed;
        Text = "Project Broom";
        ClientSize = new Size(640, 330);
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;
        StartPosition = FormStartPosition.CenterScreen;
        BackColor = Color.Black;
        ForeColor = Color.FromArgb(236, 213, 76);
        UseWaitCursor = true;

        var layout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            BackColor = Color.Black,
            Padding = new Padding(38, 22, 38, 24),
            ColumnCount = 1,
            RowCount = 7
        };
        layout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 34));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 62));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 34));
        layout.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 30));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 52));
        layout.RowStyles.Add(new RowStyle(SizeType.Absolute, 24));

        layout.Controls.Add(new Label
        {
            Text = "BROGUE CE IN 3D",
            Font = new Font(FontFamily.GenericMonospace, 11, FontStyle.Regular),
            ForeColor = Color.FromArgb(214, 204, 187),
            TextAlign = ContentAlignment.MiddleCenter,
            Dock = DockStyle.Fill
        }, 0, 0);
        layout.Controls.Add(new Label
        {
            Text = "PROJECT BROOM",
            Font = new Font(FontFamily.GenericMonospace, 30, FontStyle.Bold),
            ForeColor = Color.FromArgb(238, 209, 76),
            TextAlign = ContentAlignment.MiddleCenter,
            Dock = DockStyle.Fill
        }, 0, 1);
        layout.Controls.Add(new Label
        {
            Text = "PREPARING YOUR DESCENT",
            Font = new Font(FontFamily.GenericMonospace, 10, FontStyle.Regular),
            ForeColor = Color.FromArgb(119, 106, 151),
            TextAlign = ContentAlignment.MiddleCenter,
            Dock = DockStyle.Fill
        }, 0, 2);
        status = new Label
        {
            Text = requestedSeed.HasValue ? "LOCATING DUNGEON" : "CHOOSING A RANDOM SEED",
            Font = new Font(FontFamily.GenericMonospace, 12, FontStyle.Bold),
            ForeColor = Color.FromArgb(238, 209, 76),
            TextAlign = ContentAlignment.BottomCenter,
            Dock = DockStyle.Fill
        };
        layout.Controls.Add(status, 0, 3);
        progress = new ProgressBar
        {
            Dock = DockStyle.Fill,
            Style = ProgressBarStyle.Marquee,
            MarqueeAnimationSpeed = 24
        };
        layout.Controls.Add(progress, 0, 4);
        detail = new Label
        {
            Text = requestedSeed.HasValue
                ? $"Seed {requestedSeed.Value} will be used for both Brogue and the 3D campaign."
                : "Brogue will choose a seed, generate the dungeon, and build its 3D campaign.",
            Font = new Font(FontFamily.GenericMonospace, 9, FontStyle.Regular),
            ForeColor = Color.FromArgb(174, 168, 161),
            TextAlign = ContentAlignment.MiddleCenter,
            Dock = DockStyle.Fill
        };
        layout.Controls.Add(detail, 0, 5);
        layout.Controls.Add(new Label
        {
            Text = "New seeds can take a little longer on their first launch.",
            Font = new Font(FontFamily.GenericMonospace, 8, FontStyle.Regular),
            ForeColor = Color.FromArgb(91, 86, 91),
            TextAlign = ContentAlignment.MiddleCenter,
            Dock = DockStyle.Fill
        }, 0, 6);
        Controls.Add(layout);
        Shown += async (_, _) => await PrepareAndLaunchAsync();
    }

    private async Task PrepareAndLaunchAsync()
    {
        try
        {
            string packagedManifest = Path.Combine(AppContext.BaseDirectory, "release-manifest.json");
            if (File.Exists(packagedManifest))
                await PreparePackagedAsync(packagedManifest);
            else
                await PrepareDevelopmentAsync();
            status.Text = "ENTERING THE DUNGEON";
            detail.Text = "GZDoom is ready.";
            progress.Style = ProgressBarStyle.Continuous;
            progress.Value = 100;
            await Task.Delay(250);
            Close();
        }
        catch (Exception exception)
        {
            status.Text = "Dungeon preparation failed.";
            MessageBox.Show(this, exception.Message, "Project Broom could not start",
                MessageBoxButtons.OK, MessageBoxIcon.Error);
            Close();
        }
    }

    private async Task PrepareDevelopmentAsync()
    {
            string projectRoot = FindProjectRoot();
            string script = Path.Combine(projectRoot, "scripts", "launch-source-bridge.ps1");
            var start = new ProcessStartInfo
            {
                FileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System),
                    "WindowsPowerShell", "v1.0", "powershell.exe"),
                WorkingDirectory = projectRoot,
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true
            };
            start.ArgumentList.Add("-NoProfile");
            start.ArgumentList.Add("-ExecutionPolicy");
            start.ArgumentList.Add("Bypass");
            start.ArgumentList.Add("-File");
            start.ArgumentList.Add(script);
            if (requestedSeed.HasValue)
            {
                start.ArgumentList.Add("-Seed");
                start.ArgumentList.Add(requestedSeed.Value.ToString());
            }
            else
            {
                start.ArgumentList.Add("-RandomSeed");
            }
            start.ArgumentList.Add("-Menu");

            using Process process = Process.Start(start)
                ?? throw new InvalidOperationException("Windows PowerShell could not be started.");
            var output = new StringBuilder();
            Task<string> errorTask = process.StandardError.ReadToEndAsync();
            while (await process.StandardOutput.ReadLineAsync() is { } line)
            {
                output.AppendLine(line);
                UpdateProgress(line);
            }
            await process.WaitForExitAsync();
            string error = await errorTask;
            WriteDiagnosticLog(Path.Combine(projectRoot, "artifacts"), process.ExitCode, output.ToString(), error);
            if (process.ExitCode != 0)
                throw new InvalidOperationException(string.IsNullOrWhiteSpace(error) ? output.ToString() : error);
    }

    private async Task PreparePackagedAsync(string manifestPath)
    {
        string packageRoot = AppContext.BaseDirectory;
        ReleaseManifest manifest = JsonSerializer.Deserialize<ReleaseManifest>(
            await File.ReadAllTextAsync(manifestPath),
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
            ?? throw new InvalidDataException("The release manifest is invalid.");
        if (manifest.SchemaVersion != 1 || !manifest.Platform.Equals("win-x64", StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("This Project Broom package is not compatible with the launcher.");

        string engine = ResolvePackagePath(packageRoot, manifest.Paths.Engine);
        string exporter = ResolvePackagePath(packageRoot, manifest.Paths.Exporter);
        string compiler = ResolvePackagePath(packageRoot, manifest.Paths.Compiler);
        string iwad = ResolvePackagePath(packageRoot, manifest.Paths.Iwad);
        string staticMod = ResolvePackagePath(packageRoot, manifest.Paths.StaticMod);
        foreach (string required in new[] { engine, exporter, compiler, iwad, staticMod })
            if (!File.Exists(required)) throw new FileNotFoundException("A required Project Broom component is missing.", required);

        int seed = requestedSeed ?? RandomNumberGenerator.GetInt32(1, int.MaxValue);
        string dataRoot = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "ProjectBroom");
        string cache = Path.Combine(dataRoot, "cache", $"seed-{seed}");
        string logs = Path.Combine(dataRoot, "logs");
        string config = Path.Combine(dataRoot, "config");
        Directory.CreateDirectory(cache);
        Directory.CreateDirectory(logs);
        Directory.CreateDirectory(config);
        string json = Path.Combine(cache, "brogue-dungeon.json");
        string package = Path.Combine(cache, $"ProjectBroom-seed-{seed}.pk3");

        var combinedLog = new StringBuilder();
        if (!File.Exists(json))
        {
            status.Text = "GENERATING THE DUNGEON";
            detail.Text = $"Seed {seed} - Brogue CE is creating all 40 depths in canonical order.";
            ProcessResult result = await RunCapturedAsync(exporter,
                new[] { "--export-dungeon-json", json, "--seed", seed.ToString(), "--depths", "40" }, packageRoot);
            combinedLog.Append(result.Output).Append(result.Error);
            EnsureSuccess(result, "Brogue dungeon generation");
        }
        else
        {
            status.Text = "DUNGEON FOUND";
            detail.Text = $"Seed {seed} - reusing the authoritative Brogue snapshot.";
        }

        if (!File.Exists(package))
        {
            status.Text = "BUILDING THE 3D CAMPAIGN";
            detail.Text = "Converting Brogue terrain into 40 playable GZDoom maps.";
            ProcessResult result = await RunCapturedAsync(compiler,
                new[] { "compile", "--input", json, "--output", package }, packageRoot);
            combinedLog.Append(result.Output).Append(result.Error);
            EnsureSuccess(result, "3D campaign compilation");
        }
        else
        {
            status.Text = "3D CAMPAIGN FOUND";
            detail.Text = "The matching compiled map package is already available.";
        }

        status.Text = "VERIFYING THE CAMPAIGN";
        detail.Text = "Checking map topology, metadata, stairs, and package integrity.";
        ProcessResult verification = await RunCapturedAsync(compiler,
            new[] { "verify", "--input", json, "--package", package }, packageRoot);
        combinedLog.Append(verification.Output).Append(verification.Error);
        EnsureSuccess(verification, "Campaign verification");

        status.Text = "OPENING PROJECT BROOM";
        detail.Text = $"Seed {seed} - starting the game.";
        var start = new ProcessStartInfo
        {
            FileName = engine,
            WorkingDirectory = Path.GetDirectoryName(engine)!,
            UseShellExecute = false
        };
        foreach (string argument in new[]
        {
            "-width", "1280", "-height", "720", "-nosound",
            "-config", Path.Combine(config, "gzdoom.ini"),
            "-iwad", iwad, "-file", staticMod, package,
            "+set", "brg_seed", seed.ToString(), "+set", "brg_hud_scale", "1",
            "+set", "brg_debug", "false", "+ucm_hide", "true",
            "+ucm_drawmap", "false", "+ucm_mapshowall", "false",
            "+screenblocks", "12", "+menu_main"
        }) start.ArgumentList.Add(argument);
        _ = Process.Start(start) ?? throw new InvalidOperationException("GZDoom could not be started.");
        WriteDiagnosticLog(logs, 0, combinedLog.ToString(), string.Empty);
    }

    private static async Task<ProcessResult> RunCapturedAsync(string fileName, IEnumerable<string> arguments, string workingDirectory)
    {
        var start = new ProcessStartInfo
        {
            FileName = fileName,
            WorkingDirectory = workingDirectory,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };
        foreach (string argument in arguments) start.ArgumentList.Add(argument);
        using Process process = Process.Start(start) ?? throw new InvalidOperationException($"Could not start {fileName}.");
        Task<string> output = process.StandardOutput.ReadToEndAsync();
        Task<string> error = process.StandardError.ReadToEndAsync();
        await process.WaitForExitAsync();
        return new ProcessResult(process.ExitCode, await output, await error);
    }

    private static void EnsureSuccess(ProcessResult result, string operation)
    {
        if (result.ExitCode != 0)
            throw new InvalidOperationException($"{operation} failed.\n{(string.IsNullOrWhiteSpace(result.Error) ? result.Output : result.Error)}");
    }

    private static string ResolvePackagePath(string root, string relative)
    {
        string fullRoot = Path.GetFullPath(root);
        string fullPath = Path.GetFullPath(Path.Combine(fullRoot, relative.Replace('/', Path.DirectorySeparatorChar)));
        if (!fullPath.StartsWith(fullRoot, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("Release manifest path escapes the package root.");
        return fullPath;
    }

    private void UpdateProgress(string line)
    {
        if (line.StartsWith("Generating Brogue dungeon", StringComparison.OrdinalIgnoreCase))
        {
            status.Text = "GENERATING THE DUNGEON";
            detail.Text = ExtractSeedDetail(line, "Brogue CE is creating all 40 depths in canonical order.");
        }
        else if (line.StartsWith("Using cached Brogue", StringComparison.OrdinalIgnoreCase))
        {
            status.Text = "DUNGEON FOUND";
            detail.Text = ExtractSeedDetail(line, "Reusing the matching authoritative Brogue snapshot.");
        }
        else if (line.StartsWith("Compiling", StringComparison.OrdinalIgnoreCase))
        {
            status.Text = "BUILDING THE 3D CAMPAIGN";
            detail.Text = "Converting Brogue terrain into 40 playable GZDoom maps.";
        }
        else if (line.StartsWith("Using cached GZDoom", StringComparison.OrdinalIgnoreCase))
        {
            status.Text = "3D CAMPAIGN FOUND";
            detail.Text = "The matching compiled map package is already available.";
        }
        else if (line.StartsWith("Verifying", StringComparison.OrdinalIgnoreCase))
        {
            status.Text = "VERIFYING THE CAMPAIGN";
            detail.Text = "Checking map topology, metadata, stairs, and package integrity.";
        }
        else if (line.StartsWith("Launching GZDoom", StringComparison.OrdinalIgnoreCase)
                 || line.StartsWith("Project Broom prepared", StringComparison.OrdinalIgnoreCase))
        {
            status.Text = "OPENING PROJECT BROOM";
            detail.Text = ExtractSeedDetail(line, "Starting the game with the prepared seed.");
        }
    }

    private static string ExtractSeedDetail(string line, string suffix)
    {
        const string marker = "seed ";
        int markerIndex = line.IndexOf(marker, StringComparison.OrdinalIgnoreCase);
        if (markerIndex < 0) return suffix;
        int start = markerIndex + marker.Length;
        int end = start;
        while (end < line.Length && char.IsDigit(line[end])) end++;
        return end > start ? $"Seed {line[start..end]} - {suffix}" : suffix;
    }

    private static void WriteDiagnosticLog(string logRoot, int exitCode, string output, string error)
    {
        Directory.CreateDirectory(logRoot);
        File.WriteAllText(Path.Combine(logRoot, "launcher-last.log"),
            $"Project Broom launcher {DateTimeOffset.Now:O}{Environment.NewLine}" +
            $"Exit code: {exitCode}{Environment.NewLine}{Environment.NewLine}" +
            $"STDOUT{Environment.NewLine}{output}{Environment.NewLine}" +
            $"STDERR{Environment.NewLine}{error}");
    }

    private static string FindProjectRoot()
    {
        DirectoryInfo? directory = new(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "scripts", "launch-source-bridge.ps1")))
                return directory.FullName;
            directory = directory.Parent;
        }
        throw new DirectoryNotFoundException(
            "ProjectBroom.exe must remain inside the Project Broom project folder.");
    }
}

internal sealed record ProcessResult(int ExitCode, string Output, string Error);

internal sealed class ReleaseManifest
{
    public int SchemaVersion { get; set; }
    public string Platform { get; set; } = "";
    public ReleasePaths Paths { get; set; } = new();
}

internal sealed class ReleasePaths
{
    public string Engine { get; set; } = "";
    public string Exporter { get; set; } = "";
    public string Compiler { get; set; } = "";
    public string Iwad { get; set; } = "";
    public string StaticMod { get; set; } = "";
}
