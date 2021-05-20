for ( $i = 0; $i -lt $args.count; $i++ ) {
    $path = $args[$i]
    Write-Host "Modifiying $path"
    $content = Get-Content $path -Raw
    $content.Replace("`r`n","`n") | Set-Content $path -Force
    Write-Host "Replacing line endings in $path"
}