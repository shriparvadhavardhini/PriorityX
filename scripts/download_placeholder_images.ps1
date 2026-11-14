$images = @(
"medical/paracetamol.png|Paracetamol",
"medical/cough_syrup.png|Cough Syrup",
"medical/dettol.png|Dettol",
"medical/hellokitty_bandaid.png|Hello Kitty Bandaid",
"medical/generic_bandaid.png|Generic Bandaid",
"medical/spiderman_bandaid.png|Spiderman Bandaid",
"medical/vicks_inhaler.png|Vicks Inhaler",
"medical/vicks_vaporub.png|Vicks VapoRub",
"medical/volini_gel.png|Volini Gel",
"medical/volini_spray.png|Volini Spray",

"essentials/sanitizer.png|Hand Sanitizer",
"essentials/tissue.png|Tissue Box",
"essentials/detergent.png|Laundry Detergent",
"essentials/trashbags.png|Trash Bags",

"food/pizza.png|Margherita Pizza",
"food/coldbrew.png|Cold Brew Coffee",
"food/honey.png|Organic Honey",
"food/cake.png|Chocolate Cake",

"dresses/floral.png|Floral Summer Dress",
"dresses/denim.png|Denim Jacket",
"dresses/gown.png|Evening Gown",

"jewelry/necklace.png|Gold Plated Necklace",
"jewelry/earrings.png|Diamond Stud Earrings",

"watches/chrono.png|PriorityX Chrono Steel",
"watches/leather.png|Minimalist Leather Watch",

"skincare/vitc.png|Vitamin C Serum",
"skincare/facewash.png|Hydrating Face Wash",
"skincare/sunscreen.png|SPF 50 Sunscreen",

"electronics/earbuds.png|Wireless Earbuds",
"electronics/fitband.png|Smart Fitness Band",
"electronics/powerbank.png|Portable Power Bank",

"toys/blocks.png|Building Blocks Set",
"toys/rccar.png|RC Racing Car",

"print/photoframe.png|Custom Photo Frame",
"print/tshirt.png|Custom T-Shirt Print"
)

$root = Join-Path -Path $PSScriptRoot -ChildPath "..\static\images"
foreach ($entry in $images) {
    $parts = $entry -split '\|'
    $rel = $parts[0]
    $label = $parts[1]
    $out = Join-Path -Path $root -ChildPath $rel
    $dir = Split-Path $out -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $text = ($label -replace ' ', '+')
    $url = "https://via.placeholder.com/600x400.png?text=$text"
    try {
        Invoke-WebRequest -Uri $url -UseBasicParsing -OutFile $out -ErrorAction Stop
        Write-Host "Downloaded $rel"
    } catch {
        Write-Warning "Failed to download $rel : $_"
    }
}
Write-Host "Done downloading placeholder images."
