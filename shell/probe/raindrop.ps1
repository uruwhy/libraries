[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Execute {
    Param([String]$File)

    $stderrFile = "stderr.txt"

    try {
        # Start the process, redirect stderr to the file
        $process = Start-Process -FilePath $File -NoNewWindow -PassThru -RedirectStandardError $stderrFile
        $handle = $process.Handle
        $process.WaitForExit()
        $exitCode = $process.ExitCode

        if (Test-Path $File) {
            return $exitCode
        } else {
            return 127
        }
    } catch [System.UnauthorizedAccessException] {
        return 126
    } catch [System.InvalidOperationException] {
        return 127
    } catch {
        return 1
    }
}

function FromEnv { param([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Machine")
    if ($envVal) { return $envVal } else { return $default }
}

$ca = FromEnv "PRELUDE_CA" "prelude-account-us1-us-east-2.s3.amazonaws.com"
$dir = FromEnv "PRELUDE_DIR" $ca
$dat = ""

while ($true) {
    try {

        if ($uuid -and $auth -eq $ca) {
            Invoke-WebRequest -Uri $task.content -OutFile (New-Item -path "$dir\$uuid.exe" -Force ) -UseBasicParsing
            $code = Execute "$dir\$uuid.exe"

            # Read and parse the stderr content
            $stderrContent = Get-Content stderr.txt
            if ($stderrContent -match 'line:\s*(\d+)') {
                $line = $matches[1]
            } else {
                $line = "Unknown"
            }

            $dat = "${uuid}:${code}:${line}"
        } elseif ($task -eq "stop") {
            exit
        } else {
            throw "Test cycle done"
        }
    } catch {
        Write-Output $_.Exception
        Remove-Item $dir -Force -Recurse -ErrorAction SilentlyContinue
        $dat = ""
        Start-Sleep -Seconds 3600
    }
}
