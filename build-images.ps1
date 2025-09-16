# Build Docker images with BuildKit + local cache on G:\ (repo-local)
param(
  [string]$CacheDir = ".buildx-cache"
)

$ErrorActionPreference = "Stop"

# Ensure BuildKit
$env:DOCKER_BUILDKIT = "1"

# Create cache directory if missing
if (!(Test-Path $CacheDir)) { New-Item -ItemType Directory -Path $CacheDir | Out-Null }

function Test-BuildxAvailable {
  $null = & docker buildx version 2>$null
  if ($LASTEXITCODE -eq 0) { return $true } else { return $false }
}

$useBuildx = Test-BuildxAvailable
if ($useBuildx) {
  try {
    # Ensure a buildx builder exists and is used
    $builderName = "brunella"
    $existing = docker buildx ls 2>$null | Select-String $builderName -ErrorAction SilentlyContinue
    if (-not $existing) {
      docker buildx create --name $builderName --use | Out-Null
    } else {
      docker buildx use $builderName | Out-Null
    }
  } catch {
    Write-Warning "Buildx nem elerheto; alap docker build hasznalata."
    $useBuildx = $false
  }
} else {
  Write-Host "Buildx nem talalhato; DOCKER_BUILDKIT kikapcsolasa es alap docker build futtatasa." -ForegroundColor Yellow
  Remove-Item Env:\DOCKER_BUILDKIT -ErrorAction SilentlyContinue
}

try {
  Write-Host "Building backend image..." -ForegroundColor Cyan
  if ($useBuildx) {
    docker buildx build `
      --cache-from type=local,src=$CacheDir `
      --cache-to type=local,dest=$CacheDir,mode=max `
      --load `
      -t brunella-backend `
      -f backend/Dockerfile `
      ./backend
  } else {
    docker build -t brunella-backend -f backend/Dockerfile ./backend
  }

  Write-Host "Building frontend image..." -ForegroundColor Cyan
  # Pass VITE_API_URL to align with compose backend port 8000
  $env:VITE_API_URL = "http://localhost:8000/agent"
  if ($useBuildx) {
    docker buildx build `
      --cache-from type=local,src=$CacheDir `
      --cache-to type=local,dest=$CacheDir,mode=max `
      --build-arg VITE_API_URL=$env:VITE_API_URL `
      --load `
      -t brunella-frontend `
      -f frontend/Dockerfile `
      ./frontend
  } else {
    docker build `
      --build-arg VITE_API_URL=$env:VITE_API_URL `
      -t brunella-frontend `
      -f frontend/Dockerfile `
      ./frontend
  }
}
catch {
  Write-Error "Build sikertelen: $($_.Exception.Message)"
  exit 1
}
