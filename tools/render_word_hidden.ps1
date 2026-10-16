param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$resolvedInput = (Resolve-Path -LiteralPath $InputDocx).Path
$resolvedOutput = [IO.Path]::GetFullPath($OutputPdf)
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if (-not $resolvedOutput.StartsWith($workspaceRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Output must be inside this repository.' }
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($resolvedOutput)) | Out-Null
$word = $null
$document = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  $word.AutomationSecurity = 3
  $document = $word.Documents.Open($resolvedInput, $false, $true, $false)
  $document.Repaginate()
  $pages = $document.ComputeStatistics(2)
  $document.ExportAsFixedFormat($resolvedOutput,17)
  Write-Output ("PDF exported with Word: {0} pages; {1}" -f $pages,$resolvedOutput)
} finally {
  if ($null -ne $document) { $document.Close(0); [Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null }
  if ($null -ne $word) { $word.Quit(0); [Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null }
}
