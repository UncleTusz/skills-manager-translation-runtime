param([Parameter(Mandatory=$true)][string]$Python, [Parameter(Mandatory=$true)][string]$Downloads)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (Test-Path -LiteralPath 'dist/1.0.1-r2') { throw 'Immutable build output exists; use a fresh build checkout' }
& $Python patch_argos.py
if ($LASTEXITCODE) { throw 'Argos patch failed' }
& $Python prepare_payload.py $Downloads
if ($LASTEXITCODE) { throw 'Model preparation failed' }
& $Python -m unittest test_worker test_splitter
if ($LASTEXITCODE) { throw 'Protocol tests failed' }
& $Python -m PyInstaller --clean --onedir --console --name translation-worker --distpath dist/1.0.1-r2 --workpath build/1.0.1-r2 --specpath build --exclude-module torch --exclude-module stanza --exclude-module spacy --exclude-module minisbd --exclude-module onnxruntime --collect-all argostranslate --collect-all pysbd --collect-all ctranslate2 --collect-all sentencepiece --copy-metadata pysbd worker.py
if ($LASTEXITCODE) { throw 'Worker build failed' }
Copy-Item -LiteralPath payload-1.0.1/models -Destination dist/1.0.1-r2/translation-worker/models -Recurse
& $Python prepare_notices.py
if ($LASTEXITCODE) { throw 'License input verification failed' }
& $Python test_native_worker.py
if ($LASTEXITCODE) { throw 'Real Worker tests failed; no release package created' }
& $Python package_release.py
if ($LASTEXITCODE) { throw 'Release packaging failed' }
